import os
from sqlalchemy import create_engine, event
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

# ติดตั้ง SQLite PRAGMA (WAL mode + busy_timeout) เพื่อรองรับ Concurrent Requests ป้องกันฐานข้อมูลล็อค
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL;")
    cursor.execute("PRAGMA synchronous=NORMAL;")
    cursor.execute("PRAGMA busy_timeout=5000;")
    cursor.execute("PRAGMA foreign_keys=ON;")
    cursor.close()

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

def init_db(reset: bool = False):
    """
    สร้างตารางและ Seed ข้อมูลจำลองตอน Startup
    เมื่อ reset=True: จะล้างตารางทั้งหมดในฐานข้อมูล (รวมถึงตาราง CSV ชั่วคราว)
    เมื่อ reset=False (ค่าเริ่มต้นสำหรับ Production): รักษาตารางข้อมูลที่ผู้ใช้อัปโหลดไว้ และสร้างเฉพาะตารางเริ่มต้นที่ยังไม่มี
    """
    from app.models.mock_data import init_mock_db
    init_mock_db(reset=reset)
