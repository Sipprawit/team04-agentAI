from app.part1_data_security.integration.schema_inspector import get_database_schema_info

def build_sql_prompt(user_query: str, chat_history: list = None) -> str:
    """
    สร้าง Prompt สำหรับแปลงภาษาธรรมชาติเป็น SQL
    รวมทั้งคำถาม, โครงสร้างตาราง (Schema) และประวัติการสนทนา
    """
    schema = get_database_schema_info()
    
    history_str = ""
    if chat_history:
        history_str = "\nประวัติการแชทก่อนหน้า:\n" + "\n".join([f"- {msg['role']}: {msg['text']}" for msg in chat_history[-3:]])

    prompt = f"""
คุณคือผู้เชี่ยวชาญด้าน SQLite Database
นี่คือโครงสร้างตารางในฐานข้อมูลปัจจุบัน:
{schema}
{history_str}

คำถามจากผู้ใช้: "{user_query}"

ข้อบังคับอย่างเคร่งครัด:
1. คืนค่าเฉพาะคำสั่ง SQL เพียวๆ เท่านั้น ห้ามมีคำอธิบาย ห้ามมี markdown ครอบ
2. หากต้องแสดงข้อมูลสินค้า หรือ ลูกค้า ให้ใช้ JOIN เพื่อดึง name มาแสดงเสมอ ห้ามใช้แค่ id
3. ใช้เฉพาะชื่อตารางและคอลัมน์ที่ระบุใน Schema เท่านั้น
4. คำสั่ง SQL ต้องขึ้นต้นด้วย SELECT หรือ WITH เท่านั้น
"""
    return prompt
