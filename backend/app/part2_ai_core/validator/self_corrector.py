from app.services.llm_service import get_llm
from langchain_core.messages import HumanMessage, SystemMessage
from app.part2_ai_core.translator.nl_translator import clean_extracted_sql
# [NEW] Import Security Validator มาใช้ตรวจซ้ำ
from app.part2_ai_core.validator.security_validator import validate_sql_security

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

โปรดแก้ไขและส่งคืนเฉพาะคำสั่ง SQL ที่ถูกต้องเพียวๆ เท่านั้น ห้ามใช้คำสั่งอันตราย:
"""
    response = llm.invoke([system_msg, HumanMessage(content=prompt)]).content.strip()
    repaired_sql = clean_extracted_sql(response)
    
    # [NEW] ตรวจสอบ Security ซ้ำหลังจากที่ AI แก้ไขโค้ดเสร็จแล้ว
    sec_check = validate_sql_security(repaired_sql)
    if not sec_check["is_valid"]:
        # ถ้า AI พยายามแอบเขียนคำสั่งอันตรายตอนแก้บั๊ก ให้ Raise Error ทิ้งไปเลย
        raise ValueError(f"Security Check Failed on Repaired SQL: {sec_check['reason']}")
        
    return repaired_sql