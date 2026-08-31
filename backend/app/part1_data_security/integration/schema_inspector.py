from sqlalchemy import text, inspect
from app.db.database import engine

EXCLUDED_TABLES = {"audit_logs", "sqlite_sequence"}


def get_database_schema_info(exclude_system_tables: bool = True) -> str:
    """
    อ่านและบันทึกโครงสร้างข้อมูล (Schema Mapping System)
    ดึงตารางทั้งหมด คอลัมน์ ประเภทข้อมูล Foreign Keys และจำนวนแถว เพื่อส่งให้ AI อ่าน
    """
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()

        schema_text = []
        with engine.connect() as conn:
            for table_name in tables:
                if exclude_system_tables and table_name in EXCLUDED_TABLES:
                    continue

                # 1. คอลัมน์และชนิดข้อมูล
                columns = inspector.get_columns(table_name)
                col_info = [f"{col['name']} ({col['type']})" for col in columns]

                # 2. Foreign Keys (ความสัมพันธ์ระหว่างตาราง)
                fks = inspector.get_foreign_keys(table_name)
                fk_info = []
                for fk in fks:
                    constrained = ", ".join(fk.get("constrained_columns", []))
                    referred_tbl = fk.get("referred_table", "")
                    referred_cols = ", ".join(fk.get("referred_columns", []))
                    if constrained and referred_tbl:
                        fk_info.append(f"{constrained} -> {referred_tbl}({referred_cols})")

                # 3. จำนวนแถวคร่าวๆ
                try:
                    row_count = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar() or 0
                except Exception:
                    row_count = "N/A"

                table_str = f"Table: {table_name} (Rows: {row_count})\nColumns: {', '.join(col_info)}"
                if fk_info:
                    table_str += f"\nForeign Keys: {'; '.join(fk_info)}"

                schema_text.append(table_str)

        if not schema_text:
            return "No user tables found in database."

        return "\n\n".join(schema_text)
    except Exception as e:
        return f"Error retrieving schema: {str(e)}"


def get_schema_dict() -> dict:
    """
    ดึงโครงสร้างตารางในรูปแบบ Dictionary/JSON สำหรับส่งให้ Frontend หรือ API
    """
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        result = {}

        with engine.connect() as conn:
            for table_name in tables:
                columns = [
                    {"name": col["name"], "type": str(col["type"]), "nullable": col.get("nullable", True)}
                    for col in inspector.get_columns(table_name)
                ]
                fks = [
                    {
                        "constrained_columns": fk.get("constrained_columns", []),
                        "referred_table": fk.get("referred_table", ""),
                        "referred_columns": fk.get("referred_columns", []),
                    }
                    for fk in inspector.get_foreign_keys(table_name)
                ]
                try:
                    row_count = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar() or 0
                except Exception:
                    row_count = 0

                result[table_name] = {
                    "columns": columns,
                    "foreign_keys": fks,
                    "row_count": row_count,
                    "is_system": table_name in EXCLUDED_TABLES,
                }
        return result
    except Exception as e:
        return {"error": str(e)}
