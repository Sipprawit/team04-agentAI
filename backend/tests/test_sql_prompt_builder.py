"""
Unit Tests สำหรับ SQL Prompt Builder (Part 2)
ทดสอบการสร้าง Prompt เพื่อส่งให้ AI แปลงภาษาธรรมชาติเป็น SQL
"""
import pytest
from app.part2_ai_core.translator.sql_prompt_builder import build_sql_prompt


class TestSQLPromptBuilder:
    def test_build_prompt_basic(self):
        prompt = build_sql_prompt("แจกแจงจำนวนรายการตามแต่ละหมวดหมู่ใน col_1")
        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert "แจกแจงจำนวนรายการตามแต่ละหมวดหมู่ใน col_1" in prompt
        assert "SQLite Database" in prompt

    def test_build_prompt_with_dict_history(self):
        history = [
            {"role": "user", "text": "มีข้อมูลอะไรบ้าง"},
            {"role": "assistant", "text": "พบข้อมูล 10 รายการ"},
        ]
        prompt = build_sql_prompt("สรุปยอดรวม", chat_history=history)
        assert "- user: มีข้อมูลอะไรบ้าง" in prompt
        assert "- assistant: พบข้อมูล 10 รายการ" in prompt
        assert "สรุปยอดรวม" in prompt

    def test_build_prompt_with_object_history(self):
        class DummyMsg:
            def __init__(self, role, content):
                self.role = role
                self.content = content

        history = [
            DummyMsg("user", "ขอดูยอดขาย"),
            DummyMsg("assistant", "นี่คือยอดขายปี 2558"),
        ]
        prompt = build_sql_prompt("ปี 2559 ล่ะ", chat_history=history)
        assert "- user: ขอดูยอดขาย" in prompt
        assert "- assistant: นี่คือยอดขายปี 2558" in prompt

    def test_build_prompt_contains_strict_rules(self):
        prompt = build_sql_prompt("แสดงข้อมูล")
        assert "ข้อบังคับอย่างเคร่งครัด" in prompt
        assert "SELECT" in prompt
