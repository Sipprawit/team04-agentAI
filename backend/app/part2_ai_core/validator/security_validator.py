import re

# คำสั่ง DDL / DML / Admin ที่ไม่อนุญาตใน Read-Only Text-to-SQL
FORBIDDEN_KEYWORDS = [
    r'\bDROP\b',
    r'\bDELETE\b',
    r'\bTRUNCATE\b',
    r'\bALTER\b',
    r'\bUPDATE\b',
    r'\bINSERT\b',
    r'\bCREATE\b',
    r'\bGRANT\b',
    r'\bREVOKE\b',
    r'\bPRAGMA\b',
    r'\bATTACH\b',
    r'\bDETACH\b',
    r'\bVACUUM\b',
    r'\bREPLACE\s+INTO\b',
]


def _strip_literals_and_comments(sql: str) -> str:
    """
    ตัด String literals ('...'), comments (-- ... และ /* ... */)
    ออกก่อนตรวจสอบคำสั่งอันตราย เพื่อป้องกัน false positive
    เช่น WHERE status = 'UPDATE' หรือ -- comment with DROP
    """
    # ลบ multi-line comments /* ... */
    clean = re.sub(r'/\*[\s\S]*?\*/', ' ', sql)
    # ลบ single-line comments -- ...
    clean = re.sub(r'--[^\r\n]*', ' ', clean)
    # ลบ single-quoted string literals '...' (รวม escaped '')
    clean = re.sub(r"'(?:''|[^'])*'", "''", clean)
    # ลบ double-quoted strings "..."
    clean = re.sub(r'"(?:""|[^"])*"', '""', clean)
    return clean


def validate_sql_security(sql_query: str) -> dict:
    """
    ระบบตรวจสอบคำสั่งอันตราย (Security Validator)
    ตรวจสอบว่าคำสั่ง SQL มีคำสั่งอันตราย เช่น DROP, DELETE, ALTER, UPDATE, INSERT หรือไม่
    รองรับการตัด String Literal และ Comment เพื่อป้องกัน False Positive
    """
    if not sql_query or not sql_query.strip():
        return {
            "is_valid": False,
            "reason": "คำสั่ง SQL ว่างเปล่า"
        }

    # ตัด string literals และ comments ออกก่อนตรวจคำสั่ง
    sanitized_sql = _strip_literals_and_comments(sql_query).strip()
    query_upper = sanitized_sql.upper()

    # ตรวจสอบคำสั่งอันตราย
    for pattern in FORBIDDEN_KEYWORDS:
        matched = re.search(pattern, query_upper)
        if matched:
            kw = matched.group().strip()
            return {
                "is_valid": False,
                "reason": f"คำสั่ง SQL มีคำสั่งอันตรายไม่อนุญาต ({kw}) อนุญาตเฉพาะคำสั่ง SELECT หรือ WITH เท่านั้น"
            }

    # ตรวจสอบว่าคำสั่งเริ่มต้นด้วย SELECT หรือ WITH (หลังตัด comments/whitespace)
    if not (query_upper.startswith("SELECT") or query_upper.startswith("WITH")):
        return {
            "is_valid": False,
            "reason": "คำสั่ง SQL ต้องขึ้นต้นด้วย SELECT หรือ WITH เท่านั้น"
        }

    # ตรวจสอบ Multi-statement execution (เช่น SELECT 1; DROP TABLE ...)
    # ถ้ามี semicolon คั่นกลางแล้วตามด้วยคำสั่งอื่น
    statements = [s.strip() for s in sanitized_sql.split(";") if s.strip()]
    if len(statements) > 1:
        return {
            "is_valid": False,
            "reason": "ไม่อนุญาตให้รันคำสั่ง SQL หลายคำสั่งพร้อมกัน (Multi-statement blocked)"
        }

    return {"is_valid": True, "reason": None}
