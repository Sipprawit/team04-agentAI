from fastapi import FastAPI

# สร้างตัวแอปพลิเคชันหลัก
app = FastAPI(
    title="Team04 AI Agent API",
    description="Backend API for Data Analytics and AI Agent",
    version="1.0.0"
)

# สร้าง Endpoint หน้าแรกเพื่อทดสอบระบบ
@app.get("/")
def read_root():
    return {
        "team": "Team 04",
        "message": "Welcome to AI Agent Backend API",
        "status": "Online and Ready to Code!"
    }