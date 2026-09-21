import re
import logging
from typing import Optional
from app.part3_analytics_insights.recommender.eda_analyzer import recommend_chart_type, is_metric_column

logger = logging.getLogger("ChartFormatter")


def _to_number(val):
    """แปลงค่าเป็น int/float ถ้าทำได้ ปลอดภัยจาก None และ NA placeholders"""
    if val is None:
        return 0
    if isinstance(val, (int, float)):
        return val
    if isinstance(val, str):
        clean = val.replace(",", "").strip()
        if not clean or clean.lower() in {"-", "--", "—", "n/a", "na", "null", "none", "nil", "nan"}:
            return 0
        try:
            if "." in clean:
                return float(clean)
            return int(clean)
        except ValueError:
            try:
                return float(clean)
            except ValueError:
                return 0
    return 0


def _is_numeric(val) -> bool:
    """ตรวจสอบว่าค่าเป็นตัวเลขหรือไม่ ปลอดภัยจาก None และ NA placeholders"""
    if val is None:
        return False
    if isinstance(val, (int, float)):
        return True
    if isinstance(val, str):
        clean = val.replace(",", "").strip()
        if clean and clean.lower() not in {"-", "--", "—", "n/a", "na", "null", "none", "nil", "nan"}:
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


def _pick_primary_metric(metric_keys: list) -> str:

    """เลือกคอลัมน์ metric หลักโดยจัดลำดับความสำคัญ (มูลค่า/ยอดรวม > ราคา > ปริมาณ/จำนวน > สัดส่วน)"""
    if not metric_keys:
        return ""
    priority_ranks = [
        # Rank 1: ยอดรวม / มูลค่า / Total Value / Total Amount
        {"value", "total", "amount", "sales", "มูลค่า", "ยอด", "งบประมาณ", "รายได้", "รายจ่าย"},
        # Rank 2: ราคา / Price / ต้นทุน
        {"price", "cost", "ราคา"},
        # Rank 3: ปริมาณ / Quantity / Count / จำนวน
        {"quantity", "count", "volume", "จำนวน", "ปริมาณ", "รายการ"},
        # Rank 4: สัดส่วน / ร้อยละ / Percentage
        {"สัดส่วน", "ร้อยละ", "percent", "share", "ratio", "proportion"},
    ]
    for rank_set in priority_ranks:
        for mk in metric_keys:
            mk_lower = mk.lower()
            if mk_lower in rank_set or any(p in mk_lower for p in rank_set):
                return mk
    return metric_keys[0]


