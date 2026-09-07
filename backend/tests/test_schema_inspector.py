import pytest
from app.part1_data_security.integration.schema_inspector import (
    get_database_schema_info,
    get_schema_dict
)


class TestSchemaInspector:
    def test_get_database_schema_info(self):
        info = get_database_schema_info(exclude_system_tables=True)
        assert isinstance(info, str)
        # ตรวจสอบว่ามีข้อมูลตาราง customers หรือ products ใน schema info
        assert "customers" in info or "products" in info or "orders" in info
        # ต้องไม่มีตารางระบบ audit_logs หรือ chat_sessions เมื่อ exclude_system_tables=True
        assert "[ตาราง: audit_logs]" not in info
        assert "[ตาราง: chat_sessions]" not in info

    def test_get_schema_dict(self):
        schema = get_schema_dict()
        assert isinstance(schema, dict)
        # ตรวจสอบว่าคืนค่ารายละเอียดตารางถูกต้อง
        assert "customers" in schema or "products" in schema
        target_tbl = "customers" if "customers" in schema else list(schema.keys())[0]
        assert "columns" in schema[target_tbl]
        assert "foreign_keys" in schema[target_tbl]
        assert "row_count" in schema[target_tbl]
        assert isinstance(schema[target_tbl]["columns"], list)
