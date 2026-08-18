from fastapi import APIRouter, Body
from app.part3_analytics_insights.recommender.chart_formatter import format_visualization_payload
from app.part3_analytics_insights.insights.executive_summarizer import generate_executive_insight

router = APIRouter(prefix="/part3", tags=["Part 3: Analytics & Insights"])

@router.post("/recommend-chart")
async def recommend_chart(data: list = Body(...)):
    """วิเคราะห์และแนะนำประเภทกราฟสำหรับข้อมูลดิบ"""
    payload = format_visualization_payload(data)
    return payload

@router.post("/generate-insight")
async def generate_insight(query: str = Body(...), data: list = Body(...)):
    """สร้างข้อความสรุปเชิงลึกจากข้อมูลดิบ"""
    text_insight = generate_executive_insight(query, data)
    return {"insight": text_insight}
