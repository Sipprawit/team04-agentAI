import logging
from typing import List, Optional, Any, Dict
from fastapi import APIRouter, Query, HTTPException, Body
from pydantic import BaseModel

# --- Imports Part 2 (AI Core) ---
from app.part2_ai_core.translator.nl_translator import translate_nl_to_sql
from app.part2_ai_core.validator.security_validator import validate_sql_security
from app.part2_ai_core.validator.self_corrector import self_heal_sql

# --- Imports Part 1 (Data & Security) ---
from app.part1_data_security.sandbox.sql_sandbox import execute_sql_in_sandbox
from app.part1_data_security.integration.schema_inspector import get_database_schema_info

# --- Imports Part 3 (Analytics & Insights) ---
from app.part3_analytics_insights.insights.executive_summarizer import generate_executive_insight
from app.part3_analytics_insights.recommender.chart_formatter import format_visualization_payload

logger = logging.getLogger("QueryPipeline")
router = APIRouter(prefix="/query", tags=["Part 2 & Main Workflow: Query & SQL Execution"])


class ChatMessageModel(BaseModel):
    role: str
    text: Optional[str] = ""
    content: Optional[str] = ""


class QueryRequestModel(BaseModel):
    q: str
    chat_history: Optional[List[Dict[str, Any]]] = []


def _run_query_pipeline(user_query: str, chat_history: list = None) -> dict:
    """
    ฟังก์ชันแกนกลางประมวลผล Pipeline:
    คำถามภาษาคน -> แปลง SQL -> ตรวจ Security -> รันใน Sandbox (Agentic self-heal loop) -> สรุป Insight & สร้าง Visualization
    """
    if not user_query or not user_query.strip():
        return {
            "query": "",
            "sql": "",
            "response": "กรุณาพิมพ์คำถามที่ต้องการค้นหาหรือวิเคราะห์ข้อมูล",
            "visualization": None,
            "data": [],
        }

    user_query = user_query.strip()
    history = chat_history or []

    # 1. แปลงคำถามเป็น SQL (Part 2)
    try:
        sql_query = translate_nl_to_sql(user_query, history)
    except Exception as e:
        logger.error(f"Translation failed: {e}")
        return {
            "query": user_query,
            "sql": "",
            "response": f"ขออภัยครับ ไม่สามารถเชื่อมต่อกับ AI เพื่อแปลคำถามเป็น SQL ได้ ({str(e)})",
            "visualization": None,
            "data": [],
        }

    schema_info = get_database_schema_info()
    max_retries = 2
    sandbox_result = None
    last_error = ""

    # 2-4. Agentic Loop: ตรวจ Security + รันใน Sandbox + Self-healing เมื่อเกิดข้อผิดพลาด
    for attempt in range(max_retries + 1):
        # 2. ตรวจสอบความปลอดภัย (Security Validator)
        security = validate_sql_security(sql_query)
        if not security["is_valid"]:
            last_error = security["reason"]
            logger.warning(f"Security validation blocked query: {last_error}")
            # ถ้าโดน block ให้ AI ลองแก้ query ใหม่
            if attempt < max_retries:
                sql_query = self_heal_sql(sql_query, f"Security Violation: {last_error}", schema_info)
                continue
            else:
                return {
                    "query": user_query,
                    "sql": sql_query,
                    "response": f"⚠️ คำสั่ง SQL ถูกระงับเนื่องจากความปลอดภัย: {last_error}",
                    "visualization": None,
                    "data": [],
                }

        # 3. รันใน Secure Sandbox (Part 1)
        sandbox_result = execute_sql_in_sandbox(sql_query)
        if sandbox_result["status"] == "success":
            break  # รันผ่าน สำเร็จ หลุดลูปทันที

        # ถ้า Sandbox เกิด error
        last_error = sandbox_result.get("message", "Unknown database error")
        logger.info(f"Query failed in sandbox (Attempt {attempt + 1}/{max_retries + 1}): {last_error}")

        if attempt < max_retries:
            # 4. Self-healing (Part 2)
            healed_sql = self_heal_sql(sql_query, last_error, schema_info)
            if healed_sql and healed_sql != sql_query:
                sql_query = healed_sql
            else:
                break
        else:
            break

    # ถ้าหลังลองแก้แล้วยังไม่ผ่าน
    if not sandbox_result or sandbox_result.get("status") != "success":
        return {
            "query": user_query,
            "sql": sql_query,
            "response": f"ขออภัยครับ ไม่สามารถดึงข้อมูลได้: {last_error}",
            "visualization": None,
            "data": [],
        }

    raw_data = sandbox_result.get("data", [])
    if not raw_data:
        return {
            "query": user_query,
            "sql": sql_query,
            "response": "ประมวลผลคำสั่งสำเร็จ แต่ไม่พบข้อมูลที่ตรงกับเงื่อนไขในฐานข้อมูล",
            "visualization": None,
            "data": [],
        }

    # 5. สรุป Insight ภาษาไทยสำหรับผู้บริหาร (Part 3)
    try:
        insight_text = generate_executive_insight(user_query, raw_data)
    except Exception as e:
        logger.error(f"Insight generation error: {e}")
        insight_text = f"พบข้อมูลทั้งหมด {len(raw_data)} รายการ"

    # 6. แนะนำกราฟและจัดเตรียมข้อมูล X-Y (Part 3)
    try:
        visualization = format_visualization_payload(raw_data)
    except Exception as e:
        logger.error(f"Visualization payload error: {e}")
        visualization = None

    return {
        "query": user_query,
        "sql": sql_query,
        "response": insight_text,
        "visualization": visualization,
        "data": raw_data,
    }


@router.post("")
async def query_post(request: QueryRequestModel):
    """
    Endpoint POST รับคำถามและประวัติการสนทนา (รองรับ Multi-turn context)
    """
    return _run_query_pipeline(request.q, request.chat_history)


@router.get("")
async def query_get(q: str = Query(..., description="คำถามภาษาไทยสำหรับถาม AI")):
    """
    Endpoint GET สำหรับเรียกถามแบบรวดเร็วผ่าน Browser หรือ Query Parameter
    """
    return _run_query_pipeline(q)
