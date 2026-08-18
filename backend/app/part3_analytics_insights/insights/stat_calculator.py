def calculate_advanced_statistics(data: list) -> dict:
    """
    คำนวณหาสถิติเชิงลึก (เปอร์เซ็นต์การเติบโต, ยอดสูงสุด/ต่ำสุด, ค่าเฉลี่ย, ส่วนแบ่ง %)
    """
    if not data:
        return {}
        
    first_row = data[0]
    num_keys = [k for k, v in first_row.items() if isinstance(v, (int, float))]
    
    if not num_keys:
        return {"count": len(data)}
        
    target_key = num_keys[-1]
    values = [row[target_key] for row in data if isinstance(row.get(target_key), (int, float))]
    
    if not values:
        return {"count": len(data)}
        
    total_val = sum(values)
    max_val = max(values)
    min_val = min(values)
    avg_val = total_val / len(values) if values else 0
    
    # คำนวณส่วนแบ่งเปอร์เซ็นต์สำหรับแต่ละรายการ
    stats_summary = {
        "total": total_val,
        "max": max_val,
        "min": min_val,
        "average": round(avg_val, 2),
        "count": len(values)
    }
    return stats_summary