def format_visualization_payload(data: list, sql_query: Optional[str] = None) -> dict:
    """
    จัดเตรียมโครงสร้างข้อมูลแกน X-Y และประเภทกราฟสำหรับส่งไปให้ Frontend เรนเดอร์ด้วย Recharts
    - คัดกรอง ID, ลำดับ, ปี, วันที่ ออกจากแกน Y อย่างเคร่งครัด
    - หาก chart_data มาจาก SQL ที่ไม่มี GROUP BY (เป็น raw/itemized) และจำนวนแถวที่ได้ = LIMIT พอดี (เช่นได้ 50 แถวเป๊ะ)
      จะยิง SQL เพิ่มอีกครั้งแบบ COUNT/SUM ไม่มี LIMIT เพื่อเอาผลรวมจริงมาทำกราฟ แทนที่จะ aggregate จาก sample ที่ถูกตัด
      โดยตารางยังคงแสดงแถวตัวอย่างตามเดิม
    - ป้องกันการแสดงกราฟที่ผิดพลาดหรือสร้างความสับสน
    - หากเป็นข้อมูลเชิงคุณภาพ (Qualitative) ที่ไม่มีตัวเลข จะคืนค่า recommended_chart: 'none'
    """
    if not data or len(data) == 0:
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

    # กำหนดแกน X (Dimension): ให้ความสำคัญกับคอลัมน์ที่เป็นข้อความบรรยาย ไม่ใช่ ID หรือ รหัส
    clean_dim_keys = [
        k for k in dimension_keys
        if not any(p in k.lower() for p in ["id", "_id", "code", "รหัส", "ลำดับ", "เลขที่"])
    ]
    if not clean_dim_keys:
        clean_dim_keys = [k for k in dimension_keys if not k.lower().endswith("id") and k.lower() != "id"]
    if not clean_dim_keys:
        clean_dim_keys = dimension_keys if dimension_keys else [k for k in first_row.keys() if k not in metric_keys]

    # หากมีคอลัมน์หมวดหมู่/ข้อความ ให้เลือกหมวดหมู่ก่อนคอลัมน์วันที่/เวลา เพื่อให้ได้กราฟแจกแจงที่สื่อความหมาย
    categorical_dim_keys = [
        k for k in clean_dim_keys
        if not any(p in k.lower() for p in ["month", "year", "date", "เวลา", "วันที่", "เดือน", "ปี", "ไตรมาส", "quarter"])
    ]
    if categorical_dim_keys:
        x_axis_key = categorical_dim_keys[0]
    else:
        x_axis_key = clean_dim_keys[0] if clean_dim_keys else list(first_row.keys())[0]


    # กำหนดแกน Y (Metric): เลือกลำดับความสำคัญคอลัมน์ยอดนิยม (มูลค่า/ยอดรวม > ราคา > ปริมาณ/จำนวน > สัดส่วน)
    primary_y_key = _pick_primary_metric(metric_keys)

    # ==============================================================================
    # ทางเลือก A: ตรวจสอบว่าต้องยิง SQL เพิ่มแบบ COUNT/SUM โดยไม่มี LIMIT เพื่อหาผลรวมจริงหรือไม่
    # เงื่อนไข: SQL ไม่มี GROUP BY (เป็น raw/itemized) และจำนวนแถวที่ได้ = LIMIT พอดี
    # ==============================================================================
    data_for_chart = data
    is_full_aggregation = False
    aggregation_failed = False

    if sql_query and isinstance(sql_query, str):
        has_group_by = bool(re.search(r'\bGROUP\s+BY\b', sql_query, re.IGNORECASE))
        limit_match = re.search(r'\bLIMIT\s+(\d+)', sql_query, re.IGNORECASE)
        if not has_group_by and limit_match:
            limit_val = int(limit_match.group(1))
            if len(data) >= limit_val:
                try:
                    from app.part1_data_security.sandbox.sql_sandbox import execute_sql_in_sandbox
                    base_sql = re.sub(
                        r'\s+LIMIT\s+\d+(\s*,\s*\d+|\s+OFFSET\s+\d+)?\s*;?\s*$',
                        '',
                        sql_query.strip(),
                        flags=re.IGNORECASE
                    ).rstrip(';')

                    # รับประกันว่า primary_y_key จะอยู่ใน SELECT list เสมอ ป้องกัน no such column ใน ORDER BY
                    metrics_to_sum = [primary_y_key] + [mk for mk in metric_keys if mk != primary_y_key]
                    metric_sum_clauses = [f'SUM("{mk}") AS "{mk}"' for mk in metrics_to_sum[:3]]
                    metric_select_str = ", ".join(metric_sum_clauses)

                    if x_axis_key and x_axis_key in first_row:
                        chart_sql = (
                            f'SELECT "{x_axis_key}", {metric_select_str} '
                            f'FROM ({base_sql}) AS _sub '
                            f'GROUP BY "{x_axis_key}" '
                            f'ORDER BY "{primary_y_key}" DESC '
                            f'LIMIT 20;'
                        )
                    else:
                        chart_sql = (
                            f'SELECT {metric_select_str}, COUNT(*) AS "จำนวนรายการ" '
                            f'FROM ({base_sql}) AS _sub;'
                        )

                    chart_res = execute_sql_in_sandbox(chart_sql)
                    if chart_res.get("status") == "success" and chart_res.get("data"):
                        data_for_chart = chart_res["data"]
                        is_full_aggregation = True
                        logger.info(f"Chart full aggregation executed successfully: {len(data_for_chart)} rows")
                    else:
                        aggregation_failed = True
                        err_msg = chart_res.get("message", "Unknown sandbox error") if chart_res else "No response"
                        logger.warning(f"Chart full aggregation query returned error: {err_msg}")
                        data_for_chart = data
                except Exception as e:
                    aggregation_failed = True
                    logger.warning(f"Failed to execute chart full aggregation: {e}")
                    data_for_chart = data

    chart_type = recommend_chart_type(data_for_chart)

    if not data_for_chart or chart_type in ["none"]:
        res = {
            "recommended_chart": "none",
            "labels": [],
            "values": [],
            "chart_data": [],
        }
        if aggregation_failed:
            res["aggregation_failed"] = True
            res["truncation_label"] = "⚠️ คำนวณผลรวมทั้งหมดไม่สำเร็จ แสดงจากชุดข้อมูลตัวอย่างที่สืบค้นได้"
        return res

    # อัปเดตคอลัมน์ dimension / metric ตาม data_for_chart ที่ใช้จริง
    first_chart_row = data_for_chart[0]
    chart_dim_keys, chart_metric_keys = _find_columns(data_for_chart)
    if chart_dim_keys:
        clean_chart_dim = [
            k for k in chart_dim_keys
            if not any(p in k.lower() for p in ["id", "_id", "code", "รหัส", "ลำดับ", "เลขที่"])
        ]
        if not clean_chart_dim:
            clean_chart_dim = [k for k in chart_dim_keys if not k.lower().endswith("id") and k.lower() != "id"]
        if clean_chart_dim:
            cat_keys = [
                k for k in clean_chart_dim
                if not any(p in k.lower() for p in ["month", "year", "date", "เวลา", "วันที่", "เดือน", "ปี", "ไตรมาส", "quarter"])
            ]
            x_axis_key = cat_keys[0] if cat_keys else clean_chart_dim[0]
    if chart_metric_keys:
        primary_y_key = _pick_primary_metric(chart_metric_keys)


    # กรณี Summary Card (ผลลัพธ์ 1 แถว)
    if chart_type == "summary_card" and len(data_for_chart) == 1:
        res = {
            "recommended_chart": "summary_card",
            "title": primary_y_key,
            "value": _to_number(first_chart_row.get(primary_y_key, 0)),
            "labels": [str(first_chart_row.get(x_axis_key, ""))],
            "values": [_to_number(first_chart_row.get(primary_y_key, 0))],
            "chart_data": [
                {"name": str(first_chart_row.get(x_axis_key, "")), "value": _to_number(first_chart_row.get(primary_y_key, 0))}
            ]
        }
        if is_full_aggregation:
            res["is_full_aggregation"] = True
            res["truncation_label"] = "ผลรวมจริงจากข้อมูลทั้งหมดในระบบ (ไม่มี LIMIT)"
        if aggregation_failed:
            res["aggregation_failed"] = True
            res["truncation_label"] = "⚠️ คำนวณผลรวมอัตโนมัติไม่สำเร็จ แสดงจากชุดข้อมูลตัวอย่างที่สืบค้นได้"
        return res


    labels = []
    values = []
    chart_data = []

    for row in data_for_chart:
        raw_lbl = row.get(x_axis_key, "")
        lbl_str = str(raw_lbl) if raw_lbl is not None else ""
        primary_val = _to_number(row.get(primary_y_key, 0))

        labels.append(lbl_str)
        values.append(primary_val)

        entry = {"name": lbl_str, x_axis_key: lbl_str}

        # ใส่เฉพาะ genuine metric keys ลงใน chart_data
        for mk in (chart_metric_keys or metric_keys):
            entry[mk] = _to_number(row.get(mk, 0))

        # Backward compatibility
        entry["value"] = primary_val

        # ใส่ metadata เพิ่มเติมสำหรับ Tooltip
        for extra_key in ["unit", "period_of_inv", "cate_of_busi", "year"]:
            if extra_key in row:
                entry[extra_key] = row[extra_key]

        chart_data.append(entry)

    # บันทึกจำนวนรายการดั้งเดิมก่อนจัดทอน
    total_count = len(chart_data)
    is_truncated = False
    truncation_label = None

    # กรณี Pie Chart: กรองข้อมูลที่มีค่า <= 0 ออก เพราะ Pie Chart ไม่ควรมีชิ้นที่ไม่มีค่า
    if chart_type == "pie":
        pie_data = [d for d in chart_data if d.get("value", 0) > 0]
        # ถ้าหลังกรองเหลือน้อยกว่า 2 ชิ้น ไม่คุ้มแสดง Pie → ใช้ bar แทน
        if len(pie_data) < 2:
            chart_type = "bar"
        else:
            # หากมีมากกว่า 8 ชิ้น จัดกลุ่มชิ้นเล็กเป็น 'อื่นๆ' (Others) เพื่อความชัดเจนของ Pie Chart
            if len(pie_data) > 8:
                sorted_pie = sorted(pie_data, key=lambda x: x.get("value", 0), reverse=True)
                top_slices = sorted_pie[:7]
                other_slices = sorted_pie[7:]
                other_val = sum(s.get("value", 0) for s in other_slices)
                if other_val > 0:
                    other_entry = {
                        "name": "อื่นๆ",
                        x_axis_key: "อื่นๆ",
                        primary_y_key: other_val,
                        "value": other_val,
                    }
                    chart_data = top_slices + [other_entry]
                else:
                    chart_data = top_slices
                labels = [d["name"] for d in chart_data]
                values = [d["value"] for d in chart_data]
                is_truncated = True
                truncation_label = f"แสดง 7 หมวดหมู่อันดับแรก และรวม {len(other_slices)} รายการที่เหลือเป็น 'อื่นๆ'"
            else:
                chart_data = pie_data
                labels = [d["name"] for d in chart_data]
                values = [d["value"] for d in chart_data]

    # กรณี Bar / Line / Area Chart: หากข้อมูลเกิน 20 รายการ ให้ตัดทอนเฉพาะ 20 รายการแรกเพื่อไม่ให้กราฟแออัด
    MAX_CHART_ITEMS = 20
    if chart_type == "bar" and len(chart_data) > MAX_CHART_ITEMS:
        # สำหรับ Bar chart: เรียงตามมูลค่าจากมากไปน้อยเพื่อแสดง 20 อันดับแรกที่มีค่าสูงสุด
        chart_data = sorted(chart_data, key=lambda d: d.get("value", 0), reverse=True)[:MAX_CHART_ITEMS]
        labels = [d["name"] for d in chart_data]
        values = [d["value"] for d in chart_data]
        is_truncated = True
        truncation_label = f"แสดง {MAX_CHART_ITEMS} อันดับแรกที่มีมูลค่าสูงสุดจากทั้งหมด {total_count} รายการ (ดูข้อมูลครบถ้วนได้ในแท็บตารางข้อมูล)"
    elif chart_type in ("line", "area") and len(chart_data) > MAX_CHART_ITEMS:
        # สำหรับ Line / Area chart: คงลำดับเวลา/ลำดับเดิมไว้ตามเดิม (ห้าม sort by value เพราะจะทำลายลำดับเวลา)
        chart_data = chart_data[:MAX_CHART_ITEMS]
        labels = [d["name"] for d in chart_data]
        values = [d["value"] for d in chart_data]
        is_truncated = True
        truncation_label = f"แสดง {MAX_CHART_ITEMS} รายการแรกจากทั้งหมด {total_count} รายการ (ดูข้อมูลครบถ้วนได้ในแท็บตารางข้อมูล)"
    elif chart_type not in ("pie", "bar", "line", "area") and len(chart_data) > MAX_CHART_ITEMS:
        chart_data = chart_data[:MAX_CHART_ITEMS]
        labels = [d["name"] for d in chart_data]
        values = [d["value"] for d in chart_data]
        is_truncated = True
        truncation_label = f"แสดง {MAX_CHART_ITEMS} รายการแรกจากทั้งหมด {total_count} รายการ (ดูข้อมูลครบถ้วนได้ในแท็บตารางข้อมูล)"

    result = {
        "recommended_chart": chart_type,
        "x_axis_key": x_axis_key,
        "y_axis_key": primary_y_key,
        "labels": labels,
        "values": values,
        "chart_data": chart_data,
        "is_truncated": is_truncated,
        "total_count": total_count,
        "displayed_count": len(chart_data),
    }

    if is_full_aggregation:
        result["is_full_aggregation"] = True
        if not truncation_label:
            result["truncation_label"] = "กราฟสรุปผลรวมจริงจากข้อมูลทั้งหมดในระบบ (ตารางข้อมูลแสดงตัวอย่างรายการ)"

    if aggregation_failed:
        result["aggregation_failed"] = True
        result["truncation_label"] = "⚠️ คำนวณผลรวมทั้งหมดไม่สำเร็จ แสดงจากชุดข้อมูลตัวอย่างที่สืบค้นได้"

    if truncation_label:
        result["truncation_label"] = truncation_label


    active_metrics = chart_metric_keys or metric_keys
    if len(active_metrics) > 1:
        result["series_keys"] = active_metrics

    return result

