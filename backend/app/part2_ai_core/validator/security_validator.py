import re

def validate_sql_security(sql_query: str) -> dict:
    """
    ระบบตรวจสอบคำสั่งอันตราย (Security Validator)
    """
    query_upper = sql_query.upper().strip()
    
    # [NEW] 1. ดักจับและบล็อก SQL Comments เพื่อป้องกันช่องโหว่ SQL Injection
    if re.search(r'--|/\*|\*/', query_upper):
        return {
            "is_valid": False,
            "reason": "ไม่อนุญาตให้ใช้ Comment (--, /* */) ในคำสั่ง SQL เพื่อความปลอดภัย"
        }
    
    # [UPDATE] 2. เพิ่มคำสั่งอันตรายกลุ่ม PRAGMA, ATTACH, DETACH, VACUUM
    forbidden_keywords = [
        'DROP', 'DELETE', 'TRUNCATE', 'ALTER', 'UPDATE', 'INSERT', 
        'CREATE', 'REPLACE', 'GRANT', 'REVOKE',
        'PRAGMA', 'ATTACH', 'DETACH', 'VACUUM'
    ]
    
    for kw in forbidden_keywords:
        # ใช้ \b เพื่อเช็กเป็นคำๆ ป้องกันการบล็อกผิด เช่น ถ้าตารางชื่อ user_update
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