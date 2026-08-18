import re
from sqlalchemy import text
from app.db.database import engine
from app.services.llm_service import get_llm
from langchain_core.messages import HumanMessage, SystemMessage

def extract_sql_query(text_input: str) -> str:
    """สกัดคำสั่ง SQL (SELECT หรือ WITH) ออกจากข้อความของ LLM โดยตรง"""
    if not text_input:
        return ""
    
    # 1. ถ้ามีแท็กปิด </think> ให้เอาเฉพาะข้อความหลัง </think>
    if "</think>" in text_input:
        text_input = text_input.split("</think>")[-1]
    
    # ลบ code fences และ backticks
    cleaned = text_input.replace("```sql", "").replace("```", "").replace("`", "").strip()
    
    # คำขยะภาษาอังกฤษที่แสดงถึงข้อความประเมิน/คิดของ AI
    junk_keywords = ['previous error', 'syntax error', 'user pasted', 'deconstruct', 'no dml/ddl', 'or with', 'failed attempt']
    
    # 2. ค้นหาคำสั่ง SQL ที่ขึ้นต้นด้วย WITH <name> AS (...) SELECT ...
    with_matches = re.finditer(r'\b(WITH\s+[a-zA-Z0-9_]+\s+AS\s*\([\s\S]+?\bSELECT\b[\s\S]+?)(?:;|\Z)', cleaned, re.IGNORECASE)
    for m in with_matches:
        sql = m.group(1).strip()
        if not any(j in sql.lower() for j in junk_keywords):
            clean_lines = []
            for line in sql.split('\n'):
                l = line.strip()
                if any(l.startswith(w) for w in ['This ', 'Note:', 'Here ', 'Output:', 'Constraint', 'The ', 'Previous ']):
                    break
                clean_lines.append(line)
            sql = '\n'.join(clean_lines).strip()
            if not sql.endswith(';'):
                sql += ';'
            return sql
        
    # 3. ค้นหาคำสั่ง SELECT ... FROM ...
    select_matches = re.finditer(r'\b(SELECT\s+[\s\S]+?\bFROM\b[\s\S]+?)(?:;|\Z)', cleaned, re.IGNORECASE)
    for m in select_matches:
        sql = m.group(1).strip()
        if not any(j in sql.lower() for j in junk_keywords):
            clean_lines = []
            for line in sql.split('\n'):
                l = line.strip()
                if any(l.startswith(w) for w in ['This ', 'Note:', 'Here ', 'Output:', 'Constraint', 'The ', 'Previous ']):
                    break
                clean_lines.append(line)
            sql = '\n'.join(clean_lines).strip()
            if not sql.endswith(';'):
                sql += ';'
            return sql
            
    return cleaned.strip()

def clean_summary_response(text_input: str) -> str:
    """ทำความสะอาดข้อความสรุปผลลัพธ์: ลบแท็ก <think> และดึงเฉพาะรายงานผลลัพธ์ภาษาไทย (ตัด Self-Check ทิ้ง)"""
    if not text_input:
        return ""
    
    # 1. ถ้ามีแท็กปิด </think> ให้เอาเฉพาะข้อความหลัง </think>
    if "</think>" in text_input:
        text_input = text_input.split("</think>")[-1]
        
    lines = text_input.split('\n')
    clean_lines = []
    is_thinking = True
    
    for line in lines:
        l = line.strip()
        l_lower = l.lower()
        
        # คำภาษาอังกฤษที่เป็นการคิด/ประเมินตนเองของ AI
        is_english_meta = any(k in l_lower for k in [
            'check constraint', 'check against', 'check:', 'draft:', 'analyze', 
            'process', 'task:', 'role:', 'structure:', 'let\'s', 'wait,', 
            'one minor', 'all constraints', 'matches', 'self-correction', 
            'refinement', 'proceeds', 'final check', 'no greetings', 
            'only important', 'tone:', 'percentage', 'no code', 'language:'
        ])
        
        # ค้นหาจุดเริ่มต้นของรายงานสรุปจริงภาษาไทย
        if is_thinking:
            if any(l.startswith(prefix) for prefix in ['**ยอดขาย', '**สินค้า', '- ยอดขาย', '- สินค้า', 'ยอดขาย', 'สินค้า', 'สัดส่วน', 'จากข้อมูล', 'รายงาน', '**']):
                if not is_english_meta:
                    is_thinking = False
        
        # เมื่อเริ่มเก็บรายงานแล้ว ถ้าเจอคำภาษาอังกฤษที่เป็น Self-Check ให้หยุดเก็บทันที
        if not is_thinking:
            if is_english_meta:
                break
            clean_lines.append(line)

    cleaned = '\n'.join(clean_lines)
    cleaned = re.sub(r'```(?:markdown)?', '', cleaned, flags=re.IGNORECASE)
    cleaned = cleaned.replace('```', '').replace('`', '')
    return cleaned.strip()

