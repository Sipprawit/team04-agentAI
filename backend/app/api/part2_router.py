import logging
import re
from typing import List, Optional, Any, Dict
from fastapi import APIRouter, Query, HTTPException, Body
from pydantic import BaseModel

# --- Imports Part 2 (AI Core) ---
from app.part2_ai_core.translator.nl_translator import translate_nl_to_sql
from app.part2_ai_core.validator.security_validator import validate_sql_security
from app.part2_ai_core.validator.self_corrector import self_heal_sql

# --- Imports Part 1 (Data & Security) ---
from app.part1_data_security.sandbox.sql_sandbox import execute_sql_in_sandbox
from app.part1_data_security.integration.schema_inspector import get_database_schema_info, get_uploaded_tables

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


def _generate_follow_up_questions(user_query: str, sql_query: str, raw_data: list = None) -> list:
    """
    สร้าง 2-3 คำถามแนะนำต่อเนื่อง (Follow-up Questions) อย่างชาญฉลาด
    รองรับทั้งข้อมูลเชิงคุณภาพ (Qualitative/หมวดหมู่/ข้อความสรุป) และเชิงปริมาณ (Quantitative/ตัวเลข)
    ไม่ยึดติดกับเฉพาะเรื่องยอดขายหรือการเงิน
    """
    q_lower = user_query.lower()
    sql_upper = sql_query.upper() if sql_query else ""
    follow_ups = []

    # ตรวจสอบโครงสร้างคอลัมน์ของข้อมูลจริง
    if raw_data and len(raw_data) > 0:
        first_row = raw_data[0]
        keys = list(first_row.keys())

        # แยกคอลัมน์ตัวเลขเชิงปริมาณ กับคอลัมน์ข้อความ/หมวดหมู่
        from app.part3_analytics_insights.recommender.eda_analyzer import is_metric_column
        metric_cols = [k for k in keys if is_metric_column(k, [r.get(k) for r in raw_data[:5]])]
        text_cols = [k for k in keys if k not in metric_cols and not k.lower().endswith("id") and k.lower() != "id"]

        # 1. กรณีเป็นข้อมูลเชิงคุณภาพล้วน (ไม่มีตัวเลข หรือเป็นหมวดหมู่/สรุปผล)
        if not metric_cols and text_cols:
            primary_text_col = text_cols[0]
            follow_ups.append(f"จัดกลุ่มและนับจำนวนรายการตาม {primary_text_col}")
            follow_ups.append(f"แสดงรายการทั้งหมดที่ไม่ซ้ำกันในคอลัมน์ {primary_text_col}")
            if len(text_cols) > 1:
                follow_ups.append(f"แจกแจงความสัมพันธ์ระหว่าง {text_cols[0]} และ {text_cols[1]}")
            else:
                follow_ups.append("ค้นหากลุ่มที่มีการบันทึกข้อมูลมากที่สุด")

        # 2. กรณีมีตัวเลขเชิงสถิติที่แท้จริง
        elif metric_cols:
            primary_metric = metric_cols[0]
            label_col = text_cols[0] if text_cols else "รายการ"

            if "sum" not in sql_upper and "avg" not in sql_upper:
                follow_ups.append(f"สรุปผลรวมและค่าเฉลี่ยของ {primary_metric}")
            follow_ups.append(f"ค้นหา 5 อันดับแรกที่มี {primary_metric} สูงสุด")
            if len(raw_data) > 1:
                follow_ups.append(f"เปรียบเทียบ {primary_metric} แยกตาม {label_col}")

        # 3. กรณีมีคอลัมน์เวลา/ปี
        date_cols = [k for k in keys if any(d in k.lower() for d in ["date", "year", "month", "ปี", "วัน", "เดือน"])]
        if date_cols and metric_cols:
            follow_ups.append(f"วิเคราะห์แนวโน้มการเปลี่ยนแปลงตาม {date_cols[0]}")

    # Fallback กรณีไม่มีข้อมูล หรือไม่เข้าเงื่อนไขข้างต้น
    if not follow_ups:
        tbl_match = re.search(r'FROM\s+["\']?([a-zA-Z0-9_\u0E00-\u0E7F]+)["\']?', sql_query, re.IGNORECASE)
        tbl = tbl_match.group(1) if tbl_match else "ชุดข้อมูล"
        follow_ups.append("แสดงข้อมูลทั้งหมดในชุดข้อมูล")
        follow_ups.append("สรุปภาพรวมและสถิติสำคัญของข้อมูล")
        follow_ups.append("แจกแจงจำนวนรายการตามแต่ละหมวดหมู่")
        follow_ups.append("ค้นหา 5 อันดับแรกที่มีค่ามากที่สุด")

    # คืนค่า 2-3 คำถามที่ไม่ซ้ำกับคำถามเดิมของผู้ใช้
    clean_follow_ups = [f for f in follow_ups if f.strip() and f.strip() != user_query.strip()][:3]
    return clean_follow_ups


