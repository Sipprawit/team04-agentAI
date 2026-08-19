import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# ตั้งค่า Database URL สำหรับ SQLite
# บันทึกไฟล์ test.db ไว้ที่ root ของ backend/
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SQLALCHEMY_DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'test.db')}"

# สร้าง Engine (check_same_thread=False จำเป็นสำหรับ SQLite ใน FastAPI)
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# สร้าง SessionLocal class สำหรับคุยกับ Database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class สำหรับสร้าง Models
Base = declarative_base()

# Dependency สำหรับใช้ใน FastAPI (app/api/...)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """สร้างตารางและ Seed ข้อมูลจำลองตอน Startup (ถ้ายังไม่มี)"""
    from app.models.mock_data import init_mock_db
    init_mock_db()
