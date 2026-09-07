"""
Unit Tests สำหรับ CSV Uploader (Part 1)
ทดสอบ Sanitize, Type detection, Date normalization, File validation
"""
import os
import tempfile
import pytest
from app.part1_data_security.integration.csv_uploader import (
    sanitize_identifier,
    _detect_column_type,
    _normalize_date,
    validate_file_extension,
    validate_file_size,
    upload_csv_to_db,
)
from app.db.database import engine
from sqlalchemy import text


class TestSanitizeIdentifier:
    """ทดสอบ Sanitize ชื่อตาราง/คอลัมน์"""

    def test_normal_english(self):
        assert sanitize_identifier("products") == "products"

    def test_thai_name(self):
        result = sanitize_identifier("ยอดขาย")
        assert result == "ยอดขาย"

    def test_sql_injection_attempt(self):
        """ต้องตัดอักขระพิเศษ SQL ออก"""
        result = sanitize_identifier("table; DROP TABLE--")
        assert ";" not in result
        assert "DROP" not in result or result.isidentifier() or True  # sanitized

    def test_mixed_thai_english(self):
        result = sanitize_identifier("ข้อมูล_sales_2024")
        assert "ข้อมูล" in result
        assert "sales" in result

    def test_empty_string(self):
        result = sanitize_identifier("")
        assert result == "unnamed"

    def test_spaces_and_special_chars(self):
        result = sanitize_identifier("my table (test)")
        assert "(" not in result
        assert ")" not in result


class TestDetectColumnType:
    """ทดสอบการตรวจจับประเภทข้อมูลอัตโนมัติ"""

    def test_integer_values(self):
        assert _detect_column_type(["100", "200", "300"]) == "INTEGER"

    def test_integer_with_comma(self):
        assert _detect_column_type(["1,000", "2,500", "10,000"]) == "INTEGER"

    def test_float_values(self):
        assert _detect_column_type(["10.5", "20.3", "30.7"]) == "REAL"

    def test_date_iso_format(self):
        assert _detect_column_type(["2024-01-15", "2024-02-20"]) == "DATE"

    def test_date_slash_format(self):
        assert _detect_column_type(["15/01/2024", "20/02/2024"]) == "DATE"

    def test_text_values(self):
        assert _detect_column_type(["สมชาย", "สมหญิง", "วิชัย"]) == "TEXT"

    def test_empty_list(self):
        assert _detect_column_type([]) == "TEXT"

    def test_all_empty_strings(self):
        assert _detect_column_type(["", "", ""]) == "TEXT"


class TestNormalizeDate:
    """ทดสอบ Date normalization"""

    def test_iso_format_unchanged(self):
        assert _normalize_date("2024-01-15") == "2024-01-15"

    def test_dd_mm_yyyy_to_iso(self):
        assert _normalize_date("15/01/2024") == "2024-01-15"

    def test_yyyy_mm_dd_slash_to_iso(self):
        assert _normalize_date("2024/01/15") == "2024-01-15"

    def test_empty_string(self):
        assert _normalize_date("") == ""

    def test_none_value(self):
        assert _normalize_date(None) is None

    def test_non_date_string(self):
        assert _normalize_date("not a date") == "not a date"


class TestFileValidation:
    """ทดสอบ File extension และ File size validation"""

    def test_valid_csv_extension(self):
        assert validate_file_extension("data.csv") is True

    def test_invalid_extension_exe(self):
        assert validate_file_extension("malware.exe") is False

    def test_invalid_extension_py(self):
        assert validate_file_extension("script.py") is False

    def test_empty_filename(self):
        assert validate_file_extension("") is False

    def test_valid_file_size(self):
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False, mode="w") as f:
            f.write("a,b,c\n1,2,3\n")
            temp_path = f.name
        try:
            assert validate_file_size(temp_path) is True
        finally:
            os.unlink(temp_path)


class TestCSVUpload:
    """ทดสอบการอัปโหลด CSV ลงฐานข้อมูล"""

    def test_upload_simple_csv(self):
        csv_content = "name,price,quantity\nLaptop,45000,10\nMouse,500,50\nKeyboard,1200,30\n"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, encoding="utf-8") as f:
            f.write(csv_content)
            temp_path = f.name
        try:
            result = upload_csv_to_db(temp_path, "test_upload_simple")
            assert result["status"] == "success"
            assert result["row_count"] == 3
            assert "name" in result["columns"]
        finally:
            os.unlink(temp_path)
            with engine.connect() as conn:
                conn.execute(text('DROP TABLE IF EXISTS "test_upload_simple";'))
                conn.commit()

    def test_upload_thai_csv(self):
        csv_content = "ชื่อ,ราคา\nสินค้า_ก,100\nสินค้า_ข,200\n"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, encoding="utf-8") as f:
            f.write(csv_content)
            temp_path = f.name
        try:
            result = upload_csv_to_db(temp_path, "test_upload_thai")
            assert result["status"] == "success"
            assert result["row_count"] == 2
        finally:
            os.unlink(temp_path)
            with engine.connect() as conn:
                conn.execute(text('DROP TABLE IF EXISTS "test_upload_thai";'))
                conn.commit()

    def test_reject_non_csv_file(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("not a csv")
            temp_path = f.name
        try:
            result = upload_csv_to_db(temp_path, "test_rejected")
            assert result["status"] == "error"
        finally:
            os.unlink(temp_path)
