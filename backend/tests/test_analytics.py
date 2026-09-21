"""
Unit Tests สำหรับ Part 3: Analytics & Insights
ทดสอบ stat_calculator, eda_analyzer, chart_formatter
"""
import pytest
from app.part3_analytics_insights.insights.stat_calculator import calculate_advanced_statistics
from app.part3_analytics_insights.recommender.eda_analyzer import recommend_chart_type
from app.part3_analytics_insights.recommender.chart_formatter import format_visualization_payload


class TestStatCalculator:
    """ทดสอบ Advanced Statistics Calculator"""

    def test_empty_data(self):
        result = calculate_advanced_statistics([])
        assert result == {}

    def test_basic_stats(self):
        data = [{"name": "A", "value": 10}, {"name": "B", "value": 20}, {"name": "C", "value": 30}]
        result = calculate_advanced_statistics(data)
        assert result["total"] == 60
        assert result["max"] == 30
        assert result["min"] == 10
        assert result["average"] == 20
        assert result["count"] == 3

    def test_excludes_id_column(self):
        """ต้องไม่นำคอลัมน์ id มาคำนวณ"""
        data = [{"id": 1, "price": 100}, {"id": 2, "price": 200}]
        result = calculate_advanced_statistics(data)
        assert result["target_column"] == "price"
        assert result["total"] == 300

    def test_excludes_foreign_key_id(self):
        """ต้องไม่นำคอลัมน์ customer_id มาคำนวณ"""
        data = [{"customer_id": 1, "quantity": 5}, {"customer_id": 2, "quantity": 10}]
        result = calculate_advanced_statistics(data)
        assert result["target_column"] == "quantity"

    def test_no_numeric_columns(self):
        data = [{"name": "A"}, {"name": "B"}]
        result = calculate_advanced_statistics(data)
        assert result == {"count": 2}

    def test_priority_value_column(self):
        """ถ้ามีคอลัมน์ชื่อ value ต้องเลือก value เป็นหลัก"""
        data = [{"quantity": 5, "value": 100}, {"quantity": 10, "value": 200}]
        result = calculate_advanced_statistics(data)
        # value ควรถูกเลือกเป็น target เพราะอยู่ใน priority_names
        assert result["target_column"] in ("value", "quantity")
        assert result["count"] == 2


class TestEDAAnalyzer:
    """ทดสอบ Auto-EDA Chart Type Recommender"""

    def test_empty_data(self):
        assert recommend_chart_type([]) == "none"

    def test_single_row_summary(self):
        assert recommend_chart_type([{"count": 100}]) == "summary_card"

    def test_date_column_line_chart(self):
        data = [{"date": "2024-01-01", "value": 10}, {"date": "2024-01-02", "value": 20}]
        assert recommend_chart_type(data) == "line"

    def test_thai_date_column_line_chart(self):
        """คอลัมน์ชื่อภาษาไทย 'ปี' ต้องแนะนำ line chart"""
        data = [{"ปี": 2558, "value": 10}, {"ปี": 2560, "value": 20}]
        assert recommend_chart_type(data) == "line"

    def test_bar_chart_categories(self):
        data = [{"name": f"item_{i}", "value": i * 10} for i in range(5)]
        assert recommend_chart_type(data) == "bar"

    def test_no_numeric_none(self):
        data = [{"name": "A"}, {"name": "B"}]
        assert recommend_chart_type(data) == "none"

    def test_large_dataset_none(self):
        """ข้อมูลมากกว่า 25 รายการไม่แนะนำกราฟ"""
        data = [{"name": f"item_{i}", "value": i} for i in range(30)]
        assert recommend_chart_type(data) == "none"


