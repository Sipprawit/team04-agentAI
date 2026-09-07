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
                '**ยอด', '**สัดส่วน', '**ผล', '**ข้อมูล', '**รายงาน', '**สินค้า', '**สถิติ',
                '**สรุป', '**รายการ', '**หมวด', '- ', '#', '**', 'ปี '
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
    if not raw_data:
        return "ไม่พบข้อมูลที่ตรงกับเงื่อนไขที่ค้นหา"
    count = len(raw_data)
    first_row = raw_data[0]
    keys = list(first_row.keys())

    unit_val = ""
    for k in keys:
        if 'unit' in k.lower() or 'หน่วย' in k.lower():
            unit_val = str(first_row.get(k, ""))
            break

    lines = [f"**ผลการค้นหาข้อมูล ({count} รายการ)**"]
    for row in raw_data[:6]:
        val_str = ", ".join([f"{k}: {v}" for k, v in row.items() if v is not None])
        lines.append(f"- {val_str}")
    if count > 6:
        lines.append(f"- และอีก {count - 6} รายการ...")

    if "total" in stats and "average" in stats:
        u_suffix = f" {unit_val}" if unit_val else ""
        lines.append(f"\n📊 **สถิติสำคัญ**: ยอดรวม = {stats.get('total'):,}{u_suffix}, ค่าเฉลี่ย = {stats.get('average'):,}{u_suffix}")
    return "\n".join(lines)


def generate_executive_insight(user_query: str, raw_data: list) -> str:
    """
    ระบบสร้างข้อความสรุปข้อมูลเชิงลึก (Automated Insight Generator System)
    เขียนบรรยายสรุปตัวเลขและสถิติสำคัญอย่างแม่นยำตามหน่วยจริงในข้อมูล (เช่น ร้อยละ, ชิ้น, บาท)
    """
    if not raw_data:
        return "ไม่พบข้อมูลที่ตรงกับเงื่อนไขในฐานข้อมูล"

    stats = calculate_advanced_statistics(raw_data)

    try:
        llm = get_llm()
        sample_data = raw_data[:15]

        summary_prompt = f"""คุณคือ Data Analyst Assistant ผู้เชี่ยวชาญด้านการวิเคราะห์ข้อมูลและสรุปรายงานเชิงสถิติ
คำถามจากผู้ใช้: "{user_query}"
ข้อมูลที่ดึงจากฐานข้อมูล (ซึ่งผ่านการกรองเงื่อนไขตามคำถามมาแล้ว): {sample_data}
จำนวนข้อมูลทั้งหมดที่พบ: {len(raw_data)} รายการ
สถิติที่คำนวณเพิ่มเติม: {stats}

จงสรุปและรายงานผลลัพธ์ข้อมูลที่ได้รับมานี้โดยยึดข้อบังคับอย่างเคร่งครัด:

1. **ข้อมูลที่ได้รับมานี้คือผลลัพธ์ที่ตรงตามเงื่อนไขที่ผู้ใช้ถามเรียบร้อยแล้ว**:
   - จงนำรายชื่อและตัวเลขในข้อมูลที่ได้รับมาสรุปให้ผู้ใช้ทันที (ห้ามปฏิเสธว่าไม่มีข้อมูลหรือไม่พบคอลัมน์)
2. **ระบุหน่วย (Unit) และความหมายของข้อมูลให้ถูกต้อง**:
   - หากหน่วยเป็น "ร้อยละ" หรือ "%" ให้ระบุหน่วยเป็น "ร้อยละ" หรือ "%" เสมอ (ห้ามเปลี่ยนเป็นบาทหรือล้านบาท)
3. **โครงสร้างการตอบ**:
   - **Headline (บรรทัดแรก)**: สรุปผลลัพธ์หลัก 1 บรรทัด (ใช้ Markdown **ตัวหนา**)
   - **Details**: รายละเอียดสำคัญโดยใช้ Bullet points (`- ...`) แสดงรายชื่อหมวดธุรกิจ/สินค้าและค่าตัวเลข
   - **Insight**: ข้อสังเกตที่เป็นประโยชน์ 1 บรรทัดสั้นๆ
4. **ข้อบังคับ**:
   - ห้ามเกริ่นนำหรือลงท้าย ให้เข้าเรื่องที่ Headline ทันที
   - ใช้ภาษาไทยที่กระชับ เป็นทางการ และอ่านง่าย
"""
        system_msg = SystemMessage(
            content="You are an expert Data Analyst Assistant. Present and summarize the filtered data provided directly. DO NOT reject or complain about missing filter columns since the SQL query has already filtered the records."
        )

        raw_answer = llm.invoke([system_msg, HumanMessage(content=summary_prompt)]).content.strip()
        cleaned = clean_summary_response(raw_answer)
        return cleaned if cleaned else _fallback_summary(user_query, raw_data, stats)
    except Exception as e:
        logger.error(f"Error generating executive insight: {e}")
        return _fallback_summary(user_query, raw_data, stats)
