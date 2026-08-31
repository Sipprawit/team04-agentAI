import re
import logging
from app.services.llm_service import get_llm
from langchain_core.messages import HumanMessage, SystemMessage
from app.part3_analytics_insights.insights.stat_calculator import calculate_advanced_statistics

logger = logging.getLogger("ExecutiveSummarizer")


def clean_summary_response(text_input: str) -> str:
    """ทำความสะอาดข้อความสรุปผลลัพธ์: ลบแท็ก <think> และดึงเฉพาะรายงานผลลัพธ์ภาษาไทย"""
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
            if any(l.startswith(prefix) for prefix in [
                '**ยอดขาย', '**สินค้า', '- ยอดขาย', '- สินค้า', 'ยอดขาย', 'สินค้า',
                'สัดส่วน', 'จากข้อมูล', 'รายงาน', '**', '#'
            ]):
                if not is_english_meta:
                    is_thinking = False

        if not is_thinking:
            if is_english_meta:
                break
            clean_lines.append(line)

    cleaned = '\n'.join(clean_lines)
    cleaned = re.sub(r'```(?:markdown)?', '', cleaned, flags=re.IGNORECASE)
    cleaned = cleaned.replace('```', '')
    return cleaned.strip() if cleaned.strip() else text_input.strip()


def _fallback_summary(user_query: str, raw_data: list, stats: dict) -> str:
    """สร้างข้อความสรุปแบบ Rule-based กรณีที่ LLM ไม่ตอบสนอง"""
    count = len(raw_data)
    first_row = raw_data[0]
    keys = list(first_row.keys())

    lines = [f"**ผลการค้นหาข้อมูล ({count} รายการ)**"]
    for row in raw_data[:5]:
        val_str = ", ".join([f"{k}: {v}" for k, v in row.items()])
        lines.append(f"- {val_str}")
    if count > 5:
        lines.append(f"- และอีก {count - 5} รายการ...")

    if "total" in stats:
        lines.append(f"\n📊 **สถิติรวม**: ยอดรวม = {stats.get('total'):,}, ค่าเฉลี่ย = {stats.get('average'):,}")
    return "\n".join(lines)


def generate_executive_insight(user_query: str, raw_data: list) -> str:
    """
    ระบบสร้างข้อความสรุปข้อมูลเชิงลึก (Automated Insight Generator System)
    เขียนบรรยายสรุปตัวเลขและสถิติสำคัญให้ผู้บริหารอ่านเข้าใจง่าย
    พร้อม Fallback กรณี LLM Error
    """
    if not raw_data:
        return "ไม่พบข้อมูลที่ตรงกับเงื่อนไขในฐานข้อมูล"

    stats = calculate_advanced_statistics(raw_data)

    try:
        llm = get_llm()
        sample_data = raw_data[:15]  # จำกัด 15 รายการเพื่อประหยัด Token

        summary_prompt = f"""คุณคือ Data Analyst Assistant สร้าง Data Report สรุปข้อมูล E-commerce
คำถามจากผู้ใช้: "{user_query}"
ข้อมูลที่ดึงจากฐานข้อมูล: {sample_data}
สถิติที่คำนวณเพิ่มเติม: {stats}

จงตอบผู้ใช้โดยยึดโครงสร้างและข้อบังคับนี้อย่างเคร่งครัด:

โครงสร้างการตอบ:
1. Headline (สรุปผลหลัก): เขียนแค่ 1 บรรทัด เน้นตัวหนา (Markdown) ในส่วนสำคัญ
2. Details (รายละเอียด): ใช้ Bullet points (- ...)
3. Insight (ข้อสังเกต): สถิติหรือข้อสังเกตที่เป็นประโยชน์ 1 บรรทัดสั้นๆ

ข้อบังคับ:
1. ห้ามเกริ่นนำหรือปิดท้าย ให้เริ่มที่ Headline ทันที
2. ตอบเป็นภาษาไทยที่กระชับและเป็นทางการ
"""
        system_msg = SystemMessage(
            content="You are a professional Data Analyst Assistant. "
                    "Output ONLY the final Thai report directly without reasoning or check-lists."
        )

        raw_answer = llm.invoke([system_msg, HumanMessage(content=summary_prompt)]).content.strip()
        cleaned = clean_summary_response(raw_answer)
        return cleaned if cleaned else _fallback_summary(user_query, raw_data, stats)
    except Exception as e:
        logger.error(f"Error generating executive insight: {e}")
        return _fallback_summary(user_query, raw_data, stats)
