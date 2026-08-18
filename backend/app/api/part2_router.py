from fastapi import APIRouter, Query, HTTPException
from app.part2_ai_core.translator.nl_translator import translate_nl_to_sql
from app.part2_ai_core.validator.security_validator import validate_sql_security
from app.part1_data_security.sandbox.sql_sandbox import execute_sql_in_sandbox
from app.part2_ai_core.validator.self_corrector import self_heal_sql
from app.part1_data_security.integration.schema_inspector import get_database_schema_info
from app.part3_analytics_insights.insights.executive_summarizer import generate_executive_insight
from app.part3_analytics_insights.recommender.chart_formatter import format_visualization_payload

router = APIRouter(prefix="/query", tags=["Part 2 & Main Workflow: Query & SQL Execution"])

@router.get("")
async def query_pipeline(q: str = Query(..., description="คำถามภาษาไทยสำหรับถาม AI")):
    """
    Pipeline หลักที่เชื่อมโยง Part 1, Part 2 และ Part 3 เข้าด้วยกัน
    คำถามภาษาคน -> แปลง SQL -> ตรวจ Security -> รันใน Sandbox -> สร้างกราฟ & สรุปผล
    """
    # 1. แปลงคำถามเป็น SQL (Part 2)
    sql_query = translate_nl_to_sql(q)
    
    # 2. ตรวจสอบ Security Validator (Part 2)
    security = validate_sql_security(sql_query)
    if not security["is_valid"]:
        raise HTTPException(status_code=400, detail=security["reason"])
        
    # 3. รันใน Secure Sandbox (Part 1)
    sandbox_result = execute_sql_in_sandbox(sql_query)
    
    # 4. หากเกิด Error ใน Sandbox ให้ลอง Self-healing (Part 2)
    if sandbox_result["status"] == "error":
        schema_info = get_database_schema_info()
        healed_sql = self_heal_sql(sql_query, sandbox_result["message"], schema_info)
        sandbox_result = execute_sql_in_sandbox(healed_sql)
        if sandbox_result["status"] == "error":
            return {"query": q, "sql": healed_sql, "response": f"เกิดข้อผิดพลาดในการดึงข้อมูล: {sandbox_result['message']}"}
        sql_query = healed_sql

    raw_data = sandbox_result["data"]
    if not raw_data:
        return {"query": q, "sql": sql_query, "response": "ไม่พบข้อมูลที่ต้องการในฐานข้อมูล"}

    # 5. สร้างข้อความสรุปเชิงลึกภาษาไทย (Part 3)
    insight_text = generate_executive_insight(q, raw_data)
    
    # 6. แนะนำกราฟและจัดเตรียมข้อมูล X-Y (Part 3)
    visualization = format_visualization_payload(raw_data)
    
    return {
        "query": q,
        "sql": sql_query,
        "response": insight_text,
        "visualization": visualization,
        "data": raw_data
    }