def _create_out_of_scope_response(query: str) -> dict:
    """
    สร้างคำตอบปฏิเสธอย่างสุภาพเมื่อเจอคำถามนอกขอบเขตข้อมูล (Out-of-Scope Guardrails & Zero Hallucination)
    ระบุบทบาทของระบบ พร้อมแนะนำ Guided Prompts ที่ยืดหยุ่นครอบคลุมทุกประเภทข้อมูล
    """
    uploaded = get_uploaded_tables()
    guides = [
        "แสดงข้อมูลทั้งหมดในชุดข้อมูล",
        "สรุปภาพรวมและสถิติสำคัญของข้อมูล",
        "แจกแจงจำนวนรายการตามแต่ละหมวดหมู่",
        "ค้นหา 5 อันดับแรกที่มีค่ามากที่สุด",
    ]
    if uploaded:
        tbl = uploaded[0]
        scope_desc = f"วิเคราะห์ข้อมูลและสรุปสถิติเชิงลึกจากชุดข้อมูลที่คุณนำเข้า (เช่น ตาราง `{tbl}`)"
    else:
        scope_desc = "วิเคราะห์ข้อมูล สรุปสถิติเชิงลึก และสร้างแผนภูมิจากชุดข้อมูลหรือไฟล์ CSV ที่คุณนำเข้า"

    guide_bullets = "\n".join(f"- *\"{g}\"*" for g in guides)
    response_text = (
        f"ขออภัยครับ ระบบนี้ออกแบบมาเพื่อ{scope_desc}เท่านั้น ไม่สามารถตอบคำถามทั่วไปในหัวข้ออื่นได้ครับ\n\n"
        f"💡 **คุณสามารถลองถามเกี่ยวกับข้อมูลที่ระบบรองรับได้นะครับ เช่น:**\n"
        f"{guide_bullets}\n\n"
        f"*(หรือคลิกปุ่ม **`+`** ด้านล่างเพื่อนำเข้าไฟล์ CSV ของคุณสำหรับการวิเคราะห์)*"
    )
    return {
        "query": query,
        "sql": "",
        "response": response_text,
        "visualization": None,
        "data": [],
        "follow_up_questions": guides,
    }


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
            "follow_up_questions": [],
        }

    user_query = user_query.strip()
    history = chat_history or []

    # Layer 1 Defense: ตรวจสอบคำสั่งอันตรายเบื้องต้นหากผู้ใช้พิมพ์ SQL ตรงๆ
    # เพื่อประหยัด Token และสกัดกั้นการพยายามลบ/แก้ไขข้อมูลตั้งแต่ก่อนส่งให้ LLM
    pre_sec = validate_sql_security(user_query)
    # ถ้าผู้ใช้ส่ง SQL โดยตรงมา และติดคำสั่งต้องห้าม (เช่น DROP, DELETE, ALTER)
    if not pre_sec["is_valid"] and any(user_query.upper().startswith(kw) for kw in ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "TRUNCATE", "PRAGMA"]):
        logger.warning(f"Layer 1 Input Blocked: {pre_sec['reason']}")
        return {
            "query": user_query,
            "sql": user_query,
            "response": f"⚠️ คำสั่งถูกระงับเนื่องจากความปลอดภัย (Layer 1 Defense): {pre_sec['reason']}",
            "visualization": None,
            "data": [],
            "follow_up_questions": ["แสดงรายชื่อสินค้าทั้งหมด", "แสดงรายการคำสั่งซื้อล่าสุด"],
        }

    # ตรวจจับคำถามนอกขอบเขตข้อมูลโดยสิ้นเชิง (Fast-path Out-of-Scope Guardrails)
    out_of_scope_patterns = [
        "อากาศ", "พยากรณ์อากาศ", "ฝนตก", "อุณหภูมิ",
        "สูตรทำ", "สูตรอาหาร", "ทำอาหาร", "ผัดกะเพรา", "ต้มยำ", "วิธีทำอาหาร",
        "แต่งกลอน", "บทกวี", "เล่าเรื่อง", "นิทาน", "มุกตลก",
        "นายกรัฐมนตรี", "การเมือง", "เลือกตั้ง", "ดูดวง", "ราศี",
        "ผลบอล", "ฟุตบอล", "ดารา", "ร้องเพลง", "เนื้อเพลง"
    ]
    if any(p in user_query.lower() for p in out_of_scope_patterns):
        return _create_out_of_scope_response(user_query)

    # ตรวจสอบสถานะชุดข้อมูล: หากยังไม่มีการอัปโหลดไฟล์ CSV เข้ามาในระบบ
    uploaded_tables = get_uploaded_tables()
    if not uploaded_tables:
        # อนุญาตให้เข้าถึง mock data เฉพาะเมื่อผู้ใช้ระบุเจตนาชัดเจนว่าต้องการทดสอบด้วยชุดข้อมูลจำลอง
        q_lower = user_query.lower()
        mock_intent_keywords = [
            "mock", "จำลอง", "ทดสอบระบบ", "ตัวอย่างระบบ",
            "ลูกค้า", "คำสั่งซื้อ", "สินค้า",
            "customers", "products", "orders"
        ]
        is_explicit_mock_intent = any(kw in q_lower for kw in mock_intent_keywords)

        if not is_explicit_mock_intent:
            return {
                "query": user_query,
                "sql": "",
                "response": (
                    "ขณะนี้ยังไม่มีชุดข้อมูลหรือไฟล์ที่ถูกนำเข้าในระบบครับ\n\n"
                    "💡 **คำแนะนำ**: กรุณาคลิกปุ่ม **`+`** ด้านล่างกล่องข้อความเพื่อนำเข้าไฟล์ CSV ของคุณ "
                    "(เช่น ข้อมูลงบประมาณ, ข้อมูลการเงิน, ข้อมูลสถานที่ท่องเที่ยว/ร้านอาหาร หรือชุดข้อมูลอื่นๆ ที่ต้องการวิเคราะห์) "
                    "เพื่อเริ่มต้นการค้นหาและสร้างแผนภูมิรายงานได้ทันทีครับ"
                ),
                "visualization": None,
                "data": [],
                "follow_up_questions": [
                    "นำเข้าไฟล์ CSV เพื่อเริ่มวิเคราะห์ (+)",
                ],
            }

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
            "follow_up_questions": [
                "แสดงข้อมูลทั้งหมดในชุดข้อมูล",
                "สรุปภาพรวมและสถิติสำคัญของข้อมูล",
            ],
        }

    # กรณี AI ส่งสัญญาณว่าคำถามอยู่นอกขอบเขต (Zero Hallucination) หรือไม่ได้สร้างคำสั่ง SQL
    if sql_query.startswith("[OUT_OF_SCOPE]") or (not sql_query.upper().startswith("SELECT") and not sql_query.upper().startswith("WITH")):
        return _create_out_of_scope_response(user_query)

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
            if attempt < max_retries:
                sql_query = self_heal_sql(sql_query, f"Security Violation: {last_error}", schema_info, user_query)
                continue
            else:
                return {
                    "query": user_query,
                    "sql": sql_query,
                    "response": f"⚠️ คำสั่ง SQL ถูกระงับเนื่องจากความปลอดภัย: {last_error}",
                    "visualization": None,
                    "data": [],
                    "follow_up_questions": [],
                }

        # 3. รันใน Secure Sandbox (Part 1)
        sandbox_result = execute_sql_in_sandbox(sql_query)
        if sandbox_result["status"] == "success":
            break

        last_error = sandbox_result.get("message", "Unknown database error")
        logger.info(f"Query failed in sandbox (Attempt {attempt + 1}/{max_retries + 1}): {last_error}")

        if attempt < max_retries:
            healed_sql = self_heal_sql(sql_query, last_error, schema_info, user_query)
            if healed_sql and healed_sql != sql_query:
                sql_query = healed_sql
            else:
                break
        else:
            break

    default_fallbacks = [
        "แสดงข้อมูลทั้งหมดในชุดข้อมูล",
        "สรุปภาพรวมและสถิติสำคัญของข้อมูล",
        "แจกแจงจำนวนรายการตามแต่ละหมวดหมู่",
        "ค้นหา 5 อันดับแรกที่มีค่ามากที่สุด",
    ]

    if not sandbox_result or sandbox_result.get("status") != "success":
        return {
            "query": user_query,
            "sql": sql_query,
            "response": f"ขออภัยครับ ไม่สามารถดึงข้อมูลได้: {last_error}",
            "visualization": None,
            "data": [],
            "follow_up_questions": default_fallbacks[:2],
        }

    raw_data = sandbox_result.get("data", [])
    if not raw_data:
        return {
            "query": user_query,
            "sql": sql_query,
            "response": "ประมวลผลคำสั่งสำเร็จ แต่ไม่พบข้อมูลที่ตรงกับเงื่อนไขในฐานข้อมูล",
            "visualization": None,
            "data": [],
            "follow_up_questions": default_fallbacks,
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

    # 7. สร้างคำถามแนะนำต่อเนื่อง (Smart Follow-up Questions)
    follow_ups = _generate_follow_up_questions(user_query, sql_query, raw_data)

    return {
        "query": user_query,
        "sql": sql_query,
        "response": insight_text,
        "visualization": visualization,
        "data": raw_data,
        "follow_up_questions": follow_ups,
    }


@router.post("")
def query_post(request: QueryRequestModel):
    """
    Endpoint POST รับคำถามและประวัติการสนทนา (รองรับ Multi-turn context)
    ใช้ sync def เพื่อให้ FastAPI ส่งเข้า Threadpool อัตโนมัติ (ไม่บล็อก Event Loop)
    """
    return _run_query_pipeline(request.q, request.chat_history)


@router.get("")
def query_get(q: str = Query(..., description="คำถามภาษาไทยสำหรับถาม AI")):
    """
    Endpoint GET สำหรับเรียกถามแบบรวดเร็วผ่าน Browser หรือ Query Parameter
    ใช้ sync def เพื่อให้ FastAPI ส่งเข้า Threadpool อัตโนมัติ (ไม่บล็อก Event Loop)
    """
    return _run_query_pipeline(q)
