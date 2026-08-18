def recommend_chart_type(data: list) -> str:
    """
    ระบบแนะนำการแสดงผลกราฟอัตโนมัติ (Auto-EDA System)
    วิเคราะห์โครงสร้างข้อมูลดิบเพื่อตัดสินใจว่าควรใช้กราฟประเภทใด (Bar, Line, Pie หรือ Table)
    """
    if not data or len(data) == 0:
        return "none"
        
    first_row = data[0]
    keys = list(first_row.keys())
    
    # หากมีเพียง 1 หรือ 2 แถว
    if len(data) <= 2:
        return "summary_card"
        
    # ตรวจสอบว่ามีคอลัมน์วันที่/เวลา หรือไม่
    has_date = any('date' in k.lower() or 'time' in k.lower() or 'month' in k.lower() for k in keys)
    if has_date:
        return "line"
        
    # ตรวจสอบถ้าเป็นข้อมูลเปรียบเทียบหมวดหมู่ 3-7 รายการ
    if 3 <= len(data) <= 8:
        return "bar"
        
    # หากมีรายการเยอะเกินไป แนะนำให้เป็น Bar หรือ Table
    return "bar"