def get_db_schema():
    """ส่งคืนโครงสร้างตาราง (Schema) ที่ใช้อ้างอิง"""
    return """
    Table: customers
    Columns: id (INTEGER), name (VARCHAR), email (VARCHAR)
    
    Table: products
    Columns: id (INTEGER), name (VARCHAR), price (FLOAT)
    
    Table: orders
    Columns: id (INTEGER), customer_id (INTEGER), product_id (INTEGER), quantity (INTEGER), date (DATE)
    """

def ask_agent(query: str) -> str:
    """
    ฟังก์ชันสำหรับให้ AI สร้าง SQL -> รันใน Database -> นำผลลัพธ์มาสรุปเป็นภาษาไทย
    พร้อมระบบ Self-Correction และจัดการข้อผิดพลาดเบื้องต้น
    """
    llm = get_llm()
    schema = get_db_schema()
    
    print("\n[Step 1] สร้างคำสั่ง SQL...")
    
    # 1. Prompt ให้ AI เขียน SQL
    base_sql_prompt = f"""
คุณคือผู้เชี่ยวชาญด้าน SQLite Database
นี่คือโครงสร้างตารางในระบบ E-commerce:
{schema}

จงสร้างคำสั่ง SQL เพื่อตอบคำถาม: "{query}"

ข้อบังคับอย่างเคร่งครัด:
1. คืนค่าเฉพาะคำสั่ง SQL เพียวๆ เท่านั้น ห้ามมีคำอธิบาย ห้ามมี markdown ครอบ
2. หากต้องแสดงข้อมูลสินค้า หรือ ลูกค้า ให้ใช้ JOIN เพื่อดึง name มาแสดงเสมอ ห้ามใช้แค่ id
3. หากเจอชื่อตารางหรือคอลัมน์ที่ไม่ตรงกับ Schema ที่ให้ไป ห้ามเดาชื่อเอง ให้ใช้เฉพาะชื่อที่ระบุใน Schema เท่านั้น
4. ห้ามใช้ LIMIT ใน SQL เว้นแต่ผู้ใช้จะระบุจำนวนที่ต้องการเจาะจงเอง ให้ดึงข้อมูลที่เกี่ยวข้องทั้งหมดออกมา เพื่อให้ AI นำมาวิเคราะห์และประมวลผลต่อในสเตปถัดไปแทน
5. เมื่อผู้ใช้ถามหาสินค้าที่มียอดขายมากที่สุดหรือน้อยที่สุด ห้ามดึงมาแค่ตัวเลข Aggregate ลอยๆ ให้ดึงข้อมูลทั้งหมดมาเรียงลำดับ หรือใช้ Subquery/Window Function ดึงรายการอันดับ 1 ออกมาทั้งหมด (ห้ามใช้ LIMIT 1 เด็ดขาด)
6. คำสั่ง SQL ต้องขึ้นต้นด้วย SELECT หรือ WITH เท่านั้น ห้ามใช้คำสั่งดัดแปลงข้อมูลอื่น
    """
    
    sql_system_message = SystemMessage(content=(
        "You are an expert SQLite Database Engineer. "
        "Your task is to generate valid SQLite SQL queries only. "
        "DO NOT output reasoning, thinking process, <think> tags, or markdown explanations. "
        "Output ONLY the raw SQL query directly."
    ))
    
    max_retries = 1
    sql_response = ""
    rows = []
    last_error = ""
    
    for attempt in range(max_retries + 1):
        try:
            # เพิ่ม Error message เข้าไปใน Prompt หากเป็นการลองใหม่
            if attempt == 0:
                prompt_to_send = base_sql_prompt
            else:
                prompt_to_send = base_sql_prompt + f"\n\nคำสั่ง SQL ก่อนหน้านี้ ({sql_response}) รันไม่ได้เนื่องจาก:\n{last_error}\nโปรดเขียน SQL ใหม่ให้ถูกต้อง"
                
            raw_response = llm.invoke([sql_system_message, HumanMessage(content=prompt_to_send)]).content.strip()
            
            # ทำความสะอาด: สกัดเอาเฉพาะคำสั่ง SQL (SELECT / WITH)
            sql_response = extract_sql_query(raw_response)
            print(f"- SQL (Attempt {attempt+1}): {sql_response}")
            
            # 2. รันคำสั่ง SQL จริงในฐานข้อมูล
            with engine.connect() as conn:
                result = conn.execute(text(sql_response))
                if result.returns_rows:
                    rows = result.fetchall()
                else:
                    rows = []
            
            # ถ้ารันผ่าน ให้ออกจาก Loop
            break
            
        except Exception as e:
            last_error = str(e)
            print(f"- [Warning] SQL Error: {last_error}")
            if attempt == max_retries:
                return f"เกิดข้อผิดพลาดในการดึงข้อมูล: {last_error}"

    if not rows:
        return "ไม่พบข้อมูลที่ต้องการในฐานข้อมูล"
        
    data_str = str(rows)
    print(f"- ดึงข้อมูลสำเร็จ: พบ {len(rows)} รายการ")
    print("[Step 2] สรุปผลลัพธ์เป็นภาษาไทย...")
        
    # 3. Prompt ให้ AI นำข้อมูลดิบมาสรุป
    summary_prompt = f"""
คุณคือ Data Analyst Assistant สร้าง Data Report สรุปข้อมูล E-commerce
คำถามจากผู้ใช้: "{query}"
ข้อมูลที่ดึงจากฐานข้อมูล: {data_str}

จงตอบผู้ใช้โดยยึดโครงสร้างและข้อบังคับนี้อย่างเคร่งครัด:

โครงสร้างการตอบ (ต้องเรียงตามนี้):
1. Headline (สรุปผลหลัก): เขียนแค่ 1 บรรทัด เน้นตัวหนา (Markdown) ในส่วนสำคัญ เช่น "สินค้าที่ขายดีที่สุดคือ **Wireless Earbuds** (9 ชิ้น/34.6%)"
2. Details (รายละเอียด): ใช้ Bullet points เท่านั้น ห้ามเขียนเป็นพารากราฟ (หากมีหลายรายการ ให้เน้น Top 3 และจับกลุ่มรายการที่เหลือรวมกัน)
3. Insight (ข้อสังเกต): สถิติที่น่าสนใจเพียง 1 บรรทัดสั้นๆ (เช่น สัดส่วนเมื่อเทียบกับกลุ่มอื่น หรือความต่างที่ชัดเจน)

ข้อบังคับอย่างเคร่งครัด (ห้ามละเมิด):
1. ห้ามเกริ่นนำหรือปิดท้ายเด็ดขาด! (ห้ามพิมพ์คำว่า "จากการวิเคราะห์ข้อมูล...", "โดยสรุปคือ...", "เราพบว่า...", "หากต้องการให้เจาะลึก...") ให้เข้าเรื่องที่ Headline ทันที
2. ใส่ตัวเลขเฉพาะที่สำคัญที่สุดเท่านั้น ห้ามอธิบายตัวเลขเยอะจนลายตา
3. โทนภาษา: สั้น กระชับ เป็นทางการเหมือนรายงานสรุปยอดขาย (Sales Report) จากผู้เชี่ยวชาญ
4. การคำนวณ: ถ้ามีข้อมูลพอ ให้แนบเปอร์เซ็นต์ส่วนแบ่ง (Market Share) ในวงเล็บเสมอ
5. ห้ามใส่บล็อกโค้ด (```) ครอบคำตอบเด็ดขาด
    """
    
    summary_system_message = SystemMessage(content=(
        "You are a professional Data Analyst Assistant. "
        "Your task is to write a clean Thai Data Report based on the provided database results. "
        "DO NOT output reasoning, thinking process, <think> tags, or self-evaluation check-lists. "
        "Output ONLY the final Thai report directly."
    ))

    try:
        raw_answer = llm.invoke([summary_system_message, HumanMessage(content=summary_prompt)]).content.strip()
        # ทำความสะอาด: ลบ <think> block และ Markdown
        final_answer = clean_summary_response(raw_answer)
        return final_answer
        
    except Exception as e:
        return f"เกิดข้อผิดพลาดในการสรุปข้อมูล: {str(e)}"


# โค้ดสำหรับทดสอบ
if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    
    test_question = "สรุปยอดขายสินค้าแต่ละตัวให้หน่อย เรียงจากมากไปน้อย"
    print(f"คำถามทดสอบ: {test_question}")
    
    answer = ask_agent(test_question)
    
    print("-" * 50)
    print("คำตอบจาก AI:")
    print("-" * 50)
    print(answer)
