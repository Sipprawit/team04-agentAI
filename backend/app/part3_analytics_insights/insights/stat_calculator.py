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

    stats_summary = {
        "target_column": target_key,
        "total": round(total_val, 2),
        "max": round(max_val, 2),
        "min": round(min_val, 2),
        "average": round(avg_val, 2),
        "count": len(values)
    }
    return stats_summary
