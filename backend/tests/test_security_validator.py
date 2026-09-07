"""
Unit Tests สำหรับ Security Validator (Part 2)
ทดสอบการตรวจจับคำสั่ง SQL อันตรายและป้องกัน False Positive
"""
import pytest
from app.part2_ai_core.validator.security_validator import validate_sql_security


class TestSQLSecurityValidator:
    """ทดสอบการตรวจจับคำสั่ง SQL อันตราย"""

    # --- คำสั่งที่ต้อง BLOCK ---

    def test_block_drop_table(self):
        result = validate_sql_security("DROP TABLE customers;")
        assert result["is_valid"] is False
        assert "DROP" in result["reason"]

    def test_block_delete(self):
        result = validate_sql_security("DELETE FROM orders WHERE id = 1;")
        assert result["is_valid"] is False

    def test_block_update(self):
        result = validate_sql_security("UPDATE products SET price = 0;")
        assert result["is_valid"] is False

    def test_block_insert(self):
        result = validate_sql_security("INSERT INTO users (name) VALUES ('hacker');")
        assert result["is_valid"] is False

    def test_block_alter(self):
        result = validate_sql_security("ALTER TABLE products ADD COLUMN hack TEXT;")
        assert result["is_valid"] is False

    def test_block_create(self):
        result = validate_sql_security("CREATE TABLE evil (id INTEGER);")
        assert result["is_valid"] is False

    def test_block_pragma(self):
        result = validate_sql_security("PRAGMA table_info(customers);")
        assert result["is_valid"] is False

    def test_block_attach(self):
        result = validate_sql_security("ATTACH DATABASE '/etc/passwd' AS evil;")
        assert result["is_valid"] is False

    def test_block_multi_statement(self):
        """ป้องกัน SQL Injection ต่อท้ายด้วย semicolon"""
        result = validate_sql_security("SELECT 1; DROP TABLE customers;")
        assert result["is_valid"] is False

    def test_block_empty_query(self):
        result = validate_sql_security("")
        assert result["is_valid"] is False

    def test_block_whitespace_only(self):
        result = validate_sql_security("   ")
        assert result["is_valid"] is False

    # --- คำสั่งที่ต้อง ALLOW ---

    def test_allow_simple_select(self):
        result = validate_sql_security("SELECT * FROM products;")
        assert result["is_valid"] is True

    def test_allow_select_with_where(self):
        result = validate_sql_security("SELECT name, price FROM products WHERE price > 1000;")
        assert result["is_valid"] is True

    def test_allow_select_with_join(self):
        sql = "SELECT o.id, c.name FROM orders o JOIN customers c ON o.customer_id = c.id;"
        result = validate_sql_security(sql)
        assert result["is_valid"] is True

    def test_allow_cte_with_select(self):
        sql = "WITH top_products AS (SELECT * FROM products WHERE price > 5000) SELECT * FROM top_products;"
        result = validate_sql_security(sql)
        assert result["is_valid"] is True

    def test_allow_aggregate_functions(self):
        sql = "SELECT COUNT(*), SUM(price), AVG(price), MAX(price), MIN(price) FROM products;"
        result = validate_sql_security(sql)
        assert result["is_valid"] is True

    # --- False Positive Prevention ---

    def test_no_false_positive_string_with_update(self):
        """ค่า string ที่มีคำว่า UPDATE ไม่ควรถูก block"""
        sql = "SELECT * FROM orders WHERE status = 'UPDATE';"
        result = validate_sql_security(sql)
        assert result["is_valid"] is True

    def test_no_false_positive_string_with_drop(self):
        """ค่า string ที่มีคำว่า DROP ไม่ควรถูก block"""
        sql = "SELECT * FROM products WHERE name = 'DROP Zone';"
        result = validate_sql_security(sql)
        assert result["is_valid"] is True

    def test_no_false_positive_comment_with_delete(self):
        """Comment ที่มีคำว่า DELETE ไม่ควรถูก block"""
        sql = "SELECT * FROM orders -- DELETE this later"
        result = validate_sql_security(sql)
        assert result["is_valid"] is True
