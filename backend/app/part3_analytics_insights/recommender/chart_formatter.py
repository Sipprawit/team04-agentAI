from app.part3_analytics_insights.recommender.eda_analyzer import recommend_chart_type, is_metric_column


def _to_number(val):
    """แปลงค่าเป็น int/float ถ้าทำได้"""
    if isinstance(val, (int, float)):
        return val
    if isinstance(val, str):
        try:
            clean = val.replace(",", "").strip()
            if "." in clean:
                return float(clean)
            return int(clean)
        except ValueError:
            return 0
    return 0


def _is_numeric(val) -> bool:
    """ตรวจสอบว่าค่าเป็นตัวเลขหรือไม่"""
    if isinstance(val, (int, float)):
        return True
    if isinstance(val, str):
        clean = val.replace(",", "").strip()
        if clean:
            try:
                float(clean)
                return True
            except ValueError:
                pass
    return False


def _find_columns(data: list) -> tuple:
    """
    แยกคอลัมน์ออกเป็น dimension_keys (แกน X: ข้อความ, วันที่, ปี)
    กับ metric_keys (แกน Y: ตัวเลขสถิติที่แท้จริง ไม่รวม ID หรือ ปี)
    """
    if not data:
        return [], []

    first_row = data[0]
    keys = list(first_row.keys())
    dimension_keys = []
    metric_keys = []

    for k in keys:
        sample_vals = [row.get(k) for row in data[:10]]
        has_num = any(_is_numeric(v) for v in sample_vals if v is not None and v != "")

        if has_num and is_metric_column(k, sample_vals):
            metric_keys.append(k)
        else:
            # คัดกรอง ID ออกจากแกน X ด้วยถ้ามีคอลัมน์ข้อความอื่นให้ใช้
            dimension_keys.append(k)

    return dimension_keys, metric_keys


def format_visualization_payload(data: list) -> dict:
    """
    จัดเตรียมโครงสร้างข้อมูลแกน X-Y และประเภทกราฟสำหรับส่งไปให้ Frontend เรนเดอร์ด้วย Recharts
    - คัดกรอง ID, ลำดับ, ปี, วันที่ ออกจากแกน Y อย่างเคร่งครัด
    - ป้องกันการแสดงกราฟที่ผิดพลาดหรือสร้างความสับสน
    - หากเป็นข้อมูลเชิงคุณภาพ (Qualitative) ที่ไม่มีตัวเลข จะคืนค่า recommended_chart: 'none'
    """
    chart_type = recommend_chart_type(data)

    if not data or chart_type in ["none"]:
        return {
            "recommended_chart": "none",
            "labels": [],
            "values": [],
            "chart_data": [],
        }

    dimension_keys, metric_keys = _find_columns(data)

    # หากไม่มีคอลัมน์ตัวเลขที่ถูกต้อง ไม่ต้องแสดงกราฟ
    if not metric_keys:
        return {
            "recommended_chart": "none",
            "labels": [],
            "values": [],
            "chart_data": [],
        }

    first_row = data[0]

    # กำหนดแกน X (Dimension): ให้ความสำคัญกับคอลัมน์ที่ไม่ใช่ ID
    clean_dim_keys = [k for k in dimension_keys if not k.lower().endswith("id") and k.lower() != "id"]
    if not clean_dim_keys:
        clean_dim_keys = dimension_keys if dimension_keys else list(first_row.keys())

    x_axis_key = clean_dim_keys[0] if clean_dim_keys else list(first_row.keys())[0]

    # กำหนดแกน Y (Metric): ลำดับความสำคัญคอลัมน์ยอดนิยม (value, total, price, etc.)
    priority_metrics = {"value", "total", "amount", "sales", "price", "quantity", "count", "ยอด", "มูลค่า", "จำนวน", "สัดส่วน", "ร้อยละ"}
    primary_y_key = metric_keys[0]
    for mk in metric_keys:
        if mk.lower() in priority_metrics or any(p in mk.lower() for p in priority_metrics):
            primary_y_key = mk
            break

    # กรณี Summary Card (ผลลัพธ์ 1 แถว)
    if chart_type == "summary_card" and len(data) == 1:
        return {
            "recommended_chart": "summary_card",
            "title": primary_y_key,
            "value": _to_number(first_row.get(primary_y_key, 0)),
            "labels": [str(first_row.get(x_axis_key, ""))],
            "values": [_to_number(first_row.get(primary_y_key, 0))],
            "chart_data": [
                {"name": str(first_row.get(x_axis_key, "")), "value": _to_number(first_row.get(primary_y_key, 0))}
            ]
        }

    labels = []
    values = []
    chart_data = []

    for row in data:
        raw_lbl = row.get(x_axis_key, "")
        lbl_str = str(raw_lbl) if raw_lbl is not None else ""
        primary_val = _to_number(row.get(primary_y_key, 0))

        labels.append(lbl_str)
        values.append(primary_val)

        entry = {"name": lbl_str, x_axis_key: lbl_str}

        # ใส่เฉพาะ genuine metric keys ลงใน chart_data
        for mk in metric_keys:
            entry[mk] = _to_number(row.get(mk, 0))

        # Backward compatibility
        entry["value"] = primary_val

        # ใส่ metadata เพิ่มเติมสำหรับ Tooltip
        for extra_key in ["unit", "period_of_inv", "cate_of_busi", "year"]:
            if extra_key in row:
                entry[extra_key] = row[extra_key]

        chart_data.append(entry)

    # กรณี Pie Chart: กรองข้อมูลที่มีค่า <= 0 ออก เพราะ Pie Chart ไม่ควรมีชิ้นที่ไม่มีค่า
    if chart_type == "pie":
        pie_data = [d for d in chart_data if d.get("value", 0) > 0]
        pie_labels = [labels[i] for i, v in enumerate(values) if v > 0]
        pie_values = [v for v in values if v > 0]
        # ถ้าหลังกรองเหลือน้อยกว่า 2 ชิ้น ไม่คุ้มแสดง Pie → ใช้ bar แทน
        if len(pie_data) < 2:
            chart_type = "bar"
        else:
            chart_data = pie_data
            labels = pie_labels
            values = pie_values

    result = {
        "recommended_chart": chart_type,
        "x_axis_key": x_axis_key,
        "y_axis_key": primary_y_key,
        "labels": labels,
        "values": values,
        "chart_data": chart_data,
    }

    if len(metric_keys) > 1:
        result["series_keys"] = metric_keys

    return result
