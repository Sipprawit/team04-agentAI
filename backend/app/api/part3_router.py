from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from app.part3_analytics_insights.recommender.chart_formatter import format_visualization_payload
from app.part3_analytics_insights.insights.executive_summarizer import generate_executive_insight

router = APIRouter(prefix="/part3", tags=["Part 3: Analytics & Insights"])


class InsightRequest(BaseModel):
    query: Optional[str] = Field(default="", description="คำถามของผู้ใช้")
    question: Optional[str] = Field(default="", description="คำถาม (alias สำหรับ query)")
    data: List[Dict[str, Any]] = Field(default_factory=list, description="ข้อมูลดิบที่ต้องการสรุป")

    @property
    def get_query(self) -> str:
        return self.query or self.question or ""


@router.post("/recommend-chart")
def recommend_chart(data: List[Dict[str, Any]]):
    """
    วิเคราะห์และแนะนำประเภทกราฟสำหรับข้อมูลดิบ (ใช้ sync def เพื่อไม่บล็อก Event Loop)
    """
    return format_visualization_payload(data)


@router.post("/generate-insight")
def generate_insight(req: InsightRequest):
    """
    สร้างข้อความสรุปเชิงลึกจากข้อมูลดิบสำหรับผู้บริหาร (ใช้ sync def เพื่อไม่บล็อก Event Loop)
    """
    text_insight = generate_executive_insight(req.get_query, req.data)
    return {"insight": text_insight}
