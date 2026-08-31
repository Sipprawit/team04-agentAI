import csv
import re
from sqlalchemy import text
from app.db.database import engine

# ============================================
# ข้อจำกัดด้านความปลอดภัย
# ============================================
MAX_FILE_SIZE_MB = 10
ALLOWED_EXTENSIONS = {".csv"}

# รายการ Encoding ที่รองรับ (เรียงตามลำดับความน่าจะเป็น)
# cp874 และ tis-620 เป็น Encoding ภาษาไทยที่ Microsoft Excel บน Windows ใช้เป็นค่าเริ่มต้น
ENCODINGS_TO_TRY = ["utf-8-sig", "cp874", "tis-620", "utf-8", "windows-1252", "latin-1"]

# SQL Reserved Words ที่ห้ามใช้เป็นชื่อตาราง/คอลัมน์
_SQL_RESERVED = {
    "select", "insert", "update", "delete", "drop", "create", "alter",
    "table", "from", "where", "and", "or", "not", "null", "index",
    "pragma", "attach", "detach", "vacuum", "grant", "revoke",
}


def sanitize_identifier(name: str) -> str:
    """
    Sanitize SQL identifier (table name / column name) to prevent SQL Injection.
    - รองรับทั้งตัวอักษรภาษาไทย (\u0E00-\u0E7F) และภาษาอังกฤษ (a-z, A-Z), ตัวเลข (0-9) และ underscore
    - ลบอักขระพิเศษอันตราย เช่น ;, ', ", --, /*, (), =, <, > ออกทั้งหมด
    - ถ้าขึ้นต้นด้วยตัวเลข จะเติม 'col_' นำหน้า
    - ถ้าตรงกับ SQL Reserved Word จะเติม 'col_' นำหน้า
    - ถ้าว่างเปล่า จะใช้ชื่อ 'unnamed'
    """
    clean = re.sub(r'[^\w\u0E00-\u0E7F]', '_', name.strip()).lower()
    # ลบ underscore ซ้ำ
    clean = re.sub(r'_+', '_', clean).strip('_')
    if not clean:
        clean = "unnamed"
    if clean[0].isdigit():
        clean = f"col_{clean}"
    if clean in _SQL_RESERVED:
        clean = f"col_{clean}"
    return clean


def _read_csv_with_fallback(file_path: str):
    """
    อ่านไฟล์ CSV โดยพยายามใช้ Encoding ต่างๆ (UTF-8, CP874 สำหรับภาษาไทยจาก Excel, TIS-620, Windows-1252)
    ป้องกัน UnicodeDecodeError เมื่อผู้ใช้อัปโหลดไฟล์ที่บันทึกจาก Excel บน Windows
    """
    last_error = None
    for enc in ENCODINGS_TO_TRY:
        try:
            with open(file_path, mode="r", encoding=enc, newline="") as f:
                reader = csv.reader(f)
                try:
                    raw_headers = next(reader)
                except StopIteration:
                    return [], [], enc
                rows = list(reader)
                return raw_headers, rows, enc
        except (UnicodeDecodeError, UnicodeError) as e:
            last_error = e
            continue
        except Exception as e:
            last_error = e
            break

    raise ValueError(f"ไม่สามารถถอดรหัสตัวอักษรของไฟล์ CSV ได้ (สาเหตุ: {last_error}) กรุณาบันทึกเป็น UTF-8 หรือ Windows Thai (CP874)")


def _detect_column_type(values: list) -> str:
    """
    ตรวจจับชนิดข้อมูลอัตโนมัติจากค่าตัวอย่างในคอลัมน์
    ลำดับการตรวจ: INTEGER -> REAL -> DATE -> TEXT
    """
    # กรองค่าว่างออก
    samples = [v.strip() for v in values if v and v.strip()]
    if not samples:
        return "TEXT"

    # ตรวจสอบ INTEGER
    is_int = True
    for s in samples:
        try:
            int(s.replace(",", ""))  # รองรับตัวเลขที่มีจุลภาค เช่น 1,000
        except ValueError:
            is_int = False
            break
    if is_int:
        return "INTEGER"

    # ตรวจสอบ REAL (float)
    is_float = True
    for s in samples:
        try:
            float(s.replace(",", ""))
        except ValueError:
            is_float = False
            break
    if is_float:
        return "REAL"

    # ตรวจสอบ DATE (รูปแบบ YYYY-MM-DD หรือ DD/MM/YYYY)
    date_pattern = re.compile(
        r"^\d{4}-\d{2}-\d{2}$|^\d{2}/\d{2}/\d{4}$|^\d{4}/\d{2}/\d{2}$"
    )
    is_date = all(date_pattern.match(s) for s in samples)
    if is_date:
        return "DATE"

    return "TEXT"


