import csv
from sqlalchemy import text
from app.db.database import engine

def upload_csv_to_db(file_path: str, table_name: str) -> dict:
    """
    ระบบการนำเข้าข้อมูลและจัดการโครงสร้าง (Data Integration System)
    อ่านไฟล์ CSV ด้วย Python Standard CSV Library และนำเข้าตารางในฐานข้อมูล SQLite
    """
    try:
        table_clean = table_name.strip().replace(' ', '_').lower()
        
        with open(file_path, mode='r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            headers = [h.strip().replace(' ', '_').lower() for h in next(reader)]
            rows = list(reader)
            
        if not headers:
            return {"status": "error", "message": "ไฟล์ CSV ไม่มี Header"}
            
        col_defs = ", ".join([f"{col} TEXT" for col in headers])
        create_sql = f"CREATE TABLE IF NOT EXISTS {table_clean} ({col_defs});"
        
        placeholders = ", ".join([f":{col}" for col in headers])
        insert_sql = f"INSERT INTO {table_clean} ({', '.join(headers)}) VALUES ({placeholders});"
        
        with engine.connect() as conn:
            conn.execute(text(create_sql))
            for row in rows:
                if len(row) == len(headers):
                    row_dict = {headers[i]: row[i] for i in range(len(headers))}
                    conn.execute(text(insert_sql), row_dict)
            conn.commit()
            
        return {
            "status": "success",
            "table_name": table_clean,
            "row_count": len(rows),
            "columns": headers
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"ไม่สามารถนำเข้าไฟล์ CSV ได้: {str(e)}"
        }
