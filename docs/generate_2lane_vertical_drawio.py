import xml.etree.ElementTree as ET
import os

def generate_vertical_drawio():
    mxfile = ET.Element("mxfile", {
        "host": "app.diagrams.net",
        "modified": "2026-09-22T22:30:00.000Z",
        "agent": "Antigravity AI Agent",
        "version": "24.0.0",
        "type": "device"
    })
    
    diagram = ET.SubElement(mxfile, "diagram", {
        "id": "team04-activity-diagram-vertical-2lanes",
        "name": "UML Activity Diagram (Vertical 2 Lanes)"
    })
    
    model = ET.SubElement(diagram, "mxGraphModel", {
        "dx": "1400",
        "dy": "900",
        "grid": "1",
        "gridSize": "10",
        "guides": "1",
        "tooltips": "1",
        "connect": "1",
        "arrows": "1",
        "fold": "1",
        "page": "1",
        "pageScale": "1",
        "pageWidth": "960",
        "pageHeight": "3200",
        "math": "0",
        "shadow": "0"
    })
    
    root = ET.SubElement(model, "root")
    
    # Base cells
    ET.SubElement(root, "mxCell", {"id": "0"})
    ET.SubElement(root, "mxCell", {"id": "1", "parent": "0"})
    
    # Total Diagram Bounds
    table_x = 40
    table_y = 40
    lane_user_w = 280
    lane_sys_w = 540
    total_w = lane_user_w + lane_sys_w
    total_h = 3060
    
    # Header & Swimlanes
    # Lane 1: ผู้ใช้งาน (User)
    lane_user = ET.SubElement(root, "mxCell", {
        "id": "lane_user",
        "value": "<b>ผู้ใช้งาน (User)</b>",
        "style": "swimlane;whiteSpace=wrap;html=1;startSize=40;swimlaneFillColor=#FFFFFF;fillColor=#FFFFFF;strokeColor=#000000;strokeWidth=1.5;fontColor=#000000;fontSize=14;align=center;",
        "vertex": "1",
        "parent": "1"
    })
    ET.SubElement(lane_user, "mxGeometry", {
        "x": str(table_x), "y": str(table_y), "width": str(lane_user_w), "height": str(total_h), "as": "geometry"
    })
    
    # Lane 2: ระบบ (System)
    lane_sys = ET.SubElement(root, "mxCell", {
        "id": "lane_sys",
        "value": "<b>ระบบ (System)</b>",
        "style": "swimlane;whiteSpace=wrap;html=1;startSize=40;swimlaneFillColor=#FFFFFF;fillColor=#FFFFFF;strokeColor=#000000;strokeWidth=1.5;fontColor=#000000;fontSize=14;align=center;",
        "vertex": "1",
        "parent": "1"
    })
    ET.SubElement(lane_sys, "mxGeometry", {
        "x": str(table_x + lane_user_w), "y": str(table_y), "width": str(lane_sys_w), "height": str(total_h), "as": "geometry"
    })

    # Common Styles based on reference image:
    # Yellow fill: #fff2cc, Reddish-brown border: #b85450, Reddish-brown edge: #b85450
    STYLE_ACT = "rounded=1;whiteSpace=wrap;html=1;arcSize=30;fillColor=#fff2cc;strokeColor=#b85450;strokeWidth=1.5;fontColor=#000000;fontSize=11;align=center;"
    STYLE_ACT_BOLD = "rounded=1;whiteSpace=wrap;html=1;arcSize=30;fillColor=#fff2cc;strokeColor=#b85450;strokeWidth=1.5;fontColor=#000000;fontSize=11;fontStyle=1;align=center;"
    STYLE_DIAMOND = "rhombus;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#b85450;strokeWidth=1.5;fontColor=#000000;fontSize=11;align=center;"
    STYLE_START = "ellipse;whiteSpace=wrap;html=1;aspect=fixed;fillColor=#000000;strokeColor=#b85450;strokeWidth=2;"
    STYLE_END = "ellipse;html=1;shape=endState;fillColor=#000000;strokeColor=#b85450;strokeWidth=2;"
    STYLE_SYNC = "rounded=1;whiteSpace=wrap;html=1;fillColor=#b85450;strokeColor=#b85450;"
    STYLE_BADGE = "rounded=1;whiteSpace=wrap;html=1;fillColor=#f8f9fa;strokeColor=#b85450;strokeWidth=1;fontColor=#b85450;fontSize=11;fontStyle=1;align=left;spacingLeft=10;"

    def add_node(nid, val, x, y, w, h, style):
        c = ET.SubElement(root, "mxCell", {
            "id": nid, "value": val, "style": style, "vertex": "1", "parent": "1"
        })
        ET.SubElement(c, "mxGeometry", {
            "x": str(x), "y": str(y), "width": str(w), "height": str(h), "as": "geometry"
        })
        return c

    def add_edge(eid, src, tgt, label="", points=None):
        edge = ET.SubElement(root, "mxCell", {
            "id": eid, "value": label,
            "style": "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#b85450;strokeWidth=1.5;fontColor=#b85450;fontSize=11;endArrow=classic;endFill=1;",
            "edge": "1", "parent": "1", "source": src, "target": tgt
        })
        geo = ET.SubElement(edge, "mxGeometry", {"relative": "1", "as": "geometry"})
        if points:
            pts = ET.SubElement(geo, "Array", {"as": "points"})
            for px, py in points:
                ET.SubElement(pts, "mxPoint", {"x": str(px), "y": str(py)})
        return edge

    # =========================================================================
    # 🟢 START NODE
    # =========================================================================
    add_node("start", "", 165, 95, 30, 30, STYLE_START)

    # =========================================================================
    # 📂 กิจกรรมที่ 1: การนำเข้าไฟล์และตรวจสอบความปลอดภัยข้อมูล
    # =========================================================================
    add_node("badge_1", "กิจกรรมที่ 1: การนำเข้าไฟล์และตรวจสอบความปลอดภัยข้อมูล", 60, 140, 780, 24, STYLE_BADGE)

    # 1. User
    add_node("u_1", "เปิดหน้าต่างนำเข้าข้อมูล<br/>และเลือกไฟล์ (.csv, .xlsx, .xls, .tsv, .txt)", 75, 180, 210, 55, STYLE_ACT)
    add_edge("e_start_u1", "start", "u_1")

    # 2. System: Frontend Check
    add_node("s_1_check", "ตรวจสอบขนาดไฟล์ (&le; 20MB)<br/>และนามสกุลไฟล์", 440, 180, 220, 55, STYLE_ACT)
    add_edge("e_u1_s1", "u_1", "s_1_check")

    # Decision 1
    add_node("d_1", "ไฟล์ถูกต้องหรือไม่?", 485, 260, 130, 70, STYLE_DIAMOND)
    add_edge("e_s1_d1", "s_1_check", "d_1")

    # Error path
    add_node("s_1_err", "แจ้งเตือนข้อผิดพลาดบนหน้าจอ<br/>(ขนาดไฟล์เกิน / ชนิดไฟล์ไม่รองรับ)", 670, 267, 180, 55, STYLE_ACT)
    add_node("end_1_err", "", 745, 345, 28, 28, STYLE_END)
    add_edge("e_d1_err", "d_1", "s_1_err", label="[no]")
    add_edge("e_err_end1", "s_1_err", "end_1_err")

    # 3. System: POST /upload-csv
    add_node("s_1_upload", "ส่งไฟล์ผ่าน REST API<br/>POST /upload-csv", 440, 360, 220, 50, STYLE_ACT)
    add_edge("e_d1_ok", "d_1", "s_1_upload", label="[yes]")

    # 4. System: Encoding
    add_node("s_1_enc", "ตรวจสอบ Encoding อัตโนมัติ<br/>(UTF-8, TIS-620, Windows-874)", 440, 435, 220, 50, STYLE_ACT)
    add_edge("e_up_enc", "s_1_upload", "s_1_enc")

    # 5. System: Type Inference
    add_node("s_1_type", "ทำ Type Inference ตรวจจับชนิดข้อมูล<br/>(Integer, Float, DateTime, Text)", 440, 510, 220, 50, STYLE_ACT)
    add_edge("e_enc_type", "s_1_enc", "s_1_type")

    # 6. System: PII & Sanitize
    add_node("s_1_pii", "ตรวจหา PII (บัตร ปชช., เบอร์โทร, อีเมล)<br/>และ Sanitize ตัดอักขระพิเศษชื่อคอลัมน์", 440, 585, 220, 55, STYLE_ACT)
    add_edge("e_type_pii", "s_1_type", "s_1_pii")

    # 7-8. System: SQLite Sandbox
    add_node("s_1_db", "สร้างตารางใหม่ หรือ Overwrite ตารางเดิม<br/>และบันทึกข้อมูลลง SQLite Sandbox", 440, 665, 220, 55, STYLE_ACT)
    add_edge("e_pii_db", "s_1_pii", "s_1_db")

    # 9-10. System: Return and Preview
    add_node("s_1_result", "แสดงผลลัพธ์นำเข้าสำเร็จ, พรีวิว 10 แถวแรก<br/>และตั้งชื่อห้องแชท 'ชุดข้อมูล: &lt;ชื่อตาราง&gt;'", 440, 745, 220, 60, STYLE_ACT)
    add_edge("e_db_res", "s_1_db", "s_1_result")

    # =========================================================================
    # 🧠 กิจกรรมที่ 2: การแปลงคำถามภาษาธรรมชาติเป็น SQL และการซ่อมแซมคำสั่ง
    # =========================================================================
    add_node("badge_2", "กิจกรรมที่ 2: การแปลงคำถามภาษาธรรมชาติเป็น SQL และการซ่อมแซมคำสั่งอัตโนมัติ", 60, 835, 780, 24, STYLE_BADGE)

    # 1. User Query
    add_node("u_2_ask", "ผู้ใช้พิมพ์คำถามภาษาไทย<br/>เช่น 'แสดงยอดขาย 5 อันดับแรกแยกตามภาค'", 75, 880, 210, 55, STYLE_ACT)
    add_edge("e_res_u2", "s_1_result", "u_2_ask", points=[(320, 775), (320, 907)])

    # 2. Frontend Validation & Send
    add_node("s_2_front", "Frontend ตรวจสอบคำถามไม่เป็นค่าว่าง<br/>แสดง Loading และส่ง POST /query (Context 5)", 440, 880, 220, 55, STYLE_ACT)
    add_edge("e_u2_s2", "u_2_ask", "s_2_front")

    # Decision 2: Rate Limit
    add_node("d_2_rate", "Rate Limit<br/>เกิน 120 req/m?", 485, 960, 130, 70, STYLE_DIAMOND)
    add_edge("e_s2_drate", "s_2_front", "d_2_rate")

    # Rate limit error
    add_node("s_2_rate_err", "ส่ง HTTP 429 Too Many Requests<br/>แจ้งผู้ใช้รอสักครู่ก่อนส่งใหม่", 670, 967, 180, 55, STYLE_ACT)
    add_node("end_2_rate", "", 745, 1045, 28, 28, STYLE_END)
    add_edge("e_drate_yes", "d_2_rate", "s_2_rate_err", label="[yes]")
    add_edge("e_rate_end", "s_2_rate_err", "end_2_rate")

    # 5. Schema Inspector
    add_node("s_2_schema", "Schema Inspector ดึง Schema คอลัมน์,<br/>Data Types และข้อมูลตัวอย่าง 3 แถว", 440, 1060, 220, 50, STYLE_ACT)
    add_edge("e_drate_no", "d_2_rate", "s_2_schema", label="[no]")

    # 6. Prompt Builder
    add_node("s_2_prompt", "Prompt Builder ผสาน Schema + คำถาม<br/>+ กฎความปลอดภัย + ตัวอย่าง Few-shot", 440, 1135, 220, 50, STYLE_ACT)
    add_edge("e_schema_prompt", "s_2_schema", "s_2_prompt")

    # 7. LLM Synthesis
    add_node("s_2_llm", "ส่ง Prompt ไปยัง LLaMA 3.3 70B (Groq)<br/>เพื่อสังเคราะห์คำสั่ง SQL", 440, 1210, 220, 50, STYLE_ACT)
    add_edge("e_prompt_llm", "s_2_prompt", "s_2_llm")

    # Decision 3: Security AST
    add_node("d_2_sec", "Security AST<br/>อนุญาตเฉพาะ SELECT?", 480, 1285, 140, 70, STYLE_DIAMOND)
    add_edge("e_llm_dsec", "s_2_llm", "d_2_sec")

    # Security error
    add_node("s_2_sec_err", "บล็อกคำสั่งอันตราย (DROP/DELETE ฯลฯ)<br/>แจ้งเตือนความปลอดภัย", 670, 1292, 180, 55, STYLE_ACT)
    add_node("end_2_sec", "", 745, 1370, 28, 28, STYLE_END)
    add_edge("e_dsec_no", "d_2_sec", "s_2_sec_err", label="[no]")
    add_edge("e_sec_end", "s_2_sec_err", "end_2_sec")

    # 9. Run in SQLite Sandbox
    add_node("s_2_sandbox", "นำ SQL รันใน SQLite Sandbox<br/>(WAL Mode, Read-Only, Timeout 5s)", 440, 1385, 220, 50, STYLE_ACT)
    add_edge("e_dsec_yes", "d_2_sec", "s_2_sandbox", label="[yes]")

    # Decision 4: Execution Error?
    add_node("d_2_err", "มีข้อผิดพลาดหรือไม่?<br/>(Syntax ผิด / รันไม่ผ่าน)", 480, 1460, 140, 70, STYLE_DIAMOND)
    add_edge("e_sand_derr", "s_2_sandbox", "d_2_err")

    # Decision 5: Retry < 2?
    add_node("d_2_retry", "รอบ Retry<br/>&lt; 2 ครั้ง?", 670, 1460, 110, 70, STYLE_DIAMOND)
    add_edge("e_derr_yes", "d_2_err", "d_2_retry", label="[yes]")

    # Self correction node
    add_node("s_2_correct", "Self-Correction Loop:<br/>นำ Error + SQL เดิม + Schema<br/>ป้อนกลับให้ AI สังเคราะห์ใหม่", 655, 1210, 180, 55, STYLE_ACT)
    add_edge("e_dretry_yes", "d_2_retry", "s_2_correct", label="[yes]")
    add_edge("e_correct_llm", "s_2_correct", "s_2_llm")

    # Retry fail message
    add_node("s_2_fail", "ส่งข้อความอธิบายความผิดพลาด<br/>อย่างสุภาพให้ผู้ใช้", 670, 1555, 180, 50, STYLE_ACT)
    add_node("end_2_fail", "", 745, 1630, 28, 28, STYLE_END)
    add_edge("e_dretry_no", "d_2_retry", "s_2_fail", label="[no]")
    add_edge("e_fail_end", "s_2_fail", "end_2_fail")

    # 10. Extract Rows
    add_node("s_2_success", "รัน SQL สำเร็จ: ดึงชุดข้อมูลผลลัพธ์ (Rows)<br/>ส่งต่อไปยังระบบวิเคราะห์สถิติ", 440, 1555, 220, 50, STYLE_ACT)
    add_edge("e_derr_no", "d_2_err", "s_2_success", label="[no]")

    # =========================================================================
    # 📊 กิจกรรมที่ 3: การวิเคราะห์ข้อมูลสถิติและการเลือกกราฟอัตโนมัติ
    # =========================================================================
    add_node("badge_3", "กิจกรรมที่ 3: การวิเคราะห์ข้อมูลสถิติและการเลือกกราฟอัตโนมัติ", 60, 1680, 780, 24, STYLE_BADGE)

    # Decision 6: Rows > 0?
    add_node("d_3_rows", "จำนวนแถวผลลัพธ์<br/>&gt; 0 หรือไม่?", 485, 1725, 130, 70, STYLE_DIAMOND)
    add_edge("e_succ_drows", "s_2_success", "d_3_rows")

    # Empty rows
    add_node("s_3_empty", "สรุปแจ้งว่าไม่พบข้อมูลที่ตรงกับเงื่อนไข<br/>(0 แถว) แจ้งเตือนผู้ใช้", 670, 1732, 180, 55, STYLE_ACT)
    add_node("end_3_empty", "", 745, 1810, 28, 28, STYLE_END)
    add_edge("e_drows_no", "d_3_rows", "s_3_empty", label="[no]")
    add_edge("e_empty_end", "s_3_empty", "end_3_empty")

    # 3. EDA Analyzer
    add_node("s_3_eda", "EDA Analyzer: แยกแยะคอลัมน์ตัวเลข (Metrics)<br/>และคอลัมน์หมวดหมู่/วันที่ (Dimensions)", 440, 1825, 220, 55, STYLE_ACT)
    add_edge("e_drows_yes", "d_3_rows", "s_3_eda", label="[yes]")

    # 4. Aggregation & Truncation
    add_node("s_3_trunc", "Smart Truncation: หากผลลัพธ์ &gt; 20 รายการ<br/>รวมกลุ่ม/ตัด 20 แถวแรก (is_truncated=true)", 440, 1905, 220, 55, STYLE_ACT)
    add_edge("e_eda_trunc", "s_3_eda", "s_3_trunc")

    # 5. Chart Recommender
    add_node("s_3_chart", "Chart Recommender: เลือกประเภทกราฟ<br/>(Bar, Line, Area, Pie หรือ Summary Card)", 440, 1985, 220, 55, STYLE_ACT)
    add_edge("e_trunc_chart", "s_3_trunc", "s_3_chart")

    # 6. Statistical Summarizer
    add_node("s_3_stats", "Statistical Summarizer: คำนวณสถิติเชิงปฏิบัติ<br/>(Total, Average, Max, Min, Count)", 440, 2065, 220, 50, STYLE_ACT)
    add_edge("e_chart_stats", "s_3_chart", "s_3_stats")

    # 7-8. Frontend Rendering
    add_node("s_3_render", "แสดงคำตอบ AI, คำสั่ง SQL, แผนภูมิ Interactive,<br/>ตารางข้อมูล, ปุ่ม CSV, ส่งออก PNG และปักหมุด", 440, 2140, 220, 65, STYLE_ACT)
    add_edge("e_stats_render", "s_3_stats", "s_3_render")

    # User Interaction
    add_node("u_3_interact", "ผู้ใช้ดูผลวิเคราะห์, สลับประเภทกราฟ,<br/>กดส่งออก PNG 2x หรือดาวน์โหลด CSV", 75, 2145, 210, 55, STYLE_ACT)
    add_edge("e_render_u3", "s_3_render", "u_3_interact")

    # =========================================================================
    # 📌 กิจกรรมที่ 4: การจัดการประวัติการสนทนาและการปักหมุดแดชบอร์ด
    # =========================================================================
    add_node("badge_4", "กิจกรรมที่ 4: การจัดการประวัติการสนทนาและการปักหมุดแดชบอร์ด", 60, 2235, 780, 24, STYLE_BADGE)

    # User Choice Decision
    add_node("d_4_choice", "ผู้ใช้เลือก<br/>การทำงานต่อ", 115, 2280, 130, 70, STYLE_DIAMOND)
    add_edge("e_u3_d4", "u_3_interact", "d_4_choice")

    # Case A: New chat / rename
    add_node("u_4_a", "กรณี A: พิมพ์ถามคำถามแรก<br/>ในห้องสนทนาใหม่", 75, 2375, 210, 50, STYLE_ACT)
    add_node("s_4_a", "Frontend generateSessionTitle() ตัดคำสร้อย<br/>ยิง PUT /sessions/{id} บันทึกชื่อลง SQLite", 440, 2375, 220, 50, STYLE_ACT)
    add_edge("e_d4_a", "d_4_choice", "u_4_a", label="[กรณี A]")
    add_edge("e_u4a_s4a", "u_4_a", "s_4_a")

    # Case B: Pinning
    add_node("u_4_b", "กรณี B: กดปุ่ม 📌 ปักหมุด<br/>บนการ์ดผลลัพธ์การวิเคราะห์", 75, 2450, 210, 50, STYLE_ACT)
    add_node("s_4_b", "ส่งข้อมูลไป POST /pinned-dashboard<br/>บันทึกลงตาราง pinned_items ใน SQLite", 440, 2450, 220, 50, STYLE_ACT)
    add_edge("e_d4_b", "d_4_choice", "u_4_b", label="[กรณี B]", points=[(55, 2315), (55, 2475)])
    add_edge("e_u4b_s4b", "u_4_b", "s_4_b")

    # Case C: View Dashboard
    add_node("u_4_c", "กรณี C: สลับไปยังแท็บ<br/>'แดชบอร์ดรวม' (Dynamic Dashboard)", 75, 2525, 210, 50, STYLE_ACT)
    add_node("s_4_c", "GET /pinned-dashboard ดึงการ์ดทั้งหมด<br/>จัดเรียง Grid, รองรับปลดหมุด และพิมพ์ PDF", 440, 2525, 220, 50, STYLE_ACT)
    add_edge("e_d4_c", "d_4_choice", "u_4_c", label="[กรณี C]", points=[(45, 2315), (45, 2550)])
    add_edge("e_u4c_s4c", "u_4_c", "s_4_c")

    # Sync Bar (Join)
    add_node("sync_bar", "", 75, 2605, 585, 8, STYLE_SYNC)
    add_edge("e_s4a_sync", "s_4_a", "sync_bar", points=[(550, 2435), (550, 2605)])
    add_edge("e_s4b_sync", "s_4_b", "sync_bar", points=[(550, 2510), (550, 2605)])
    add_edge("e_s4c_sync", "s_4_c", "sync_bar", points=[(550, 2585), (550, 2605)])

    # Final User Action
    add_node("u_final", "ผู้ใช้เข้าถึงข้อมูลสถิติ กราฟสรุปผล<br/>และรายงานแดชบอร์ดครบถ้วนสมบูรณ์", 75, 2640, 210, 55, STYLE_ACT)
    add_edge("e_sync_ufinal", "sync_bar", "u_final", points=[(180, 2613), (180, 2640)])

    # 🔴 Final End Node
    add_node("end_final", "", 165, 2725, 30, 30, STYLE_END)
    add_edge("e_ufinal_end", "u_final", "end_final")

    # Save to file
    out_path = "D:/Project/team04-agentAI/docs/activity_diagram_activities_1_to_4.drawio"
    tree = ET.ElementTree(mxfile)
    ET.indent(tree, space="  ", level=0)
    tree.write(out_path, encoding="utf-8", xml_declaration=True)
    print(f"Successfully generated: {out_path}")

    # Also overwrite system_activity_diagram_end_to_end.drawio
    e2e_path = "D:/Project/team04-agentAI/docs/system_activity_diagram_end_to_end.drawio"
    tree.write(e2e_path, encoding="utf-8", xml_declaration=True)
    print(f"Successfully updated: {e2e_path}")

if __name__ == "__main__":
    generate_vertical_drawio()