def validate_file_extension(filename: str) -> bool:
    """ตรวจสอบนามสกุลไฟล์ว่าอนุญาตหรือไม่"""
    if not filename:
        return False
    ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return ext in ALLOWED_EXTENSIONS


def validate_file_size(file_path: str) -> bool:
    """ตรวจสอบขนาดไฟล์ว่าไม่เกินขีดจำกัด"""
    import os
    size_mb = os.path.getsize(file_path) / (1024 * 1024)
    return size_mb <= MAX_FILE_SIZE_MB


def upload_csv_to_db(file_path: str, table_name: str) -> dict:
    """
    ระบบการนำเข้าข้อมูลและจัดการโครงสร้าง (Data Integration & Schema Mapping System)
    - อ่านไฟล์ CSV ด้วย Auto-Encoding Detection (รองรับทั้ง UTF-8 และ CP874 / TIS-620 ภาษาไทย)
    - ตรวจจับชนิดข้อมูลอัตโนมัติ (INTEGER, REAL, DATE, TEXT)
    - ป้องกัน SQL Injection ด้วยการ Sanitize ชื่อตารางและชื่อคอลัมน์ (รองรับภาษาไทย)
    - ตรวจสอบนามสกุลไฟล์และขนาดไฟล์
    - นำเข้าตารางในฐานข้อมูล SQLite
    """
    try:
        # --- ตรวจสอบนามสกุลไฟล์ ---
        if not validate_file_extension(file_path):
            return {
                "status": "error",
                "message": f"File type not allowed. Accepted: {', '.join(ALLOWED_EXTENSIONS)}"
            }

        # --- ตรวจสอบขนาดไฟล์ ---
        if not validate_file_size(file_path):
            return {
                "status": "error",
                "message": f"File too large. Max size: {MAX_FILE_SIZE_MB} MB"
            }

        table_clean = sanitize_identifier(table_name)

        # --- อ่าน CSV พร้อม Fallback Encoding อัตโนมัติ ---
        try:
            raw_headers, rows, used_encoding = _read_csv_with_fallback(file_path)
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }

        if not raw_headers:
            return {"status": "error", "message": "CSV file has no headers"}

        if not rows:
            return {"status": "error", "message": "CSV file has no data rows"}

        # --- Sanitize ชื่อคอลัมน์เพื่อป้องกัน SQL Injection ---
        headers = []
        seen = {}
        for h in raw_headers:
            clean = sanitize_identifier(h)
            # จัดการชื่อคอลัมน์ซ้ำ: เติมเลขต่อท้าย
            if clean in seen:
                seen[clean] += 1
                clean = f"{clean}_{seen[clean]}"
            else:
                seen[clean] = 0
            headers.append(clean)

        # --- ตรวจจับชนิดข้อมูลอัตโนมัติ (Data Type Detection) ---
        col_types = {}
        for col_idx, col_name in enumerate(headers):
            col_values = [row[col_idx] for row in rows if col_idx < len(row)]
            col_types[col_name] = _detect_column_type(col_values)

        col_defs = ", ".join([f'"{col}" {col_types[col]}' for col in headers])
        drop_sql = f'DROP TABLE IF EXISTS "{table_clean}";'
        create_sql = f'CREATE TABLE "{table_clean}" ({col_defs});'

        quoted_headers = [f'"{col}"' for col in headers]
        placeholders = ", ".join([f":param_{i}" for i in range(len(headers))])
        insert_sql = f'INSERT INTO "{table_clean}" ({", ".join(quoted_headers)}) VALUES ({placeholders});'

        # --- นำเข้าฐานข้อมูล ---
        inserted_count = 0
        with engine.connect() as conn:
            conn.execute(text(drop_sql))
            conn.execute(text(create_sql))
            for row in rows:
                if len(row) == len(headers):
                    row_dict = {}
                    for i, col in enumerate(headers):
                        val = row[i].strip() if row[i] else None
                        # แปลงค่าตามชนิดที่ตรวจจับได้
                        if val is not None and val != "":
                            # ลบคอมม่าออกจากตัวเลข
                            clean_num = val.replace(",", "")
                            if col_types[col] == "INTEGER":
                                try:
                                    val = int(clean_num)
                                except ValueError:
                                    pass
                            elif col_types[col] == "REAL":
                                try:
                                    val = float(clean_num)
                                except ValueError:
                                    pass
                        row_dict[f"param_{i}"] = val
                    conn.execute(text(insert_sql), row_dict)
                    inserted_count += 1
            conn.commit()

        return {
            "status": "success",
            "table_name": table_clean,
            "row_count": inserted_count,
            "columns": headers,
            "detected_types": col_types,
            "encoding": used_encoding,
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to import CSV: {str(e)}"
        }
