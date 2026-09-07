import pytest
from app.part3_analytics_insights.insights.executive_summarizer import (
    clean_summary_response,
    _fallback_summary,
    generate_executive_insight
)


class TestExecutiveSummarizer:
    def test_clean_summary_response_think_tags(self):
        raw = "<think>Generating insights for user</think>สรุปผล: พบสินค้า 10 รายการ"
        cleaned = clean_summary_response(raw)
        assert cleaned == "สรุปผล: พบสินค้า 10 รายการ"

    def test_clean_summary_response_english_instructions(self):
        raw = "Here is the summary:\n- Headline: ภาพรวมยอดขาย\n- Details: ยอดรวม 5,000 บาท"
        cleaned = clean_summary_response(raw)
        assert "Here is the summary" not in cleaned
        assert "ภาพรวมยอดขาย" in cleaned

    def test_fallback_summary_empty_data(self):
        summary = _fallback_summary("ยอดขายทั้งหมด", [], {})
        assert "ไม่พบข้อมูล" in summary

    def test_fallback_summary_with_stats(self):
        stats = {
            "target_column": "total",
            "count": 5,
            "total": 5000,
            "average": 1000,
            "max": 2000,
            "min": 500
        }
        data = [{"id": 1, "total": 1000}]
        summary = _fallback_summary("หายอดขายรวม", data, stats)
        assert "ผลการค้นหาข้อมูล" in summary
        assert "5,000" in summary
        assert "1,000" in summary

    def test_generate_executive_insight_mock(self, monkeypatch):
        class MockLLMResponse:
            content = "สรุปยอดขายรวม: 10,000 บาท เติบโตขึ้น 15%"

        class MockLLM:
            def invoke(self, messages):
                return MockLLMResponse()

        monkeypatch.setattr("app.part3_analytics_insights.insights.executive_summarizer.get_llm", lambda: MockLLM())
        insight = generate_executive_insight("สรุปยอดขาย", [{"total": 10000}])
        assert "สรุปยอดขายรวม: 10,000 บาท" in insight
