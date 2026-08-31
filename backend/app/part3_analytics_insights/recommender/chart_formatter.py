from app.part3_analytics_insights.recommender.eda_analyzer import recommend_chart_type


def _to_number(val):
    """แปลงค่าเป็น int/float ถ้าทำได้"""
    if isinstance(val, (int, float)):
        return val
    if isinstance(val, str):
        try:
            if "." in val:
                return float(val)
            return int(val)
        except ValueError:
            return 0
    return 0


def format_visualization_payload(data: list) -> dict:
    """
    จัดเตรียมโครงสร้างข้อมูลแกน X-Y และประเภทกราฟสำหรับส่งไปให้ Frontend เรนเดอร์ด้วย Recharts
    """
    chart_type = recommend_chart_type(data)

    if not data or chart_type in ["none"]:
        return {
            "recommended_chart": "none",
            "labels": [],
            "values": [],
            "chart_data": [],
        }

    first_row = data[0]
    keys = list(first_row.keys())

    # กรณี Summary Card (ผลลัพธ์ 1 แถว)
    if chart_type == "summary_card" and len(data) == 1:
        # หาคอลัมน์ที่เป็นตัวเลข
        num_key = keys[0]
        label_key = keys[0]
        for k in keys:
            v = first_row[k]
            if isinstance(v, (int, float)) or (isinstance(v, str) and v.replace(".", "", 1).isdigit()):
                num_key = k
            else:
                label_key = k

        return {
            "recommended_chart": "summary_card",
            "title": label_key,
            "value": _to_number(first_row.get(num_key, 0)),
            "labels": [str(first_row.get(label_key, ""))],
            "values": [_to_number(first_row.get(num_key, 0))],
            "chart_data": [
                {"name": str(first_row.get(label_key, "")), "value": _to_number(first_row.get(num_key, 0))}
            ]
        }

    # แยกคอลัมน์ที่เป็น Label (String/Date) กับ Value (Number)
    label_key = keys[0]
    value_key = keys[1] if len(keys) > 1 else keys[0]

    for k in keys:
        v = first_row[k]
        if isinstance(v, (int, float)):
            value_key = k
        elif isinstance(v, str):
            if v.replace(".", "", 1).isdigit():
                value_key = k
            else:
                label_key = k

    labels = []
    values = []
    chart_data = []

    for row in data:
        raw_lbl = row.get(label_key, "")
        lbl_str = str(raw_lbl) if raw_lbl is not None else ""
        val_num = _to_number(row.get(value_key, 0))

        labels.append(lbl_str)
        values.append(val_num)
        chart_data.append({
            "name": lbl_str,
            "value": val_num,
            label_key: lbl_str,
            value_key: val_num
        })

    return {
        "recommended_chart": chart_type,
        "x_axis_key": label_key,
        "y_axis_key": value_key,
        "labels": labels,
        "values": values,
        "chart_data": chart_data,
    }
