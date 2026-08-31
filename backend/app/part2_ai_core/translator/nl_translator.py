import re
import logging
from app.services.llm_service import get_llm
from langchain_core.messages import HumanMessage, SystemMessage
from app.part2_ai_core.translator.sql_prompt_builder import build_sql_prompt

logger = logging.getLogger("NLTranslator")


def clean_extracted_sql(text_input: str) -> str:
    """
    สกัดคำสั่ง SQL บริสุทธิ์ออกจากข้อความตอบกลับของ LLM
    ตัด markdown, think tags, และคำอธิบายภาษาไทย/อังกฤษออก
    """
    if not text_input:
        return ""

    # ลบ <think>...</think> tags
    if "</think>" in text_input:
        text_input = text_input.split("</think>")[-1]

    # ลบ Markdown code blocks ```sql ... ```
    # หาเนื้อหาใน code block ก่อน
    code_block_match = re.search(r'```(?:sql)?\s*([\s\S]*?)\s*```', text_input, re.IGNORECASE)
    if code_block_match:
        text_input = code_block_match.group(1)

    cleaned = text_input.replace("`", "").strip()

    # ลบ comment บรรทัดที่ขึ้นต้นด้วย -- หรือ //
    lines = []
    for line in cleaned.splitlines():
        trimmed = line.strip()
        if not trimmed.startswith("--") and not trimmed.startswith("//"):
            lines.append(line)
    cleaned = "\n".join(lines).strip()

    junk_keywords = ['previous error', 'syntax error', 'user pasted', 'deconstruct', 'no dml/ddl', 'or with']

    # 1. ดึง CTE WITH ... SELECT ...
    with_matches = re.finditer(
        r'\b(WITH\s+[a-zA-Z0-9_]+\s+AS\s*\([\s\S]+?\bSELECT\b[\s\S]+?)(?:;|\Z)',
        cleaned,
        re.IGNORECASE
    )
    for m in with_matches:
        sql = m.group(1).strip()
        if not any(j in sql.lower() for j in junk_keywords):
            if not sql.endswith(';'):
                sql += ';'
            return sql

    # 2. ดึง SELECT ... FROM ...
    select_matches = re.finditer(
        r'\b(SELECT\s+[\s\S]+?\bFROM\b[\s\S]+?)(?:;|\Z)',
        cleaned,
        re.IGNORECASE
    )
    for m in select_matches:
        sql = m.group(1).strip()
        if not any(j in sql.lower() for j in junk_keywords):
            if not sql.endswith(';'):
                sql += ';'
            return sql

    # 3. ดึง SELECT ใดๆ (เช่น SELECT 1 หรือ scalar queries)
    if cleaned.upper().startswith("SELECT"):
        # ตัดคำอธิบายหลัง semicolon
        first_stmt = cleaned.split(";")[0].strip()
        return first_stmt + ";"

    return cleaned.strip()


def translate_nl_to_sql(user_query: str, chat_history: list = None) -> str:
    """
    ระบบแปลงภาษาธรรมชาติเป็นชุดคำสั่ง SQL (NL to SQL Translator System)
    พร้อม Error handling
    """
    try:
        llm = get_llm()
        prompt = build_sql_prompt(user_query, chat_history)

        system_msg = SystemMessage(
            content="You are an expert SQLite Database Engineer. Output ONLY the executable SQL query directly. "
                    "DO NOT output reasoning, explanations, or think tags."
        )

        response = llm.invoke([system_msg, HumanMessage(content=prompt)]).content.strip()
        sql_clean = clean_extracted_sql(response)
        return sql_clean
    except Exception as e:
        logger.error(f"Error during NL to SQL translation: {e}")
        # ถ้า LLM ล่ม ให้ fallback เป็น query พื้นฐานหรือ raise ชัดเจน
        raise RuntimeError(f"ไม่สามารถแปลงคำถามเป็น SQL ผ่าน AI ได้: {str(e)}")
