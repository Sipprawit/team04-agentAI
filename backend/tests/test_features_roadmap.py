"""
Unit Tests สำหรับ Roadmap Enhancements:
1. PII Detection (เลขบัตรประชาชน, เบอร์โทรศัพท์, อีเมล)
2. In-Memory Query Caching (Part 2)
3. User-Friendly Error Messages (Part 2)
4. Few-Shot Prompting (Part 2)
5. Dataset Deletion API (Part 1)
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from main import app
from app.db.database import engine
from app.part1_data_security.integration.csv_uploader import detect_pii
from app.api.part2_router import (
    _get_cache_key,
    _get_cached_result,
    _set_cached_result,
    clear_query_cache,
    _format_user_friendly_error,
)
from app.part2_ai_core.translator.sql_prompt_builder import build_sql_prompt

client = TestClient(app)


class TestPIIDetection:
    """ทดสอบการตรวจจับข้อมูลส่วนบุคคลที่ละเอียดอ่อน (PII)"""

    def test_detect_thai_citizen_id(self):
        headers = ["id", "citizen_id", "name"]
        rows = [
            ["1", "1100501234567", "นายสมชาย"],
            ["2", "1-1005-01234-56-7", "นางสมศรี"],
        ]
        warnings = detect_pii(headers, rows)
        assert len(warnings) == 1
        assert warnings[0]["column"] == "citizen_id"
        assert warnings[0]["type"] == "citizen_id"

    def test_detect_phone_number(self):
        headers = ["name", "tel"]
        rows = [
            ["สมชาย", "0812345678"],
            ["สมหญิง", "02-987-6543"],
        ]
        warnings = detect_pii(headers, rows)
        assert len(warnings) == 1
        assert warnings[0]["column"] == "tel"
        assert warnings[0]["type"] == "phone_number"

    def test_detect_email(self):
        headers = ["name", "contact_email"]
        rows = [
            ["สมชาย", "somchai@company.co.th"],
            ["สมศักดิ์", "somsak.dev@gmail.com"],
        ]
        warnings = detect_pii(headers, rows)
        assert len(warnings) == 1
        assert warnings[0]["column"] == "contact_email"
        assert warnings[0]["type"] == "email"

    def test_clean_dataset_no_warnings(self):
        headers = ["product_name", "category", "price", "stock"]
        rows = [
            ["ปากกา", "เครื่องเขียน", "25", "100"],
            ["สมุดบันทึก", "เครื่องเขียน", "50", "200"],
        ]
        warnings = detect_pii(headers, rows)
        assert len(warnings) == 0


class TestQueryCache:
    """ทดสอบระบบ In-Memory Query Caching"""

    def setup_method(self):
        clear_query_cache()

    def test_cache_miss_and_hit(self):
        key = _get_cache_key("ยอดขายทั้งหมด", ["orders"])
        assert _get_cached_result(key) is None

        payload = {"query": "ยอดขายทั้งหมด", "sql": "SELECT * FROM orders;", "response": "ผลลัพธ์"}
        _set_cached_result(key, payload)

        same_key = _get_cache_key("  ยอดขายทั้งหมด  ", ["orders"])
        cached = _get_cached_result(same_key)
        assert cached is not None
        assert cached["sql"] == "SELECT * FROM orders;"

    def test_clear_query_cache(self):
        key = _get_cache_key("test_query", ["orders"])
        _set_cached_result(key, {"dummy": 123})
        assert _get_cached_result(key) is not None
        clear_query_cache()
        assert _get_cached_result(key) is None


class TestUserFriendlyErrorMessages:
    """ทดสอบการแปลงข้อความ Error ทางเทคนิคเป็นคำแนะนำภาษาไทย"""

    def test_no_such_column_error(self):
        msg = _format_user_friendly_error("sqlite3.OperationalError: no such column: salary_amount", "เงินเดือนเท่าไหร่")
        assert "salary_amount" in msg
        assert "ไม่พบคอลัมน์" in msg

    def test_no_such_table_error(self):
        msg = _format_user_friendly_error("no such table: secret_dataset", "ดูข้อมูล secret_dataset")
        assert "ไม่พบตารางข้อมูล" in msg
        assert "นำเข้าไฟล์ CSV" in msg

    def test_rate_limit_error(self):
        msg = _format_user_friendly_error("Groq RateLimitError 429: TPM exceeded", "สรุปข้อมูล")
        assert "เกินขีดจำกัด" in msg or "ชั่วคราว" in msg

    def test_generic_fallback_error(self):
        msg = _format_user_friendly_error("Unexpected network socket drop", "สืบค้นข้อมูล")
        assert "เกิดข้อผิดพลาดในการประมวลผลข้อมูล" in msg


class TestFewShotPromptBuilder:
    """ทดสอบว่า Prompt Builder บรรจุ Few-Shot Examples ครบถ้วน"""

    def test_prompt_contains_few_shot_examples(self):
        prompt = build_sql_prompt("สรุปยอดโครงการทั้งหมด")
        assert "Few-Shot Examples" in prompt
        assert "ตัวอย่าง 1" in prompt
        assert "ตัวอย่าง 2" in prompt
        assert "ตัวอย่าง 6" in prompt
        assert "[OUT_OF_SCOPE]" in prompt


class TestDatasetDeletionAPI:
    """ทดสอบ API สำหรับลบ Dataset Table (Part 1)"""

    def test_delete_protected_system_table_forbidden(self):
        resp = client.delete("/part1/tables/customers")
        assert resp.status_code == 403
        assert "ไม่สามารถลบตารางระบบหรือตารางตัวอย่าง 'customers' ได้" in resp.json()["detail"]

    def test_delete_protected_chat_sessions_forbidden(self):
        resp = client.delete("/part1/tables/chat_sessions")
        assert resp.status_code == 403

    def test_delete_non_existent_table(self):
        resp = client.delete("/part1/tables/table_not_exists_12345")
        assert resp.status_code == 404
        assert "ไม่พบชุดข้อมูลตาราง 'table_not_exists_12345' ในระบบ" in resp.json()["detail"]

    def test_delete_custom_table_success(self):
        table_name = "test_custom_delete_me"
        with engine.connect() as conn:
            conn.execute(text(f'CREATE TABLE IF NOT EXISTS "{table_name}" (id INTEGER, val TEXT);'))
            conn.commit()

        resp = client.delete(f"/part1/tables/{table_name}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "success"
        assert data["table_name"] == table_name

        with engine.connect() as conn:
            check = conn.execute(
                text("SELECT name FROM sqlite_master WHERE type='table' AND name=:name;"),
                {"name": table_name}
            ).fetchone()
            assert check is None

class TestDatasetListingAPI:
    """ทดสอบ API GET /part1/datasets"""

    def test_list_datasets_success(self):
        resp = client.get("/part1/datasets")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "success"
        assert isinstance(data["datasets"], list)
        if len(data["datasets"]) > 0:
            item = data["datasets"][0]
            assert "table_name" in item
            assert "row_count" in item
            assert "columns" in item
            assert "is_uploaded" in item
            assert "is_deletable" in item


class TestAdvancedStatisticsAndAnomalies:
    """ทดสอบการคำนวณ Median, SD และ Anomaly Detection (Part 3)"""

    def test_median_and_std_dev_calculation(self):
        from app.part3_analytics_insights.insights.stat_calculator import calculate_advanced_statistics
        data = [
            {"product": "A", "price": 10},
            {"product": "B", "price": 20},
            {"product": "C", "price": 30},
            {"product": "D", "price": 40},
            {"product": "E", "price": 50},
        ]
        stats = calculate_advanced_statistics(data)
        assert stats["median"] == 30.0
        assert stats["std_dev"] > 0
        assert stats["average"] == 30.0

    def test_anomaly_detection_flags_outliers(self):
        from app.part3_analytics_insights.insights.stat_calculator import calculate_advanced_statistics
        # ข้อมูลปกติอยู่ระหว่าง 10-20 แต่มีค่ากระโดดไปที่ 500
        data = [
            {"item": "ปกติ 1", "amount": 10},
            {"item": "ปกติ 2", "amount": 12},
            {"item": "ปกติ 3", "amount": 15},
            {"item": "ปกติ 4", "amount": 14},
            {"item": "ปกติ 5", "amount": 11},
            {"item": "กระโดดผิดปกติ", "amount": 500},
        ]
        stats = calculate_advanced_statistics(data)
        assert "anomalies" in stats
        assert len(stats["anomalies"]) > 0
        top_anomaly = stats["anomalies"][0]
        assert top_anomaly["value"] == 500
        assert top_anomaly["label"] == "กระโดดผิดปกติ"
        assert top_anomaly["type"] == "high"

    def test_fallback_summary_includes_anomaly_note(self):
        from app.part3_analytics_insights.insights.executive_summarizer import _fallback_summary
        raw_data = [
            {"item": "ก", "amount": 10},
            {"item": "ข", "amount": 500},
            {"item": "ค", "amount": 12},
            {"item": "ง", "amount": 11},
        ]
        stats = {
            "total": 533,
            "average": 133.25,
            "median": 11.5,
            "anomalies": [{"label": "ข", "value": 500, "type": "high", "ratio_to_avg": 3.8}]
        }
        summary = _fallback_summary("สรุปยอด", raw_data, stats)
        assert "ข้อสังเกตค่าผิดปกติ" in summary
        assert "500" in summary


class TestSchemaRelevanceRanking:
    """ทดสอบการจัดลำดับตารางตามความเกี่ยวข้องในคำถาม (Part 2)"""

    def test_relevance_ranking_prioritizes_matching_table(self):
        from app.part1_data_security.integration.schema_inspector import get_database_schema_info
        info = get_database_schema_info(relevant_query="ลูกค้าทั้งหมดที่มียอดสั่งซื้อ")
        assert isinstance(info, str)
        # ตารางที่ชื่อหรือคอลัมน์ตรงกับคำถามควรได้รับการจัดอันดับ
        assert "customers" in info or "orders" in info
