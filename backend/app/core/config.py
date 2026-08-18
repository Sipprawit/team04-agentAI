import os
from dotenv import load_dotenv

# โหลดค่าจากไฟล์ .env (ถ้ามี)
load_dotenv()


class Settings:
    """การตั้งค่าหลักของระบบ โหลดจาก Environment Variables"""

    # Groq API Key
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")

    # ชื่อโมเดลที่ใช้งาน (สามารถเปลี่ยนได้ใน .env)
    # ตัวเลือกแนะนำจาก Groq: openai/gpt-oss-20b, openai/gpt-oss-120b, qwen/qwen3.6-27b
    LLM_MODEL_NAME: str = os.getenv("LLM_MODEL_NAME", "openai/gpt-oss-20b")

    # ชื่อแอปพลิเคชัน
    APP_NAME: str = "Text-to-SQL AI Agent"
    APP_VERSION: str = "1.0.0"

    def validate(self):
        """ตรวจสอบว่า API Key ถูกตั้งค่าแล้ว"""
        if not self.GROQ_API_KEY:
            raise ValueError(
                "ไม่พบ GROQ_API_KEY!\n"
                "กรุณาตั้งค่าในไฟล์ .env หรือ Environment Variables\n"
                "ตัวอย่าง: GROQ_API_KEY=gsk_xxxxxxxxxxxx"
            )
        return True


# สร้าง instance เดียวสำหรับใช้งานทั้งโปรเจค (Singleton pattern)
settings = Settings()
