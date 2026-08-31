def recommend_chart_type(data: list) -> str:
    """
    ระบบแนะนำการแสดงผลกราฟอัตโนมัติ (Auto-EDA System)
    วิเคราะห์โครงสร้างข้อมูลดิบเพื่อตัดสินใจว่าควรใช้กราฟประเภทใด (Bar, Line, Pie, Table หรือ Summary Card)
    """
    if not data or len(data) == 0:
        return "none"

    first_row = data[0]
    keys = list(first_row.keys())

    # หากมีเพียง 1 แถว หรือผลลัพธ์เป็นค่าเดี่ยว (Scalar aggregation)
    if len(data) == 1:
        return "summary_card"

    # หากมี 2 แถว
    if len(data) == 2:
        return "bar"

    # ตรวจสอบคอลัมน์วันที่/เวลา -> แนะนำ Line chart
    has_date = any(
        'date' in k.lower() or 'time' in k.lower() or 'month' in k.lower() or 'year' in k.lower() or 'day' in k.lower()
        for k in keys
    )
    if has_date:
        return "line"

    # ตรวจสอบถ้ามีคำว่า share, percentage, proportion, ratio หรือจำนวนแถว 3-6 แถว -> แนะนำ Pie chart
    has_percentage = any(
        'percent' in k.lower() or 'share' in k.lower() or 'ratio' in k.lower() or 'proportion' in k.lower()
        for k in keys
    )
    if has_percentage and 3 <= len(data) <= 8:
        return "pie"

    # เปรียบเทียบหมวดหมู่ 3-15 รายการ -> Bar chart
    if 3 <= len(data) <= 15:
        return "bar"

    # ข้อมูลมากกว่า 15 รายการ -> Bar chart (หรือ Table)
    return "bar"
