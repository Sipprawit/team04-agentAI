import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from dotenv import load_dotenv

# 1. โหลด Environment Variables ทันทีที่ไฟล์นี้ถูกเรียก (สำคัญสำหรับดึง Gemini API Key)
load_dotenv()

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
    
    # 2. ตรวจสอบความพร้อมของระบบ AI
    if not os.getenv("GROQ_API_KEY"):
        print("[WARNING] GROQ_API_KEY not found in .env! AI system may not work properly.")
    else:
        print("[Startup] AI Core (Groq) is ready to connect.")
        
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

# 3. Global Exception Handler (ดักจับ Error ไม่ให้เซิร์ฟเวอร์ร่วงและพ่น JSON สวยๆ กลับไปให้หน้าบ้าน)
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print(f"[Global Error] {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"status": "error", "message": "Internal Server Error", "details": str(exc)},
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