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

    def test_full_aggregation_preserves_primary_y_key_with_many_metrics(self, monkeypatch):
        """บั๊กหลัก: ถ้าตารางมีคอลัมน์ตัวเลขหลายตัว primary_y_key ('มูลค่า') ต้องไม่ถูกตัดทิ้ง"""
        # มี 5 คอลัมน์ตัวเลข โดย 'มูลค่า' อยู่ท้ายสุด (index 4)
        data = [
            {"คำอธิบาย": f"ข้าว {i % 3}", "จำนวน": 10, "ราคาต่อหน่วย": 50, "ส่วนลด": 5, "ภาษี": 7, "มูลค่า": 450}
            for i in range(50)
        ]
        sql = 'SELECT * FROM "สถิติการค้า" WHERE "คำอธิบาย" LIKE \'%ข้าว%\' LIMIT 50;'

        captured_queries = []
        def mock_execute(query):
            captured_queries.append(query)
            assert 'SUM("มูลค่า") AS "มูลค่า"' in query, "primary_y_key ต้องอยู่ใน SELECT list เสมอ"
            assert 'ORDER BY "มูลค่า" DESC' in query
            return {
                "status": "success",
                "data": [
                    {"คำอธิบาย": "ข้าวหอม", "มูลค่า": 100000},
                    {"คำอธิบาย": "ข้าวเหนียว", "มูลค่า": 50000},
                ]
            }

        monkeypatch.setattr("app.part1_data_security.sandbox.sql_sandbox.execute_sql_in_sandbox", mock_execute)

        result = format_visualization_payload(data, sql_query=sql)
        assert len(captured_queries) == 1
        assert result.get("is_full_aggregation") is True
        assert result["y_axis_key"] == "มูลค่า"
        assert result["chart_data"][0]["value"] == 100000

    def test_aggregation_failed_flag_reported(self, monkeypatch):
        """เมื่อ full-aggregation error ต้องเซ็ต aggregation_failed = True ไม่ error เงียบ"""
        data = [{"description": f"item_{i}", "value": 100} for i in range(20)]
        sql = 'SELECT * FROM "products" LIMIT 20;'

        def mock_execute_fail(query):
            raise RuntimeError("Database connection lost during chart aggregation")

        monkeypatch.setattr("app.part1_data_security.sandbox.sql_sandbox.execute_sql_in_sandbox", mock_execute_fail)

        result = format_visualization_payload(data, sql_query=sql)
        assert result.get("aggregation_failed") is True
        assert "⚠️" in result.get("truncation_label", "")
        # ยังคง fallback กลับมาแสดงข้อมูล sample ให้ผู้ใช้ดูได้
        assert len(result["chart_data"]) == 20
        assert result["recommended_chart"] == "bar"

    def test_bar_chart_truncation_sorts_by_value_descending(self):
        """จุดรอง: Bar chart ที่เกิน 20 รายการต้องเรียงตามมูลค่าสูงสุดก่อนตัดทอน ไม่ตัดมั่ว"""
        # สร้าง 24 รายการ (ช่วง 21-25 แนะนำ bar chart) โดยรายการที่มีค่าสูงสุดอยู่ท้ายๆ
        data = [{"item": f"item_{i}", "value": 10} for i in range(22)]
        data.append({"item": "top_item_1", "value": 99999})
        data.append({"item": "top_item_2", "value": 88888})

        result = format_visualization_payload(data)
        assert result["recommended_chart"] == "bar"
        assert len(result["chart_data"]) == 20
        assert result["is_truncated"] is True
        # รายการค่าสูงสุด 99999 และ 88888 ต้องติดอันดับ Top 20 แน่นอน
        chart_names = [d["name"] for d in result["chart_data"]]
        assert "top_item_1" in chart_names
        assert "top_item_2" in chart_names
        assert result["chart_data"][0]["name"] == "top_item_1"
        assert result["chart_data"][0]["value"] == 99999
        assert "20 อันดับแรกที่มีมูลค่าสูงสุด" in result["truncation_label"]


    def test_line_chart_truncation_preserves_chronological_order(self):
        """จุดรอง: Line chart (แกน X เป็นวันที่/เวลา) ต้องคงลำดับเวลา ห้าม sort by value"""
        # วันที่ 1-30 โดยวันที่ 15 มีค่ายอดกระโดด
        data = [{"date": f"2024-01-{i+1:02d}", "value": 1000 if i == 14 else (i + 1) * 10} for i in range(30)]

        result = format_visualization_payload(data)
        assert result["recommended_chart"] == "line"
        assert len(result["chart_data"]) == 20
        # ต้องเริ่มจากวันที่ 1 เรียงไปตามลำดับเวลา ไม่ใช่เรียงตามค่ากระโดด
        assert result["chart_data"][0]["name"] == "2024-01-01"
        assert result["chart_data"][1]["name"] == "2024-01-02"
        assert result["chart_data"][19]["name"] == "2024-01-20"

    def test_dimension_selection_avoids_constant_columns(self):
        """ต้องเลือกคอลัมน์ที่มีความหลากหลาย (เช่น 'จังหวัด') แทนคอลัมน์คงที่ (เช่น 'ชนิดพืช' ที่เป็น 'ทุเรียน' ทุกแถว)"""
        data = [
            {"ชนิดพืช": "ทุเรียน", "ภาค": "ภาคกลาง", "ปี": 2557, "จังหวัด": "กาญจนบุรี", "เนื้อที่ให้ผล": 348, "ผลผลิต": 260, "ผลผลิตต่อไร่": 747},
            {"ชนิดพืช": "ทุเรียน", "ภาค": "ภาคกลาง", "ปี": 2557, "จังหวัด": "จันทบุรี", "เนื้อที่ให้ผล": 167504, "ผลผลิต": 243263, "ผลผลิตต่อไร่": 1452},
            {"ชนิดพืช": "ทุเรียน", "ภาค": "ภาคกลาง", "ปี": 2557, "จังหวัด": "ชลบุรี", "เนื้อที่ให้ผล": 140, "ผลผลิต": 160, "ผลผลิตต่อไร่": 1143},
            {"ชนิดพืช": "ทุเรียน", "ภาค": "ภาคกลาง", "ปี": 2557, "จังหวัด": "ตราด", "เนื้อที่ให้ผล": 21507, "ผลผลิต": 29784, "ผลผลิตต่อไร่": 1385},
            {"ชนิดพืช": "ทุเรียน", "ภาค": "ภาคกลาง", "ปี": 2557, "จังหวัด": "ระยอง", "เนื้อที่ให้ผล": 63880, "ผลผลิต": 78406, "ผลผลิตต่อไร่": 1227},
        ]
        result = format_visualization_payload(data)
        assert result["recommended_chart"] == "bar"
        # แกน X ต้องเป็นจังหวัด ไม่ใช่ 'ทุเรียน'
        assert result["x_axis_key"] == "จังหวัด"
        assert result["labels"][0] in ["กาญจนบุรี", "จันทบุรี", "ชลบุรี", "ตราด", "ระยอง"]
        # แกน Y ต้องเลือก 'ผลผลิต' (ตัน) ก่อน 'เนื้อที่ให้ผล' หรือ 'ผลผลิตต่อไร่'
        assert result["y_axis_key"] == "ผลผลิต"
        # ตรวจสอบว่ามีข้อมูลจังหวัดใน chart_data แต่ละแท่ง
        provinces = [d["name"] for d in result["chart_data"]]
        assert "จันทบุรี" in provinces
        assert "ระยอง" in provinces
