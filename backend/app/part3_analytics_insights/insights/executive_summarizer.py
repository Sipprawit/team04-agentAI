import re
from app.services.llm_service import get_llm
from langchain_core.messages import HumanMessage, SystemMessage
from app.part3_analytics_insights.insights.stat_calculator import calculate_advanced_statistics

def clean_summary_response(text_input: str) -> str:
    """ทำความสะอาดข้อความสรุปผลลัพธ์: ลบแท็ก <think> และดึงเฉพาะรายงานผลลัพธ์ภาษาไทย (ตัด Self-Check ทิ้ง)"""
    if not text_input:
        return ""
    
    if "</think>" in text_input:
        text_input = text_input.split("</think>")[-1]
        
    lines = text_input.split('\n')
    clean_lines = []
    is_thinking = True
    
    for line in lines:
        l = line.strip()
        l_lower = l.lower()
        
        is_english_meta = any(k in l_lower for k in [
            'check constraint', 'check against', 'check:', 'draft:', 'analyze', 
            'process', 'task:', 'role:', 'structure:', 'let\'s', 'wait,', 
            'one minor', 'all constraints', 'matches', 'self-correction', 
            'refinement', 'proceeds', 'final check', 'no greetings', 
            'only important', 'tone:', 'percentage', 'no code', 'language:'
        ])
        
        if is_thinking:
            if any(l.startswith(prefix) for prefix in ['**ยอดขาย', '**สินค้า', '- ยอดขาย', '- สินค้า', 'ยอดขาย', 'สินค้า', 'สัดส่วน', 'จากข้อมูล', 'รายงาน', '**']):
                if not is_english_meta:
                    is_thinking = False
        
        if not is_thinking:
            if is_english_meta:
                break
            clean_lines.append(line)

    cleaned = '\n'.join(clean_lines)
    cleaned = re.sub(r'```(?:markdown)?', '', cleaned, flags=re.IGNORECASE)
    cleaned = cleaned.replace('```', '').replace('`', '')
    return cleaned.strip()

def generate_executive_insight(user_query: str, raw_data: list) -> str:
    """
    ระบบสร้างข้อความสรุปข้อมูลเชิงลึก (Automated Insight Generator System)
    เขียนบรรยายสรุปตัวเลขและสถิติสำคัญให้ผู้บริหารอ่านเข้าใจง่าย
    """
    if not raw_data:
        return "ไม่พบข้อมูลสำหรับวิเคราะห์"
        
    llm = get_llm()
    stats = calculate_advanced_statistics(raw_data)
    
    summary_prompt = f"""
คุณคือ Data Analyst Assistant สร้าง Data Report สรุปข้อมูล E-commerce
คำถามจากผู้ใช้: "{user_query}"
ข้อมูลที่ดึงจากฐานข้อมูล: {raw_data}
สถิติที่คำนวณเพิ่มเติม: {stats}

จงตอบผู้ใช้โดยยึดโครงสร้างและข้อบังคับนี้อย่างเคร่งครัด:

โครงสร้างการตอบ (ต้องเรียงตามนี้):
1. Headline (สรุปผลหลัก): เขียนแค่ 1 บรรทัด เน้นตัวหนา (Markdown) ในส่วนสำคัญ
2. Details (รายละเอียด): ใช้ Bullet points เท่านั้น ห้ามเขียนเป็นพารากราฟ
3. Insight (ข้อสังเกต): สถิติที่น่าสนใจเพียง 1 บรรทัดสั้นๆ

ข้อบังคับอย่างเคร่งครัด:
1. ห้ามเกริ่นนำหรือปิดท้ายเด็ดขาด! ให้เข้าเรื่องที่ Headline ทันที
2. ใส่ตัวเลขเฉพาะที่สำคัญที่สุดเท่านั้น
3. โทนภาษา: สั้น กระชับ เป็นทางการเหมือนรายงานสรุปยอดขาย (Sales Report)
"""
    
    system_msg = SystemMessage(content="You are a professional Data Analyst Assistant. Output ONLY the final Thai report directly without reasoning or check-lists.")
    
    raw_answer = llm.invoke([system_msg, HumanMessage(content=summary_prompt)]).content.strip()
    return clean_summary_response(raw_answer)
