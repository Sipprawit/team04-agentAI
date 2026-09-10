import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# ตั้งค่า Database URL สำหรับ SQLite
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
db_path = os.getenv("SQLITE_DB_PATH")
if not db_path:
    db_path = os.path.join(BASE_DIR, "test.db")
else:
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
SQLALCHEMY_DATABASE_URL = f"sqlite:///{db_path}"

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

def init_db(reset: bool = True):
    """
    สร้างตารางและ Seed ข้อมูลจำลองตอน Startup
    เมื่อ reset=True: จะล้างตารางทั้งหมดในฐานข้อมูล (รวมถึงตาราง CSV ชั่วคราว)
    และสร้างข้อมูล Mock Data ชุดสะอาดใหม่เสมอ
    """
    from app.models.mock_data import init_mock_db
    init_mock_db(reset=reset)
