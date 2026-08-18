from app.part3_analytics_insights.recommender.eda_analyzer import recommend_chart_type

def format_visualization_payload(data: list) -> dict:
    """
    จัดเตรียมโครงสร้างข้อมูลแกน X-Y และประเภทกราฟสำหรับส่งไปให้ Frontend เรนเดอร์
    """
    chart_type = recommend_chart_type(data)
    
    if not data or chart_type in ["none", "summary_card"]:
        return {
            "recommended_chart": chart_type,
            "labels": [],
            "datasets": []
        }
        
    first_row = data[0]
    keys = list(first_row.keys())
    
    # แยกคอลัมน์ที่เป็น String/Date (Label) กับ คอลัมน์ที่เป็น ตัวเลข (Value)
    label_key = keys[0]
    value_key = keys[1] if len(keys) > 1 else keys[0]
    
    for k in keys:
        if isinstance(first_row[k], (int, float)):
            value_key = k
        elif isinstance(first_row[k], str):
            label_key = k
            
    labels = [str(row.get(label_key, '')) for row in data]
    values = [row.get(value_key, 0) for row in data]
    
    return {
        "recommended_chart": chart_type,
        "x_axis_key": label_key,
        "y_axis_key": value_key,
        "labels": labels,
        "values": values
    }
