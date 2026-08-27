from sqlalchemy import text
from app.db.database import engine

_table_initialized = False


def init_audit_log_table():
    """สร้างตารางบันทึกประวัติหากยังไม่มี (เรียกครั้งเดียวตอน Startup)"""
    global _table_initialized
    if _table_initialized:
        return

    try:
        with engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS audit_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query TEXT,
                    status TEXT,
                    error_message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """))
            conn.commit()
        _table_initialized = True
    except Exception as e:
        print(f"[AuditLogger] Failed to create table: {e}")


def log_execution(query: str, status: str, error_message: str = None):
    """เก็บบันทึกประวัติการรันและข้อผิดพลาด (Audit & Error Logs)"""
    try:
        init_audit_log_table()
        with engine.connect() as conn:
            conn.execute(
                text("INSERT INTO audit_logs (query, status, error_message) VALUES (:query, :status, :error)"),
                {"query": query, "status": status, "error": error_message}
            )
            conn.commit()
    except Exception as e:
        print(f"[AuditLogger Error] {e}")


def get_audit_logs(limit: int = 50, status_filter: str = None) -> list:
    """
    ดึงประวัติ Audit Logs จากฐานข้อมูล
    - limit: จำนวนรายการสูงสุดที่ดึง (default 50)
    - status_filter: กรองตาม status เช่น 'success' หรือ 'error'
    """
    try:
        init_audit_log_table()
        with engine.connect() as conn:
            if status_filter:
                result = conn.execute(
                    text("SELECT id, query, status, error_message, created_at FROM audit_logs WHERE status = :status ORDER BY created_at DESC LIMIT :limit"),
                    {"status": status_filter, "limit": limit}
                )
            else:
                result = conn.execute(
                    text("SELECT id, query, status, error_message, created_at FROM audit_logs ORDER BY created_at DESC LIMIT :limit"),
                    {"limit": limit}
                )
            rows = result.fetchall()
            return [dict(row._mapping) for row in rows]
    except Exception as e:
        print(f"[AuditLogger Error] {e}")
        return []


def get_audit_stats() -> dict:
    """สรุปสถิติ Audit Logs (จำนวนทั้งหมด, สำเร็จ, ผิดพลาด)"""
    try:
        init_audit_log_table()
        with engine.connect() as conn:
            total = conn.execute(text("SELECT COUNT(*) FROM audit_logs")).scalar() or 0
            success = conn.execute(text("SELECT COUNT(*) FROM audit_logs WHERE status = 'success'")).scalar() or 0
            error = conn.execute(text("SELECT COUNT(*) FROM audit_logs WHERE status = 'error'")).scalar() or 0
            return {"total": total, "success": success, "error": error}
    except Exception as e:
        print(f"[AuditLogger Error] {e}")
        return {"total": 0, "success": 0, "error": 0}
