import re
from app.services.llm_service import get_llm
from langchain_core.messages import HumanMessage, SystemMessage
from app.part2_ai_core.translator.sql_prompt_builder import build_sql_prompt

def clean_extracted_sql(text_input: str) -> str:
    """สกัดคำสั่ง SQL บริสุทธิ์ออกจากข้อความตอบกลับของ LLM"""
    if not text_input:
        return ""
    if "</think>" in text_input:
        text_input = text_input.split("</think>")[-1]
    
    cleaned = text_input.replace("```sql", "").replace("```", "").replace("`", "").strip()
    
    junk_keywords = ['previous error', 'syntax error', 'user pasted', 'deconstruct', 'no dml/ddl', 'or with']
    
    # ดึง CTE WITH
    with_matches = re.finditer(r'\b(WITH\s+[a-zA-Z0-9_]+\s+AS\s*\([\s\S]+?\bSELECT\b[\s\S]+?)(?:;|\Z)', cleaned, re.IGNORECASE)
    for m in with_matches:
        sql = m.group(1).strip()
        if not any(j in sql.lower() for j in junk_keywords):
            if not sql.endswith(';'):
                sql += ';'
            return sql
            
    # ดึง SELECT ... FROM
    select_matches = re.finditer(r'\b(SELECT\s+[\s\S]+?\bFROM\b[\s\S]+?)(?:;|\Z)', cleaned, re.IGNORECASE)
    for m in select_matches:
        sql = m.group(1).strip()
        if not any(j in sql.lower() for j in junk_keywords):
            if not sql.endswith(';'):
                sql += ';'
            return sql
            
    return cleaned.strip()

def translate_nl_to_sql(user_query: str, chat_history: list = None) -> str:
    """
    ระบบแปลงภาษาธรรมชาติเป็นชุดคำสั่ง SQL (NL to SQL Translator System)
    """
    llm = get_llm()
    prompt = build_sql_prompt(user_query, chat_history)
    
    system_msg = SystemMessage(content="You are an expert SQLite Database Engineer. Output ONLY the raw SQL query directly. DO NOT output reasoning or think tags.")
    
    response = llm.invoke([system_msg, HumanMessage(content=prompt)]).content.strip()
    sql_clean = clean_extracted_sql(response)
    return sql_clean
