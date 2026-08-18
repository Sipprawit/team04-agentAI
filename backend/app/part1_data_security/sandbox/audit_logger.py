import datetime
from sqlalchemy import text
from app.db.database import engine

def init_audit_log_table():
    """สร้างตารางบันทึกประวัติหากยังไม่มี"""
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
    except Exception:
        pass

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
