import signal
import threading
from sqlalchemy import text, event
from app.db.database import engine
from app.part1_data_security.sandbox.audit_logger import log_execution

# ============================================
# ข้อจำกัดด้านความปลอดภัย
# ============================================
MAX_ROWS = 500          # จำนวนแถวผลลัพธ์สูงสุดที่อนุญาต
QUERY_TIMEOUT_SEC = 10  # จำกัดเวลาการรัน Query (วินาที)


class QueryTimeoutError(Exception):
    """Exception เมื่อ Query ใช้เวลาเกินกำหนด"""
    pass


def _sqlite_timeout_handler(conn, timeout_sec: int):
    """
    ตั้ง progress_handler สำหรับ SQLite เพื่อตรวจสอบ Timeout
    SQLite จะเรียก progress_handler ทุก N instructions
    ถ้า handler คืนค่า non-zero จะยกเลิก Query ทันที
    Returns: (timer, timeout_flag) — timeout_flag[0] = True เมื่อหมดเวลา
    """
    deadline = threading.Event()
    timeout_flag = [False]  # ใช้ list เพื่อให้ mutable จาก closure

    def on_timeout():
        timeout_flag[0] = True
        deadline.set()

    # ตั้งเวลาให้ deadline fire หลังจาก timeout_sec
    timer = threading.Timer(timeout_sec, on_timeout)
    timer.daemon = True
    timer.start()

    raw_conn = conn.connection.dbapi_connection
    # เรียกทุก 1000 SQLite VM instructions
    raw_conn.set_progress_handler(lambda: 1 if deadline.is_set() else 0, 1000)

    return timer, timeout_flag


def _clear_timeout_handler(conn, timer):
    """ล้าง progress_handler หลังรัน Query เสร็จ"""
    timer.cancel()
    raw_conn = conn.connection.dbapi_connection
    raw_conn.set_progress_handler(None, 0)


def execute_sql_in_sandbox(sql_query: str, max_rows: int = MAX_ROWS, timeout_sec: int = QUERY_TIMEOUT_SEC) -> dict:
    """
    ระบบสภาพแวดล้อมจำลองเพื่อความปลอดภัย (Secure Code Execution Sandbox System)
    - นำคำสั่ง SQL จาก AI มารันในสภาพแวดล้อมจำลองแบบจำกัดความเสี่ยง
    - จำกัดจำนวนแถวผลลัพธ์สูงสุด (Row Limit)
    - จำกัดเวลาการรัน Query (Timeout)
    - บันทึก Audit Log ทุกครั้ง
    """
    timer = None
    timeout_flag_ref = [False]
    try:
        with engine.connect() as conn:
            try:
                # --- บังคับ Read-Only ที่ระดับ SQLite Engine (Defense-in-Depth) ---
                conn.execute(text("PRAGMA query_only = ON;"))

                # --- ตั้ง Timeout Handler ---
                timer, timeout_flag_ref = _sqlite_timeout_handler(conn, timeout_sec)

                result = conn.execute(text(sql_query))

                if result.returns_rows:
                    # --- จำกัดจำนวนแถว (Row Limit) ---
                    rows = result.fetchmany(max_rows + 1)
                    is_truncated = len(rows) > max_rows
                    if is_truncated:
                        rows = rows[:max_rows]
                    data = [dict(row._mapping) for row in rows]
                else:
                    data = []
                    is_truncated = False

                # --- ล้าง Timeout Handler ---
                _clear_timeout_handler(conn, timer)
                timer = None

            finally:
                # --- รีเซ็ต Read-Only เสมอ เพื่อคืน connection กลับ pool ในสถานะปกติ ---
                try:
                    conn.execute(text("PRAGMA query_only = OFF;"))
                except Exception:
                    pass  # ถ้ารีเซ็ตไม่ได้ ไม่ให้ crash ซ้อน

        # บันทึกประวัติสำเร็จ
        log_execution(sql_query, status="success", error_message=None)
        result_dict = {
            "status": "success",
            "rows_count": len(data),
            "data": data,
        }
        if is_truncated:
            result_dict["warning"] = f"Results truncated to {max_rows} rows (original result exceeded limit)"
        return result_dict

    except Exception as e:
        error_msg = str(e)

        # ตรวจจับว่าเป็น Timeout ด้วย flag (ไม่ใช้ string matching)
        if timeout_flag_ref[0]:
            error_msg = f"Query timeout: exceeded {timeout_sec} seconds limit"

        # บันทึกประวัติข้อผิดพลาด
        log_execution(sql_query, status="error", error_message=error_msg)
        return {
            "status": "error",
            "message": error_msg
        }
    finally:
        # ทำให้แน่ใจว่า timer ถูกยกเลิกเสมอ
        if timer is not None:
            timer.cancel()