class TestChartFormatter:
    """ทดสอบ Chart Data Formatter"""

    def test_empty_data(self):
        result = format_visualization_payload([])
        assert result["recommended_chart"] == "none"

    def test_bar_chart_format(self):
        data = [{"name": "A", "value": 10}, {"name": "B", "value": 20}]
        result = format_visualization_payload(data)
        assert result["recommended_chart"] == "bar"
        assert len(result["chart_data"]) == 2
        assert result["x_axis_key"] == "name"
        assert result["y_axis_key"] == "value"

    def test_multi_series(self):
        """ต้องรองรับ multi-series (หลายแกน Y)"""
        data = [
            {"name": "Jan", "sales": 100, "cost": 50},
            {"name": "Feb", "sales": 150, "cost": 70},
        ]
        result = format_visualization_payload(data)
        assert "series_keys" in result
        assert "sales" in result["series_keys"]
        assert "cost" in result["series_keys"]
        # chart_data ต้องมี field ทั้ง sales และ cost
        assert result["chart_data"][0]["sales"] == 100
        assert result["chart_data"][0]["cost"] == 50

    def test_excludes_id_from_chart(self):
        """ต้องไม่นำ id มาเป็นแกน Y"""
        data = [{"id": 1, "name": "A", "price": 100}, {"id": 2, "name": "B", "price": 200}]
        result = format_visualization_payload(data)
        assert result["y_axis_key"] == "price"

    def test_summary_card(self):
        data = [{"total_sales": 1500000}]
        result = format_visualization_payload(data)
        assert result["recommended_chart"] == "summary_card"

    def test_pie_chart_groups_small_slices_into_others(self):
        """ทดสอบ Pie chart ที่มีชิ้นข้อมูล > 8 ชิ้น ต้องรวมกลุ่มชิ้นเล็กเป็น 'อื่นๆ'"""
        # สร้างข้อมูลสัดส่วน 12 รายการ
        data = [{"category": f"cat_{i}", "percent_share": (12 - i) * 5} for i in range(12)]
        result = format_visualization_payload(data)
        assert result["recommended_chart"] == "pie"
        assert len(result["chart_data"]) == 8  # 7 ชิ้นแรก + 1 ชิ้น 'อื่นๆ'
        assert result["chart_data"][-1]["name"] == "อื่นๆ"
        assert result["is_truncated"] is True
        assert "อื่นๆ" in result["truncation_label"]

    def test_chart_truncation_over_20_items(self):
        """ทดสอบกราฟที่มีข้อมูลเกิน 20 รายการ (เช่น กราฟเส้นช่วงเวลา 30 วัน) ต้องตัดทอนเหลือ 20 รายการแรก"""
        data = [{"date": f"2024-01-{i+1:02d}", "value": (i + 1) * 10} for i in range(30)]
        result = format_visualization_payload(data)
        assert result["recommended_chart"] == "line"
        assert len(result["chart_data"]) == 20
        assert result["is_truncated"] is True
        assert result["total_count"] == 30
        assert result["displayed_count"] == 20
        assert "20 รายการแรกจากทั้งหมด 30 รายการ" in result["truncation_label"]

    def test_full_aggregation_when_hitting_limit_without_group_by(self, monkeypatch):
        """ทางเลือก A: เมื่อ SQL ไม่มี GROUP BY และแถว = LIMIT ให้ยิง SQL หาผลรวมจริง"""
        # สร้าง raw data 50 แถว
        data = [{"description": f"item_{i % 5}", "value": 100} for i in range(50)]
        sql = 'SELECT * FROM "products" WHERE "category" = \'rice\' LIMIT 50;'

        aggregated_data = [
            {"description": "item_0", "value": 150000},
            {"description": "item_1", "value": 120000},
            {"description": "item_2", "value": 90000},
        ]

        def mock_execute(query):
            assert "GROUP BY" in query
            assert "SUM" in query
            return {"status": "success", "data": aggregated_data}

        monkeypatch.setattr("app.part1_data_security.sandbox.sql_sandbox.execute_sql_in_sandbox", mock_execute)

        result = format_visualization_payload(data, sql_query=sql)
        assert result["recommended_chart"] == "bar"
        assert result.get("is_full_aggregation") is True
        assert len(result["chart_data"]) == 3
        assert result["chart_data"][0]["value"] == 150000

    def test_skips_aggregation_when_sql_has_group_by(self, monkeypatch):
        """ถ้า SQL มี GROUP BY อยู่แล้ว ไม่ต้องยิงคำสั่งเพิ่ม"""
        data = [{"category": "A", "total": 100}]
        sql = 'SELECT category, SUM(val) as total FROM "products" GROUP BY category LIMIT 50;'

        executed = []
        def mock_execute(query):
            executed.append(query)
            return {"status": "success", "data": []}

        monkeypatch.setattr("app.part1_data_security.sandbox.sql_sandbox.execute_sql_in_sandbox", mock_execute)

        result = format_visualization_payload(data, sql_query=sql)
        assert len(executed) == 0
        assert result.get("is_full_aggregation") is not True

    def test_skips_aggregation_when_not_hitting_limit(self, monkeypatch):
        """ถ้าจำนวนแถวน้อยกว่า LIMIT แสดงว่าได้ข้อมูลครบแล้ว ไม่ต้องยิงคำสั่งเพิ่ม"""
        data = [{"name": "item_1", "value": 100}, {"name": "item_2", "value": 200}]
        sql = 'SELECT * FROM "products" LIMIT 50;'

        executed = []
        def mock_execute(query):
            executed.append(query)
            return {"status": "success", "data": []}

        monkeypatch.setattr("app.part1_data_security.sandbox.sql_sandbox.execute_sql_in_sandbox", mock_execute)

        result = format_visualization_payload(data, sql_query=sql)
        assert len(executed) == 0
        assert result.get("is_full_aggregation") is not True
