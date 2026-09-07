"""
Unit Tests สำหรับ SQL Sandbox (Part 1)
ทดสอบ Read-only enforcement, Row limit, และ Timeout
"""
import pytest
from app.part1_data_security.sandbox.sql_sandbox import execute_sql_in_sandbox
from app.db.database import engine
from sqlalchemy import text


@pytest.fixture(scope="class", autouse=True)
def setup_test_db():
    """สร้างตารางทดสอบก่อนรัน tests"""
    with engine.connect() as conn:
        conn.execute(text("CREATE TABLE IF NOT EXISTS test_sandbox (id INTEGER PRIMARY KEY, name TEXT, value REAL);"))
        conn.execute(text("DELETE FROM test_sandbox;"))
        for i in range(10):
            conn.execute(text(f"INSERT INTO test_sandbox (id, name, value) VALUES ({i}, 'item_{i}', {i * 100.5});"))
        conn.commit()
    yield
    try:
        with engine.connect() as conn:
            conn.execute(text("DROP TABLE IF EXISTS test_sandbox;"))
            conn.commit()
    except Exception:
        pass


class TestSQLSandbox:
    """ทดสอบ Secure Code Execution Sandbox"""

    def test_successful_select(self):
        """SELECT ปกติต้องทำงานได้"""
        result = execute_sql_in_sandbox("SELECT * FROM test_sandbox;")
        assert result["status"] == "success"
        assert result["rows_count"] == 10

    def test_select_with_where(self):
        """SELECT with WHERE ต้องกรองข้อมูลได้"""
        result = execute_sql_in_sandbox("SELECT * FROM test_sandbox WHERE id < 3;")
        assert result["status"] == "success"
        assert result["rows_count"] == 3

    def test_aggregate_query(self):
        """Aggregate functions ต้องทำงานได้"""
        result = execute_sql_in_sandbox("SELECT COUNT(*) as cnt, SUM(value) as total FROM test_sandbox;")
        assert result["status"] == "success"
        assert result["rows_count"] == 1
        assert result["data"][0]["cnt"] == 10

    def test_block_insert(self):
        """INSERT ต้องถูก block ด้วย PRAGMA query_only"""
        result = execute_sql_in_sandbox("INSERT INTO test_sandbox (id, name, value) VALUES (999, 'evil', 0);")
        assert result["status"] == "error"

    def test_block_update(self):
        """UPDATE ต้องถูก block ด้วย PRAGMA query_only"""
        result = execute_sql_in_sandbox("UPDATE test_sandbox SET name = 'hacked' WHERE id = 1;")
        assert result["status"] == "error"

    def test_block_delete(self):
        """DELETE ต้องถูก block ด้วย PRAGMA query_only"""
        result = execute_sql_in_sandbox("DELETE FROM test_sandbox WHERE id = 1;")
        assert result["status"] == "error"

    def test_block_drop(self):
        """DROP TABLE ต้องถูก block ด้วย PRAGMA query_only"""
        result = execute_sql_in_sandbox("DROP TABLE test_sandbox;")
        assert result["status"] == "error"

    def test_row_limit(self):
        """ผลลัพธ์ต้องถูกตัดเมื่อเกิน max_rows"""
        result = execute_sql_in_sandbox("SELECT * FROM test_sandbox;", max_rows=3)
        assert result["status"] == "success"
        assert result["rows_count"] == 3
        assert "warning" in result

    def test_invalid_sql(self):
        """SQL ที่ผิดไวยากรณ์ต้อง return error"""
        result = execute_sql_in_sandbox("SELECTT * FROMM nowhere;")
        assert result["status"] == "error"

    def test_nonexistent_table(self):
        """Table ที่ไม่มีอยู่ต้อง return error"""
        result = execute_sql_in_sandbox("SELECT * FROM nonexistent_table_xyz;")
        assert result["status"] == "error"
