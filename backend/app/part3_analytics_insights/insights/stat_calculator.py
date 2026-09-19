def calculate_advanced_statistics(data: list) -> dict:
    """
    คำนวณหาสถิติเชิงลึก (ยอดรวม, สูงสุด/ต่ำสุด, ค่าเฉลี่ย, จำนวน)
    ฉลาดในการเลือกคอลัมน์ตัวเลข: คัดกรอง id, _id, ลำดับ ออกจากการคำนวณ
    """
    if not data:
        return {}

    first_row = data[0]

    # คัดกรองคอลัมน์ ID ออกจากการคำนวณสถิติ
    id_patterns = {"id", "ลำดับ"}
    num_keys = []
    for k, v in first_row.items():
        if isinstance(v, (int, float)):
            k_lower = k.lower()
            is_id = k_lower == "id" or k_lower.endswith("_id") or k_lower in id_patterns
            if not is_id:
                num_keys.append(k)

    if not num_keys:
        return {"count": len(data)}

    # เลือกคอลัมน์ที่น่าจะเป็นค่าหลัก:
    # ถ้ามีคอลัมน์ชื่อ value, amount, total, price, ยอด, มูลค่า ให้เลือกเป็นหลัก
    priority_names = {"value", "amount", "total", "price", "quantity",
                      "ยอด", "มูลค่า", "จำนวน", "ราคา"}
    target_key = num_keys[0]
    for k in num_keys:
        if k.lower() in priority_names:
            target_key = k
            break

    values = [row[target_key] for row in data if isinstance(row.get(target_key), (int, float))]

    if not values:
        return {"count": len(data)}

    total_val = sum(values)
    max_val = max(values)
    min_val = min(values)
    avg_val = total_val / len(values) if values else 0

    # คำนวณมัธยฐาน (Median)
    sorted_vals = sorted(values)
    n = len(sorted_vals)
    if n % 2 == 1:
        median_val = sorted_vals[n // 2]
    else:
        median_val = (sorted_vals[n // 2 - 1] + sorted_vals[n // 2]) / 2.0

    # คำนวณส่วนเบี่ยงเบนมาตรฐาน (Standard Deviation: SD)
    if n >= 2:
        variance = sum((x - avg_val) ** 2 for x in values) / (n - 1)
        std_dev_val = variance ** 0.5
    else:
        std_dev_val = 0.0

    # ตรวจจับค่าผิดปกติ (Outlier / Anomaly Detection)
    anomalies = []
    if n >= 4 and std_dev_val > 0:
        # ค้นหาคอลัมน์ป้ายกำกับข้อความในแถวข้อมูล (เช่น ชื่อ, หมวด, รายการ)
        label_key = None
        for k, v in first_row.items():
            if isinstance(v, str) and k != target_key and not k.lower().endswith("id"):
                label_key = k
                break

        for row in data:
            val = row.get(target_key)
            if isinstance(val, (int, float)):
                is_high = (val - avg_val) >= (2.0 * std_dev_val) or (avg_val > 0 and val >= 3.0 * avg_val)
                is_low = (avg_val - val) >= (2.0 * std_dev_val) and (avg_val > 0 and val < avg_val / 3.0)
                if is_high or is_low:
                    label_name = str(row.get(label_key, "")) if label_key else ""
                    anomalies.append({
                        "column": target_key,
                        "label": label_name,
                        "value": round(val, 2),
                        "type": "high" if is_high else "low",
                        "ratio_to_avg": round(val / avg_val, 1) if avg_val > 0 else 0
                    })

        # คัดเฉพาะรายการที่มีความเบี่ยงเบนสูงสุด 3 อันดับแรก
        anomalies = sorted(anomalies, key=lambda a: abs(a["value"] - avg_val), reverse=True)[:3]

    stats_summary = {
        "target_column": target_key,
        "total": round(total_val, 2),
        "max": round(max_val, 2),
        "min": round(min_val, 2),
        "average": round(avg_val, 2),
        "median": round(median_val, 2),
        "std_dev": round(std_dev_val, 2),
        "anomalies": anomalies,
        "count": len(values)
    }
    return stats_summary
