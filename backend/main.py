from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.db.database import init_db
from app.api.part1_router import router as part1_router
from app.api.part2_router import router as part2_router
from app.api.part3_router import router as part3_router
from app.api.part4_router import router as part4_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager สำหรับ FastAPI
    ทำงานก่อนที่แอปจะเริ่มรัน (Startup) และหลังแอปปิดตัวลง (Shutdown)
    """
    print("[Startup] Initializing database...")
    init_db()
    print("[Startup] System ready!")
    yield
    print("[Shutdown] Closing connections...")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Text-to-SQL AI Agent Backend with 4 Modular Parts & 8 Sub-systems",
    lifespan=lifespan
)

# ตั้งค่า CORS Middleware อนุญาตให้ Frontend ยิง API ได้
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ลงทะเบียน API Routers แยกตาม 4 ส่วนงาน
app.include_router(part1_router)
app.include_router(part2_router)
app.include_router(part3_router)
app.include_router(part4_router)

@app.get("/")
def root():
    return {
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "online",
        "modules": [
            "Part 1: Data & Security System",
            "Part 2: AI Core System",
            "Part 3: Analytics & Insights System",
            "Part 4: Frontend & Dashboard System"
        ]
    }
