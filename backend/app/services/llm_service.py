# encoding: utf-8
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage

from app.core.config import settings


def get_llm() -> ChatGroq:
    """
    สร้างและคืนค่า instance ของ Groq LLM ผ่าน LangChain
    ตรวจสอบ API Key ก่อนสร้าง instance
    """
    settings.validate()

    llm = ChatGroq(
        model=settings.LLM_MODEL_NAME,
        api_key=settings.GROQ_API_KEY,
        temperature=0.2,       # ความสร้างสรรค์ (0 = แม่นยำ, 1 = สร้างสรรค์)
        max_tokens=2048,       # จำนวน token สูงสุดของคำตอบ
    )
    return llm


def test_llm_connection(prompt: str = "Hello! Please introduce yourself briefly in Thai language.") -> dict:
    """
    ทดสอบการเชื่อมต่อกับ Groq API

    Args:
        prompt (str): ข้อความที่จะส่งไปถามโมเดล

    Returns:
        dict: ผลลัพธ์การทดสอบ ประกอบด้วย status, model, prompt, response
    """
    try:
        llm = get_llm()

        # ส่ง prompt ไปยัง LLM ผ่าน Groq
        messages = [HumanMessage(content=prompt)]
        response = llm.invoke(messages)

        return {
            "status": "success",
            "provider": "Groq",
            "model": settings.LLM_MODEL_NAME,
            "prompt": prompt,
            "response": response.content,
        }

    except ValueError as e:
        # กรณี API Key ไม่ถูกตั้งค่า
        return {
            "status": "error",
            "error_type": "ConfigurationError",
            "message": str(e),
        }
    except Exception as e:
        # กรณีเกิดข้อผิดพลาดอื่น ๆ
        return {
            "status": "error",
            "error_type": type(e).__name__,
            "message": str(e),
        }


# ทดสอบตรงๆ เมื่อรันไฟล์นี้โดยตรง
if __name__ == "__main__":
    import json
    import sys

    # แก้ปัญหา encoding บน Windows
    sys.stdout.reconfigure(encoding="utf-8")

    print("Testing Groq API connection...")
    print(f"Model: {settings.LLM_MODEL_NAME}")
    print("-" * 50)

    result = test_llm_connection()
    print(json.dumps(result, ensure_ascii=False, indent=2))

    if result["status"] == "success":
        print("\n[SUCCESS] Connected! System is ready.")
    else:
        print(f"\n[ERROR] {result.get('message')}")
