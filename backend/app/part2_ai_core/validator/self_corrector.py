from app.services.llm_service import get_llm
from langchain_core.messages import HumanMessage, SystemMessage
from app.part2_ai_core.translator.nl_translator import clean_extracted_sql

def self_heal_sql(failed_sql: str, error_message: str, schema_info: str) -> str:
    """
    ระบบตรวจสอบและแก้ไขโค้ดอัตโนมัติ (Agentic Self-Correction System)
    วิเคราะห์สาเหตุของ Error แล้วให้ AI ปรับปรุงแก้ไขคำสั่ง SQL ใหม่อัตโนมัติ (Self-healing)
    """
    llm = get_llm()
    system_msg = SystemMessage(content="You are an expert SQL Repair Specialist. Fix the broken SQL query based on the error message. Output ONLY the corrected raw SQL query.")
    
    prompt = f"""
โครงสร้างตาราง:
{schema_info}

คำสั่ง SQL ที่รันไม่ผ่าน:
{failed_sql}

ข้อผิดพลาดที่เกิดขึ้น (Error):
{error_message}

โปรดแก้ไขและส่งคืนเฉพาะคำสั่ง SQL ที่ถูกต้องเพียวๆ เท่านั้น:
"""
    response = llm.invoke([system_msg, HumanMessage(content=prompt)]).content.strip()
    return clean_extracted_sql(response)
