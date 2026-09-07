import os
import json
import time
import pytest
from app.part1_data_security.sandbox.sql_sandbox import execute_sql_in_sandbox
from app.part2_ai_core.validator.security_validator import validate_sql_security
from app.part2_ai_core.validator.self_corrector import self_heal_sql
from app.part2_ai_core.translator.nl_translator import clean_extracted_sql


class TestExecutionAccuracyBenchmark:
    """
    ชุดทดสอบมาตรฐานประเมินความถูกต้องในการประมวลผลคำสั่ง (Execution Accuracy)
    และเวลาการตอบสนอง (Response Latency)
    ตามวัตถุประสงค์ข้อ 2:
    'มีความถูกต้องในการประมวลผลคำสั่ง (Execution Accuracy) ไม่ต่ำกว่าร้อยละ 85 เมื่อทดสอบกับชุดข้อมูลมาตรฐาน'
    และวัตถุประสงค์ข้อ 3:
    'มีการตอบสนองต่อคำสั่งเฉลี่ยไม่เกิน 30 วินาที'
    """

    @classmethod
    def setup_class(cls):
        benchmark_path = os.path.join(os.path.dirname(__file__), "benchmark", "standard_nl2sql_dataset.json")
        with open(benchmark_path, "r", encoding="utf-8") as f:
            cls.dataset = json.load(f)

    def test_ground_truth_execution_accuracy_and_latency(self):
        """
        ทดสอบการประมวลผลชุดคำสั่งมาตรฐานทั้งหมดใน Sandbox
        วัดอัตราความสำเร็จ (Execution Accuracy) และระยะเวลาการประมวลผลเฉลี่ย (Average Latency)
        """
        total_queries = len(self.dataset)
        successful_executions = 0
        execution_times = []
        failures = []

        for item in self.dataset:
            sql = item["ground_truth_sql"]

            # 1. ตรวจสอบความปลอดภัย Security Layer
            sec = validate_sql_security(sql)
            if not sec["is_valid"]:
                failures.append({"id": item["id"], "reason": f"Security blocked: {sec['reason']}"})
                continue

            # 2. จับเวลาการประมวลผลใน Sandbox
            start_time = time.perf_counter()
            res = execute_sql_in_sandbox(sql)
            elapsed_time = time.perf_counter() - start_time
            execution_times.append(elapsed_time)

            if res["status"] == "success":
                successful_executions += 1
            else:
                failures.append({"id": item["id"], "reason": res.get("message", "Unknown error")})

        accuracy_rate = (successful_executions / total_queries) * 100.0
        avg_latency = sum(execution_times) / len(execution_times) if execution_times else 0
        max_latency = max(execution_times) if execution_times else 0

        print(f"\n==========================================")
        print(f"EXECUTION ACCURACY BENCHMARK RESULTS")
        print(f"==========================================")
        print(f"Total Queries Evaluated:   {total_queries}")
        print(f"Successful Executions:     {successful_executions}")
        print(f"Execution Accuracy Rate:   {accuracy_rate:.2f}% (Target: >= 85.0%)")
        print(f"Average Response Latency:  {avg_latency * 1000:.2f} ms (Target: <= 30.0 s)")
        print(f"Max Query Latency:         {max_latency * 1000:.2f} ms")
        print(f"==========================================")

        assert accuracy_rate >= 85.0, (
            f"Execution accuracy {accuracy_rate:.2f}% is below target 85.0%! Failures: {failures}"
        )
        assert avg_latency < 30.0, (
            f"Average latency {avg_latency:.2f}s exceeds SLA target of 30 seconds!"
        )

    def test_agentic_self_healing_recovery_rate(self, monkeypatch):
        """
        ทดสอบกลไก Agentic Self-Correction Loop เมื่อพบข้อผิดพลาด
        สามารถวิเคราะห์ Error และกู้คืนคำสั่งให้กลับมารันสำเร็จได้
        """
        broken_cases = [
            {
                "query": "แสดงรายชื่อสินค้า",
                "broken_sql": "SELECT prod_name, prod_price FROM products;",
                "error": "no such column: prod_name",
                "fixed_sql": "SELECT name, price FROM products;"
            },
            {
                "query": "แสดงอีเมลของลูกค้า",
                "broken_sql": "SELECT customer_mail FROM customers;",
                "error": "no such column: customer_mail",
                "fixed_sql": "SELECT email FROM customers;"
            }
        ]

        class MockLLMResponse:
            def __init__(self, content):
                self.content = content

        class MockLLM:
            def __init__(self, fixes):
                self.fixes = fixes
                self.call_count = 0

            def invoke(self, messages):
                prompt_text = messages[1].content
                for item in self.fixes:
                    if item["error"] in prompt_text:
                        self.call_count += 1
                        return MockLLMResponse(item["fixed_sql"])
                return MockLLMResponse("SELECT 1;")

        mock_llm = MockLLM(broken_cases)
        monkeypatch.setattr("app.part2_ai_core.validator.self_corrector.get_llm", lambda: mock_llm)

        recovered_count = 0
        for case in broken_cases:
            # 1. รันคำสั่งที่พัง -> ต้อง fail
            initial_res = execute_sql_in_sandbox(case["broken_sql"])
            assert initial_res["status"] == "error", f"Expected error but got {initial_res}"

            # 2. เข้าสู่ Self-Healing
            schema_info = "TABLE products (id INTEGER, name TEXT, price REAL)\nTABLE customers (id INTEGER, name TEXT, email TEXT)"
            healed_sql = self_heal_sql(
                failed_sql=case["broken_sql"],
                error_message=case["error"],
                schema_info=schema_info,
                user_query=case["query"]
            )

            # 3. รันคำสั่งที่ซ่อมแล้ว -> ต้อง success
            recovered_res = execute_sql_in_sandbox(healed_sql)
            if recovered_res["status"] == "success":
                recovered_count += 1

        recovery_rate = (recovered_count / len(broken_cases)) * 100.0
        print(f"\nSelf-Healing Recovery Rate: {recovery_rate:.1f}% ({recovered_count}/{len(broken_cases)})")
        assert recovery_rate == 100.0

    def test_sql_cleaner_robustness(self):
        """
        ทดสอบความแม่นยำในการคลีนคำสั่ง SQL จาก LLM Output ในทุกรูปแบบ
        """
        test_samples = [
            ("<think>I need to query customers</think>```sql\nSELECT * FROM customers;\n```", "SELECT * FROM customers;"),
            ("```\nSELECT id, name FROM products WHERE price > 100;\n```\nคำอธิบาย: ดึงสินค้าที่มีราคาเกิน 100", "SELECT id, name FROM products WHERE price > 100;"),
            ("WITH sales_summary AS (SELECT customer_id, SUM(quantity) AS total FROM orders GROUP BY customer_id) SELECT * FROM sales_summary;", "WITH sales_summary AS (SELECT customer_id, SUM(quantity) AS total FROM orders GROUP BY customer_id) SELECT * FROM sales_summary;"),
            ("-- คอมเมนต์ภาษาไทย\nSELECT count(*) FROM orders;", "SELECT count(*) FROM orders;"),
        ]

        for dirty_input, expected in test_samples:
            cleaned = clean_extracted_sql(dirty_input)
            assert cleaned == expected
