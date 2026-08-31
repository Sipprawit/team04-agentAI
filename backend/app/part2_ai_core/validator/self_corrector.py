import logging
from app.services.llm_service import get_llm
from langchain_core.messages import HumanMessage, SystemMessage
from app.part2_ai_core.translator.nl_translator import clean_extracted_sql

logger = logging.getLogger("SelfCorrector")


def self_heal_sql(failed_sql: str, error_message: str, schema_info: str) -> str:
    """
    ระบบตรวจสอบและแก้ไขโค้ดอัตโนมัติ (Agentic Self-Correction System)
    วิเคราะห์สาเหตุของ Error แล้วให้ AI ปรับปรุงแก้ไขคำสั่ง SQL ใหม่อัตโนมัติ (Self-healing)
    """
    try:
        llm = get_llm()
        system_msg = SystemMessage(
            content="You are an expert SQL Repair Specialist. Fix the broken SQLite query based on the database schema "
                    "and the error message. Output ONLY the corrected executable SQL query directly. "
                    "DO NOT include explanations, reasoning, or markdown blocks."
        )

        prompt = f"""โครงสร้างตารางในฐานข้อมูล:
{schema_info}

คำสั่ง SQL ที่รันไม่ผ่าน:
{failed_sql}

ข้อผิดพลาดที่เกิดขึ้น (Error):
{error_message}

โปรดแก้ไขและส่งคืนเฉพาะคำสั่ง SQL ที่ถูกต้องและปลอดภัย (SELECT/WITH เท่านั้น):
"""
        response = llm.invoke([system_msg, HumanMessage(content=prompt)]).content.strip()
        corrected_sql = clean_extracted_sql(response)
        return corrected_sql if corrected_sql else failed_sql
    except Exception as e:
        logger.error(f"Self-healing LLM error: {e}")
        return failed_sql
