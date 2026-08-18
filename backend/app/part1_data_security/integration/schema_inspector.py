from sqlalchemy import text, inspect
from app.db.database import engine

def get_database_schema_info() -> str:
    """
    อ่านและบันทึกโครงสร้างข้อมูล (Schema Mapping System)
    ดึงตารางทั้งหมด คอลัมน์ และประเภทข้อมูล เพื่อส่งให้ AI อ่าน
    """
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        schema_text = []
        for table_name in tables:
            columns = inspector.get_columns(table_name)
            col_info = [f"{col['name']} ({col['type']})" for col in columns]
            schema_text.append(f"Table: {table_name}\nColumns: {', '.join(col_info)}")
            
        return "\n\n".join(schema_text)
    except Exception as e:
        return f"Error retrieving schema: {str(e)}"
