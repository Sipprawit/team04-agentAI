ID_PATTERNS = {
    "id", "_id", "ลำดับ", "code", "รหัส", "no", "num", "phone", "tel", "zip",
    "postcode", "key", "เลขที่", "ลำดับที่", "order_id", "customer_id", "product_id"
}

DATE_PATTERNS = {
    "year", "ปี", "พ.ศ.", "ค.ศ.", "month", "เดือน", "day", "วัน",
    "date", "วันที่", "time", "เวลา", "quarter", "ไตรมาส", "period", "period_of_inv"
}


def is_metric_column(col_name: str, sample_values: list = None) -> bool:
    """
    ตรวจสอบว่าคอลัมน์นี้เป็นตัวเลขเชิงปริมาณที่แท้จริง (Quantitative Metric) หรือไม่
    คัดกรอง ID, ลำดับ, รหัส, ปี, วันที่ ออกจากการเป็นแกน Y
    เพื่อป้องกันการนำตัวเลขที่ไม่ใช่ค่าสถิติมาพล็อตเป็นกราฟ
    """
    col_lower = col_name.lower().strip()

    # 1. เช็คชื่อคอลัมน์ที่เป็น ID, รหัส หรือลำดับ
    if col_lower in ID_PATTERNS or any(col_lower.endswith(p) for p in ["_id", "id", "_code", "_no"]):
        return False
    if any(p in col_lower for p in ["ลำดับ", "รหัส", "phone", "tel", "zipcode"]):
        return False

    # 2. เช็คชื่อคอลัมน์ที่เป็นมิติของเวลา (Year, Date, Month)
    if col_lower in DATE_PATTERNS:
        return False
    if col_lower in ["year", "ปี"] or any(p in col_lower for p in ["พ.ศ.", "ค.ศ."]):
        return False

    # 3. เช็คค่าตัวอย่าง หากค่าทั้งหมดมีลักษณะเป็นปี พ.ศ. หรือ ค.ศ.
    if sample_values:
        numeric_samples = []
        for s in sample_values:
            if isinstance(s, (int, float)):
                numeric_samples.append(s)
            elif isinstance(s, str):
                clean = s.replace(",", "").strip()
                try:
                    numeric_samples.append(float(clean))
                except ValueError:
                    pass
        if not numeric_samples:
            return False
        # ถ้าค่าตัวเลขทั้งหมดอยู่ในช่วงปี พ.ศ. (2450 - 2650) หรือ ค.ศ. (1900 - 2100) ถือเป็นมิติเวลา
        if len(numeric_samples) >= 1 and all(
            isinstance(v, (int, float)) and ((1900 <= v <= 2100) or (2450 <= v <= 2650))
            for v in numeric_samples
        ):
            return False

    return True


def _get_metric_columns(data: list) -> list:
    """ดึงรายชื่อคอลัมน์ที่เป็นตัวเลขเชิงปริมาณที่แท้จริงจากชุดข้อมูล"""
    if not data:
        return []
    first_row = data[0]
    metric_cols = []
    for col_name in first_row.keys():
        sample_vals = [row.get(col_name) for row in data[:10]]
        # เช็คว่ามีค่าตัวเลขหรือไม่
        has_number = any(
            isinstance(v, (int, float)) or (isinstance(v, str) and v.replace(",", "").strip().replace(".", "", 1).isdigit())
            for v in sample_vals if v is not None and v != ""
        )
        if has_number and is_metric_column(col_name, sample_vals):
            metric_cols.append(col_name)
    return metric_cols


def recommend_chart_type(data: list) -> str:
    """
    ระบบแนะนำการแสดงผลกราฟอัตโนมัติ (Auto-EDA System) ที่ฉลาดและแม่นยำ:
    - 'none': หากไม่มีคอลัมน์ตัวเลขเชิงปริมาณ (เช่น รายชื่อสินค้า, ตารางสรุปข้อความ, ข้อมูลเชิงคุณภาพ)
              ป้องกันการนำ ID หรือ ปี มาสร้างกราฟมั่ว
    - 'summary_card': หากมีแถวเดียวที่เป็นตัวเลขสรุป
    - 'line': หากมีคอลัมน์วันที่/เวลา/ปี + ตัวเลขสถิติต่อเนื่อง
    - 'pie': หากเป็นข้อมูลสัดส่วน/ร้อยละ หรือส่วนแบ่ง 3-8 หมวดหมู่
    - 'bar': หากเป็นการเปรียบเทียบหมวดหมู่ 2-25 รายการ
    """
    if not data or len(data) == 0:
        return "none"

    # ต้องมีคอลัมน์ตัวเลขเชิงสถิติที่แท้จริง (ไม่ใช่ ID หรือ ปี)
    metric_cols = _get_metric_columns(data)
    if not metric_cols:
        return "none"

    first_row = data[0]
    keys = list(first_row.keys())

    # หากมีเพียง 1 แถว -> Summary Card
    if len(data) == 1:
        return "summary_card"

    # ตรวจสอบว่ามีคอลัมน์วันที่/เวลา/ปี สำหรับแกน X หรือไม่
    has_date = any(
        'date' in k.lower() or 'time' in k.lower() or 'month' in k.lower() or 'year' in k.lower() or 'day' in k.lower()
        or 'วันที่' in k or 'เดือน' in k or 'ปี' in k or 'เวลา' in k or 'พ.ศ.' in k or 'ค.ศ.' in k
        for k in keys
    )
    if has_date:
        return "line"

    # ตรวจสอบถ้ามีคำว่า share, percentage, proportion, ratio, ร้อยละ, สัดส่วน -> แนะนำ Pie chart
    has_percentage = any(
        'percent' in k.lower() or 'share' in k.lower() or 'ratio' in k.lower() or 'proportion' in k.lower()
        or 'ร้อยละ' in k or 'เปอร์เซ็นต์' in k or 'สัดส่วน' in k
        for k in metric_cols
    )
    if has_percentage and 3 <= len(data) <= 8:
        return "pie"

    # เปรียบเทียบหมวดหมู่ 2-25 รายการที่มีตัวเลข -> Bar chart
    if 2 <= len(data) <= 25:
        return "bar"

    return "none"
