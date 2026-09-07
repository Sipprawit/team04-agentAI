import pytest
from app.part2_ai_core.validator.self_corrector import self_heal_sql


class TestSelfCorrector:
    def test_self_heal_sql_successful_fix(self, monkeypatch):
        class MockLLMResponse:
            content = "```sql\nSELECT id, name FROM products;\n```"

        class MockLLM:
            def invoke(self, messages):
                return MockLLMResponse()

        monkeypatch.setattr("app.part2_ai_core.validator.self_corrector.get_llm", lambda: MockLLM())

        fixed = self_heal_sql(
            failed_sql="SELECT id, prod_name FROM products;",
            error_message="no such column: prod_name",
            schema_info="TABLE products (id, name, price)",
            user_query="แสดงสินค้าทั้งหมด"
        )
        assert fixed == "SELECT id, name FROM products;"

    def test_self_heal_sql_exception_fallback(self, monkeypatch):
        class FailingLLM:
            def invoke(self, messages):
                raise RuntimeError("LLM Out of tokens")

        monkeypatch.setattr("app.part2_ai_core.validator.self_corrector.get_llm", lambda: FailingLLM())

        original = "SELECT id, prod_name FROM products;"
        fixed = self_heal_sql(
            failed_sql=original,
            error_message="syntax error",
            schema_info="TABLE products (id, name)",
            user_query="แสดงสินค้า"
        )
        assert fixed == original
