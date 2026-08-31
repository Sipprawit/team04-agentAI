def _has_numeric_column(data: list) -> bool:
    """ตรวจสอบว่าในชุดข้อมูลมีคอลัมน์ที่เป็นตัวเลขอย่างน้อย 1 คอลัมน์หรือไม่"""
    if not data:
        return False
    first_row = data[0]
    for k, v in first_row.items():
        if isinstance(v, (int, float)):
            return True
        if isinstance(v, str):
            # ตรวจสอบตัวเลขในรูปแบบ string เช่น "12500.50" หรือ "1,000"
            clean = v.replace(",", "").strip()
            if clean and clean.replace(".", "", 1).isdigit():
                return True
    return False


def recommend_chart_type(data: list) -> str:
    """
    ระบบแนะนำการแสดงผลกราฟอัตโนมัติ (Auto-EDA System)
    วิเคราะห์โครงสร้างข้อมูลดิบเพื่อตัดสินใจว่าควรใช้กราฟประเภทใด:
    - 'none': หากไม่มีคอลัมน์ตัวเลข (เช่น รายชื่อสินค้า, รายชื่อลูกค้า) -> แสดงเป็นข้อความ/ตาราง
    - 'summary_card': หากมีแถวเดียวที่เป็นตัวเลขสรุป (เช่น ยอดรวม, จำนวนแถว)
    - 'line': หากมีคอลัมน์วันที่/เวลา + ตัวเลข
    - 'pie': หากเป็นข้อมูลสัดส่วน/เปอร์เซ็นต์ หรือ 3-6 หมวดหมู่
    - 'bar': หากเป็นข้อมูลเปรียบเทียบหมวดหมู่ 2-20 รายการ
    """
    if not data or len(data) == 0:
        return "none"

    # ถ้าไม่มีคอลัมน์ที่เป็นตัวเลขเลย ไม่ต้องสร้างกราฟ
    if not _has_numeric_column(data):
        return "none"

    first_row = data[0]
    keys = list(first_row.keys())

    # หากมีเพียง 1 แถว หรือผลลัพธ์เป็นค่าเดี่ยว (Scalar aggregation เช่น COUNT, SUM)
    if len(data) == 1:
        # ถ้ามีหลายคอลัมน์และเป็นตัวเลข อาจเป็น Summary Card
        return "summary_card"

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

    # เปรียบเทียบหมวดหมู่ 2-25 รายการที่มีตัวเลข -> Bar chart
    if 2 <= len(data) <= 25:
        return "bar"

    # ข้อมูลมากกว่า 25 รายการ หรือตารางขนาดใหญ่ -> ไม่บังคับกราฟ ให้เป็นตารางข้อมูล
    return "none"
