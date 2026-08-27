import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

# --- Imports ของ Part 2 (AI Core) ---
from app.part2_ai_core.translator.nl_translator import translate_nl_to_sql
from app.part2_ai_core.validator.security_validator import validate_sql_security
from app.part2_ai_core.validator.self_corrector import self_heal_sql

# --- Imports ของ Part 1 และ Part 3 ---
from app.part1_data_security.sandbox.sql_sandbox import execute_sql_in_sandbox
from app.part1_data_security.integration.schema_inspector import get_database_schema_info
from app.part3_analytics_insights.insights.executive_summarizer import generate_executive_insight
from app.part3_analytics_insights.recommender.chart_formatter import format_visualization_payload

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("MasterPipeline")

router = APIRouter(prefix="/query", tags=["Part 2 & Main Workflow: Query & SQL Execution"])

# --- สร้าง Pydantic Model เพื่อรับข้อมูลและประวัติแชท ---
class ChatMessage(BaseModel):
    role: str
    text: str

class QueryRequest(BaseModel):
    q: str
    chat_history: Optional[List[ChatMessage]] = []

@router.post("")
async def query_pipeline(request: QueryRequest):
    """
    Pipeline หลักที่เชื่อมโยง Part 1, Part 2 และ Part 3 เข้าด้วยกัน
    คำถามภาษาคน -> แปลง SQL -> ตรวจ Security -> รันใน Sandbox (วนลูปแก้ถ้าพัง) -> สร้างกราฟ & สรุปผล
    """
    user_query = request.q
    
    # 1. แปลงคำถามเป็น SQL (ดึงประวัติแชทมาใช้ด้วย)
    history_dict = [msg.model_dump() for msg in request.chat_history] if request.chat_history else []
    sql_query = translate_nl_to_sql(user_query, history_dict)
    
    # --- เริ่มระบบ Agentic Loop (ทดสอบ Security และ Sandbox สูงสุด 3 รอบ) ---
    max_retries = 3
    schema_info = get_database_schema_info()
    sandbox_result = None
    
    for attempt in range(max_retries + 1):
        # 2. ตรวจสอบ Security Validator
        security = validate_sql_security(sql_query)
        if not security["is_valid"]:
            error_msg = security["reason"]
            sandbox_result = {"status": "error"} # บังคับสถานะ error เพื่อให้ลงไปเข้าเงื่อนไขแก้โค้ด
        else:
            # 3. ถ้ารหัสปลอดภัย ให้ลองรันใน Secure Sandbox
            sandbox_result = execute_sql_in_sandbox(sql_query)
            if sandbox_result["status"] != "error":
                break # ถ้ารันผ่านฉลุย ให้หลุดจากลูปทันที
            
            error_msg = sandbox_result["message"]
            
        # 4. หากเกิด Error (จาก Security หรือ Sandbox) ให้ลอง Self-healing
        if attempt < max_retries:
            logger.warning(f"พบข้อผิดพลาด: {error_msg} | กำลังซ่อมแซมโค้ด (Attempt {attempt + 1})")
            sql_query = self_heal_sql(sql_query, error_msg, schema_info)
        else:
            # ถ้าครบ 3 รอบแล้วยังพังอยู่ ให้ตอบกลับไปแบบ Graceful Degradation (ไม่ให้เซิร์ฟล่ม)
            logger.error("AI ซ่อมโค้ดไม่สำเร็จหลังพยายามครบกำหนด")
            return {
                "query": user_query, 
                "sql": sql_query, 
                "response": f"ระบบพยายามประมวลผลแล้วแต่พบข้อผิดพลาดซับซ้อน: {error_msg}",
                "visualization": None,
                "data": []
            }
    # --- จบ Agentic Loop ---

    raw_data = sandbox_result.get("data", [])
    if not raw_data:
        return {
            "query": user_query, 
            "sql": sql_query, 
            "response": "ประมวลผลสำเร็จ แต่ไม่พบข้อมูลที่ต้องการในฐานข้อมูล",
            "visualization": None,
            "data": []
        }

    # 5. สร้างข้อความสรุปเชิงลึกภาษาไทย (Part 3)
    insight_text = generate_executive_insight(user_query, raw_data)
    
    # 6. แนะนำกราฟและจัดเตรียมข้อมูล X-Y (Part 3)
    visualization = format_visualization_payload(raw_data)
    
    return {
        "query": user_query,
        "sql": sql_query,
        "response": insight_text,
        "visualization": visualization,
        "data": raw_data
    }