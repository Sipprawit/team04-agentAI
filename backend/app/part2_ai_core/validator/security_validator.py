import re

def validate_sql_security(sql_query: str) -> dict:
    """
    ระบบตรวจสอบคำสั่งอันตราย (Security Validator)
    ตรวจสอบว่าคำสั่ง SQL มีคำสั่งอันตราย เช่น DROP, DELETE, ALTER, UPDATE, INSERT หรือไม่
    """
    query_upper = sql_query.upper().strip()
    
    # คำสั่งอันตรายที่ไม่อนุญาต
    forbidden_keywords = ['DROP', 'DELETE', 'TRUNCATE', 'ALTER', 'UPDATE', 'INSERT', 'CREATE', 'REPLACE', 'GRANT', 'REVOKE']
    
    for kw in forbidden_keywords:
        if re.search(rf'\b{kw}\b', query_upper):
            return {
                "is_valid": False,
                "reason": f"คำสั่ง SQL มีคำสั่งอันตรายไม่อนุญาต ({kw}) อนุญาตเฉพาะคำสั่ง SELECT หรือ WITH เท่านั้น"
            }
            
    if not (query_upper.startswith("SELECT") or query_upper.startswith("WITH")):
        return {
            "is_valid": False,
            "reason": "คำสั่ง SQL ต้องขึ้นต้นด้วย SELECT หรือ WITH เท่านั้น"
        }
        
    return {"is_valid": True, "reason": None}
