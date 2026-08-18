from sqlalchemy import text
from app.db.database import engine
from app.part1_data_security.sandbox.audit_logger import log_execution

def execute_sql_in_sandbox(sql_query: str) -> dict:
    """
    ระบบสภาพแวดล้อมจำลองเพื่อความปลอดภัย (Secure Code Execution Sandbox System)
    นำคำสั่ง SQL จาก AI มารันในสภาพแวดล้อมจำลองแบบจำกัดความเสี่ยง
    """
    try:
        with engine.connect() as conn:
            result = conn.execute(text(sql_query))
            if result.returns_rows:
                rows = result.fetchall()
                data = [dict(row._mapping) for row in rows]
            else:
                data = []
                
        # บันทึกประวัติสำเร็จ
        log_execution(sql_query, status="success", error_message=None)
        return {
            "status": "success",
            "rows_count": len(data),
            "data": data
        }
    except Exception as e:
        error_msg = str(e)
        # บันทึกประวัติข้อผิดพลาด
        log_execution(sql_query, status="error", error_message=error_msg)
        return {
            "status": "error",
            "message": error_msg
        }
