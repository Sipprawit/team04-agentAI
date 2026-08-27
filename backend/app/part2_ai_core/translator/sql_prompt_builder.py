from app.part1_data_security.integration.schema_inspector import get_database_schema_info

def build_sql_prompt(user_query: str, chat_history: list = None) -> str:
    """
    สร้าง Prompt สำหรับแปลงภาษาธรรมชาติเป็น SQL พร้อมตัวอย่าง (Few-shot examples)
    """
    schema = get_database_schema_info()
    
    history_str = ""
    if chat_history and len(chat_history) > 0:
        history_str = "\nประวัติการสนทนาก่อนหน้า:\n" 
        for msg in chat_history[-3:]: 
            role = "ผู้ใช้" if msg.get('role') == 'user' else "AI"
            history_str += f"- {role}: {msg.get('text', '')}\n"

    # [NEW] เพิ่ม Few-shot examples เพื่อสอน AI ให้เขียน Query ตรงสเปก
    few_shot_examples = """
ตัวอย่างการแปลงคำถามเป็น SQL:
คำถาม: "ขอดูยอดขายรวมของพนักงานแต่ละคน"
SQL: SELECT e.name, SUM(s.amount) as total_sales FROM sales s JOIN employees e ON s.employee_id = e.id GROUP BY e.name;

คำถาม: "สินค้าไหนขายดีที่สุด 5 อันดับแรก"
SQL: SELECT p.product_name, SUM(o.quantity) as total_sold FROM order_items o JOIN products p ON o.product_id = p.id GROUP BY p.product_name ORDER BY total_sold DESC LIMIT 5;
"""

    prompt = f"""
คุณคือผู้เชี่ยวชาญด้าน SQLite Database
นี่คือโครงสร้างตารางในฐานข้อมูลปัจจุบัน:
{schema}
{history_str}
{few_shot_examples}

คำถามปัจจุบันจากผู้ใช้: "{user_query}"

ข้อบังคับอย่างเคร่งครัด:
1. คืนค่าเฉพาะคำสั่ง SQL เพียวๆ เท่านั้น ห้ามมีคำอธิบาย ห้ามมี markdown ครอบ
2. หากต้องแสดงข้อมูลที่มีการเชื่อมโยง ให้ใช้ JOIN ดึงชื่อมาแสดงด้วยเสมอ ห้ามแสดงแค่ id
3. ใช้เฉพาะชื่อตารางและคอลัมน์ที่มีอยู่จริงใน Schema เท่านั้น
4. คำสั่ง SQL ต้องขึ้นต้นด้วย SELECT หรือ WITH เท่านั้น ห้ามใช้ PRAGMA หรือคำสั่งเปลี่ยนแปลงข้อมูล
"""
    return prompt