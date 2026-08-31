from app.part1_data_security.integration.schema_inspector import get_database_schema_info


def build_sql_prompt(user_query: str, chat_history: list = None) -> str:
    """
    สร้าง Prompt สำหรับแปลงภาษาธรรมชาติเป็น SQL
    รวมทั้งคำถาม, โครงสร้างตาราง (Schema) และประวัติการสนทนา
    """
    schema = get_database_schema_info()

    history_lines = []
    if chat_history:
        for msg in chat_history[-5:]:
            if isinstance(msg, dict):
                role = msg.get("role", "user")
                text_content = msg.get("text") or msg.get("content") or ""
                if text_content:
                    history_lines.append(f"- {role}: {text_content}")
            elif hasattr(msg, "content"):
                role = getattr(msg, "role", "user")
                history_lines.append(f"- {role}: {msg.content}")

    history_str = ""
    if history_lines:
        history_str = "\nประวัติการสนทนาก่อนหน้า:\n" + "\n".join(history_lines)

    prompt = f"""คุณคือผู้เชี่ยวชาญด้าน SQLite Database ขั้นสูง
นี่คือโครงสร้างตารางและความสัมพันธ์ในฐานข้อมูลปัจจุบัน:
{schema}
{history_str}

คำถามจากผู้ใช้: "{user_query}"

ข้อบังคับอย่างเคร่งครัด:
1. คืนค่าเฉพาะคำสั่ง SQL เพียวๆ เท่านั้น ห้ามมีคำอธิบาย ห้ามมีข้อความนำหน้า ห้ามใส่ markdown block ครอบ
2. หากต้องแสดงข้อมูลที่เกี่ยวข้อง เช่น ชื่อสินค้า หรือ ชื่อลูกค้า ให้ใช้ JOIN เพื่อดึง name มาแสดงเสมอ ไม่แสดงเฉพาะ foreign key id
3. ใช้เฉพาะชื่อตารางและชื่อคอลัมน์ที่ระบุใน Schema เท่านั้น
4. คำสั่ง SQL ต้องขึ้นต้นด้วย SELECT หรือ WITH เท่านั้น
5. ไม่ใช้คำสั่ง DDL หรือ DML เช่น DROP, DELETE, INSERT, UPDATE เด็ดขาด
"""
    return prompt
