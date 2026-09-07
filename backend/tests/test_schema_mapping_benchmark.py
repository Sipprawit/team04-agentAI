import pytest
import os
import tempfile
from app.part1_data_security.integration.csv_uploader import (
    _detect_column_type,
    sanitize_identifier,
    upload_csv_to_db,
)


class TestSchemaMappingBenchmark:
    """
    ชุดทดสอบมาตรฐาน (Benchmark Suite) เพื่อประเมินความถูกต้องของ Schema Mapping
    ตามวัตถุประสงค์ข้อ 1:
    'ระบบต้องสามารถอ่านและทำความเข้าใจโครงสร้างตาราง (Schema Mapping) ได้อย่างถูกต้องครบถ้วนไม่น้อยกว่าร้อยละ 95'
    """

    # ชุดข้อมูลมาตรฐาน (Ground Truth Dataset) 40 คอลัมน์หลากหลายรูปแบบ
    BENCHMARK_COLUMNS = [
        # --- INTEGER Types (10 คอลัมน์) ---
        {"name": "user_id", "values": ["1", "2", "3", "4", "5"], "expected_type": "INTEGER"},
        {"name": "จำนวนสินค้า", "values": ["10", "20", "35", "100", "0"], "expected_type": "INTEGER"},
        {"name": "formatted_integer", "values": ["1,000", "2,500", "10,000", "99,999"], "expected_type": "INTEGER"},
        {"name": "negative_int", "values": ["-5", "-10", "0", "15"], "expected_type": "INTEGER"},
        {"name": "single_digit", "values": ["0", "1", "2", "3"], "expected_type": "INTEGER"},
        {"name": "big_int", "values": ["1000000", "2000000", "3500000"], "expected_type": "INTEGER"},
        {"name": "int_with_spaces", "values": [" 42 ", " 100 ", " 999 "], "expected_type": "INTEGER"},
        {"name": "int_with_nulls", "values": ["10", "", None, "30", "40"], "expected_type": "INTEGER"},
        {"name": "จำนวนครั้ง", "values": ["1", "5", "12", "8"], "expected_type": "INTEGER"},
        {"name": "order_sequence", "values": ["101", "102", "103", "104"], "expected_type": "INTEGER"},

        # --- REAL / FLOAT Types (10 คอลัมน์) ---
        {"name": "price", "values": ["10.50", "25.00", "99.99", "150.75"], "expected_type": "REAL"},
        {"name": "ราคาเฉลี่ย", "values": ["1,250.50", "2,300.00", "500.25"], "expected_type": "REAL"},
        {"name": "percentage", "values": ["0.05", "0.25", "0.75", "1.00"], "expected_type": "REAL"},
        {"name": "negative_float", "values": ["-12.34", "-0.50", "10.20"], "expected_type": "REAL"},
        {"name": "scientific_style", "values": ["0.001", "0.0005", "12.0"], "expected_type": "REAL"},
        {"name": "อัตราส่วน", "values": ["3.1415", "2.7182", "1.4142"], "expected_type": "REAL"},
        {"name": "float_with_empty", "values": ["15.5", "", "20.25", None], "expected_type": "REAL"},
        {"name": "small_decimal", "values": ["0.1", "0.2", "0.3"], "expected_type": "REAL"},
        {"name": "formatted_millions", "values": ["1,000,000.50", "2,500,000.00"], "expected_type": "REAL"},
        {"name": "score_avg", "values": ["85.5", "92.0", "78.25"], "expected_type": "REAL"},

        # --- DATE Types (10 คอลัมน์) ---
        {"name": "created_date", "values": ["2026-01-01", "2026-05-12", "2026-12-31"], "expected_type": "DATE"},
        {"name": "วันที่สั่งซื้อ", "values": ["2025-08-15", "2025-09-20", "2025-10-05"], "expected_type": "DATE"},
        {"name": "slash_date_eu", "values": ["15/08/2025", "01/12/2025", "28/02/2026"], "expected_type": "DATE"},
        {"name": "slash_date_iso", "values": ["2025/08/15", "2025/12/01", "2026/02/28"], "expected_type": "DATE"},
        {"name": "date_with_null", "values": ["2026-03-01", "", None, "2026-03-15"], "expected_type": "DATE"},
        {"name": "วันหมดอายุ", "values": ["2027-06-30", "2028-12-31", "2029-01-01"], "expected_type": "DATE"},
        {"name": "start_date", "values": ["01/01/2026", "15/01/2026", "31/01/2026"], "expected_type": "DATE"},
        {"name": "birthdate", "values": ["1990-05-20", "1985-11-15", "2000-01-01"], "expected_type": "DATE"},
        {"name": "transaction_date", "values": ["2026-07-04", "2026-07-05", "2026-07-06"], "expected_type": "DATE"},
        {"name": "event_date", "values": ["10/10/2025", "11/11/2025", "12/12/2025"], "expected_type": "DATE"},

        # --- TEXT Types (10 คอลัมน์) ---
        {"name": "customer_name", "values": ["สมชาย ใจดี", "John Doe", "สมหญิง รักเรียน"], "expected_type": "TEXT"},
        {"name": "product_code", "values": ["PROD-001", "PROD-002", "A-1234"], "expected_type": "TEXT"},
        {"name": "status", "values": ["ACTIVE", "PENDING", "CANCELLED"], "expected_type": "TEXT"},
        {"name": "email", "values": ["somchai@example.com", "test@domain.co.th"], "expected_type": "TEXT"},
        {"name": "phone_number", "values": ["081-234-5678", "02-999-8888"], "expected_type": "TEXT"},
        {"name": "description", "values": ["สินค้าคุณภาพดี นำเข้าจากญี่ปุ่น", "ไม่มีประกัน"], "expected_type": "TEXT"},
        {"name": "province", "values": ["กรุงเทพมหานคร", "เชียงใหม่", "น่าน"], "expected_type": "TEXT"},
        {"name": "mixed_content", "values": ["Version 2.0", "Release 1", "Beta"], "expected_type": "TEXT"},
        {"name": "url", "values": ["https://example.com", "http://test.org/page"], "expected_type": "TEXT"},
        {"name": "category", "values": ["เครื่องใช้ไฟฟ้า", "อาหารและเครื่องดื่ม", "เสื้อผ้า"], "expected_type": "TEXT"},
    ]

    def test_schema_mapping_accuracy_above_95_percent(self):
        """
        ทดสอบและคำนวณอัตราความถูกต้องของ Schema Mapping (Data Type Detection)
        ต้องมีความถูกต้องไม่ต่ำกว่าร้อยละ 95 (Accuracy >= 95.0%)
        """
        total_columns = len(self.BENCHMARK_COLUMNS)
        correct_predictions = 0
        failures = []

        for col in self.BENCHMARK_COLUMNS:
            detected = _detect_column_type(col["values"])
            if detected == col["expected_type"]:
                correct_predictions += 1
            else:
                failures.append({
                    "column": col["name"],
                    "expected": col["expected_type"],
                    "detected": detected,
                    "sample_values": col["values"][:3]
                })

        accuracy_rate = (correct_predictions / total_columns) * 100.0

        print(f"\n==========================================")
        print(f"SCHEMA MAPPING BENCHMARK RESULTS")
        print(f"==========================================")
        print(f"Total Columns Tested: {total_columns}")
        print(f"Correct Predictions:  {correct_predictions}")
        print(f"Accuracy Rate:        {accuracy_rate:.2f}% (Target: >= 95.0%)")
        if failures:
            print(f"Failures: {failures}")
        print(f"==========================================")

        assert accuracy_rate >= 95.0, (
            f"Schema mapping accuracy {accuracy_rate:.2f}% is below target 95.0%! "
            f"Failures: {failures}"
        )

    def test_column_sanitization_robustness(self):
        """
        ทดสอบความทนทานและความปลอดภัยของการตั้งชื่อคอลัมน์และตาราง (Sanitization)
        ต้องปลอดภัยจาก SQL Injection 100%
        """
        dangerous_names = [
            ("user_table; DROP TABLE users;--", "user_table_drop_table_users"),
            ("123_number_first", "col_123_number_first"),
            ("SELECT", "col_select"),
            ("ชื่อ สินค้า (พิเศษ)*&%", "ชื่อ_สินค้า_พิเศษ"),
            ("col___multiple___underscores", "col_multiple_underscores"),
            ("ORDER", "col_order"),
            ("", "unnamed"),
        ]

        for raw_name, expected_clean in dangerous_names:
            clean = sanitize_identifier(raw_name)
            assert clean == expected_clean
            # ตรวจสอบว่าไม่มีอักขระอันตรายหลงเหลือ
            assert not any(c in clean for c in [";", "'", '"', "-", " ", "(", ")", "*", "&", "%"])

    def test_end_to_end_csv_schema_mapping(self):
        """
        ทดสอบการนำเข้าไฟล์ CSV จริงหลายประเภทข้อมูลพร้อมกันและตรวจสอบ Schema Mapping ในตารางฐานข้อมูล
        """
        csv_content = (
            "รหัสสินค้า,ชื่อสินค้า,ราคาต่อหน่วย,จำนวนสต็อก,วันที่นำเข้า\n"
            "1001,กาแฟดอยช้าง,150.50,50,2026-01-15\n"
            "1002,ชาเขียวมัทฉะ,220.00,30,2026-02-10\n"
            "1003,ช็อกโกแลตร้อน,120.75,80,2026-03-01\n"
        )

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, encoding="utf-8") as f:
            f.write(csv_content)
            temp_path = f.name

        try:
            result = upload_csv_to_db(temp_path, "benchmark_products")
            assert result["status"] == "success"
            assert result["row_count"] == 3

            types = result["detected_types"]
            # ตรวจสอบชนิดข้อมูลที่ตรวจจับได้
            assert types["รหัสสินค้า"] == "INTEGER"
            assert types["ชื่อสินค้า"] == "TEXT"
            assert types["ราคาต่อหน่วย"] == "REAL"
            assert types["จำนวนสต็อก"] == "INTEGER"
            assert types["วันที่นำเข้า"] == "DATE"
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
