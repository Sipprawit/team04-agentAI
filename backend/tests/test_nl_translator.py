import pytest
from app.part2_ai_core.translator.nl_translator import clean_extracted_sql, translate_nl_to_sql


class TestNLTranslator:
    def test_clean_extracted_sql_think_tags(self):
        raw = "<think>Let me write the SQL query</think>SELECT * FROM customers;"
        assert clean_extracted_sql(raw) == "SELECT * FROM customers;"

    def test_clean_extracted_sql_markdown_block(self):
        raw = "Here is the query:\n```sql\nSELECT id, name FROM products;\n```\nEnjoy!"
        assert clean_extracted_sql(raw) == "SELECT id, name FROM products;"

    def test_clean_extracted_sql_generic_code_block(self):
        raw = "```\nSELECT count(*) FROM orders;\n```"
        assert clean_extracted_sql(raw) == "SELECT count(*) FROM orders;"

    def test_clean_extracted_sql_comments(self):
        raw = "-- Query to get products\n// Another comment\nSELECT * FROM products;"
        assert clean_extracted_sql(raw) == "SELECT * FROM products;"

    def test_clean_extracted_sql_cte(self):
        raw = "WITH recent_orders AS (SELECT * FROM orders LIMIT 5) SELECT * FROM recent_orders;"
        assert clean_extracted_sql(raw) == "WITH recent_orders AS (SELECT * FROM orders LIMIT 5) SELECT * FROM recent_orders;"

    def test_clean_extracted_sql_empty_or_none(self):
        assert clean_extracted_sql("") == ""
        assert clean_extracted_sql(None) == ""

    def test_translate_nl_to_sql_mock(self, monkeypatch):
        class MockLLMResponse:
            content = "```sql\nSELECT id, name FROM products;\n```"

        class MockLLM:
            def invoke(self, messages):
                return MockLLMResponse()

        monkeypatch.setattr("app.part2_ai_core.translator.nl_translator.get_llm", lambda: MockLLM())
        result = translate_nl_to_sql("แสดงสินค้าทั้งหมด")
        assert result == "SELECT id, name FROM products;"

    def test_translate_nl_to_sql_failure_fallback(self, monkeypatch):
        class FailingLLM:
            def invoke(self, messages):
                raise ConnectionError("API Unavailable")

        monkeypatch.setattr("app.part2_ai_core.translator.nl_translator.get_llm", lambda: FailingLLM())
        with pytest.raises(RuntimeError) as exc_info:
            translate_nl_to_sql("แสดงสินค้าทั้งหมด")
        assert "ไม่สามารถแปลงคำถามเป็น SQL ผ่าน AI ได้" in str(exc_info.value)

    def test_clean_extracted_sql_out_of_scope(self):
        raw = "[OUT_OF_SCOPE] คำถามนี้อยู่นอกเหนือขอบเขตข้อมูล"
        assert clean_extracted_sql(raw) == "[OUT_OF_SCOPE]"

    def test_clean_extracted_sql_refusal(self):
        raw = "ขออภัยครับ ระบบไม่สามารถตอบคำถามเกี่ยวกับสภาพอากาศได้"
        assert clean_extracted_sql(raw) == "[OUT_OF_SCOPE]"

