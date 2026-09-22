import xml.etree.ElementTree as ET
import html

def build_drawio():
    mxfile = ET.Element("mxfile", {
        "host": "app.diagrams.net",
        "modified": "2026-09-22T21:30:00.000Z",
        "agent": "Antigravity AI Agent",
        "version": "24.0.0",
        "type": "device"
    })
    
    diagram = ET.SubElement(mxfile, "diagram", {
        "id": "team04-activity-diagram",
        "name": "End-to-End System Activity Diagram"
    })
    
    model = ET.SubElement(diagram, "mxGraphModel", {
        "dx": "1422",
        "dy": "762",
        "grid": "1",
        "gridSize": "10",
        "guides": "1",
        "tooltips": "1",
        "connect": "1",
        "arrows": "1",
        "fold": "1",
        "page": "1",
        "pageScale": "1",
        "pageWidth": "1480",
        "pageHeight": "3700",
        "math": "0",
        "shadow": "1"
    })
    
    root = ET.SubElement(model, "root")
    
    # Base cells 0 and 1
    ET.SubElement(root, "mxCell", {"id": "0"})
    ET.SubElement(root, "mxCell", {"id": "1", "parent": "0"})
    
    # Title Header Block
    title_cell = ET.SubElement(root, "mxCell", {
        "id": "title_banner",
        "value": "&lt;b&gt;&lt;font style='font-size: 16px;'&gt;แผนภาพกิจกรรมการทำงานของระบบแบบครบวงจร (End-to-End UML Activity Diagram)&lt;/font&gt;&lt;/b&gt;&lt;br&gt;&lt;font style='font-size: 12px; color: #555555;'&gt;โครงงานระบบผู้ช่วยสืบค้นและวิเคราะห์ข้อมูลอัจฉริยะ (Text-to-SQL AI Agent System - Team 04)&lt;/font&gt;",
        "style": "rounded=1;whiteSpace=wrap;html=1;fillColor=#F8F9F9;strokeColor=#BDC3C7;strokeWidth=1.5;align=center;shadow=1;",
        "vertex": "1",
        "parent": "1"
    })
    ET.SubElement(title_cell, "mxGeometry", {
        "x": "40", "y": "20", "width": "1400", "height": "50", "as": "geometry"
    })
    
    # Swimlane Pool
    pool = ET.SubElement(root, "mxCell", {
        "id": "pool",
        "value": "ระบบผู้ช่วยวิเคราะห์ข้อมูลอัจฉริยะ (Text-to-SQL AI Agent System)",
        "style": "swimlane;html=1;childLayout=stackLayout;resizeParent=1;resizeParentMax=0;startSize=30;horizontal=0;horizontalStack=1;fillColor=#1A252F;fontColor=#FFFFFF;fontSize=14;fontStyle=1;strokeColor=#2C3E50;",
        "vertex": "1",
        "parent": "1"
    })
    ET.SubElement(pool, "mxGeometry", {
        "x": "40", "y": "80", "width": "1400", "height": "3580", "as": "geometry"
    })
    
    # 4 Lanes
    lanes = [
        ("lane_user", "👤 ผู้ใช้งาน (User)", 280, "#EBF5FB", "#2980B9"),
        ("lane_front", "💻 ส่วนหน้าบ้าน (Frontend: React UI)", 340, "#E8F8F5", "#16A085"),
        ("lane_back", "⚙️ ระบบหลังบ้าน & AI (FastAPI / Agent / Security)", 480, "#FEF9E7", "#D4AC0D"),
        ("lane_db", "🗄️ สภาพแวดล้อมฐานข้อมูล (SQLite Sandbox)", 300, "#F5EEF8", "#8E44AD"),
    ]
    
    for lid, lname, lwidth, lbg, lstroke in lanes:
        lane = ET.SubElement(root, "mxCell", {
            "id": lid,
            "value": f"&lt;b&gt;{lname}&lt;/b&gt;",
            "style": f"swimlane;html=1;startSize=30;fillColor={lbg};strokeColor={lstroke};fontSize=12;fontStyle=1;strokeWidth=1.5;",
            "vertex": "1",
            "parent": "pool"
        })
        ET.SubElement(lane, "mxGeometry", {
            "x": "0", "y": "0", "width": str(lwidth), "height": "3580", "as": "geometry"
        })

    # Helper function to add nodes (relative to parent lane)
    def add_node(nid, parent_lane, val, x, y, w, h, style):
        cell = ET.SubElement(root, "mxCell", {
            "id": nid,
            "value": val,
            "style": style,
            "vertex": "1",
            "parent": parent_lane
        })
        ET.SubElement(cell, "mxGeometry", {
            "x": str(x), "y": str(y), "width": str(w), "height": str(h), "as": "geometry"
        })
        return cell

    def add_edge(eid, src, tgt, label="", exitX=None, exitY=None, entryX=None, entryY=None, is_red=False):
        style = "edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;fontSize=10;"
        if is_red:
            style += "strokeColor=#E74C3C;strokeWidth=2;fontColor=#C0392B;"
        else:
            style += "strokeColor=#2C3E50;strokeWidth=1.5;fontColor=#2C3E50;"
        if exitX is not None:
            style += f"exitX={exitX};exitY={exitY};exitDx=0;exitDy=0;"
        if entryX is not None:
            style += f"entryX={entryX};entryY={entryY};entryDx=0;entryDy=0;"
            
        edge = ET.SubElement(root, "mxCell", {
            "id": eid,
            "value": label,
            "style": style,
            "edge": "1",
            "source": src,
            "target": tgt,
            "parent": "1"
        })
        ET.SubElement(edge, "mxGeometry", {"relative": "1", "as": "geometry"})
        return edge

    # Style constants
    S_ACTION = "rounded=1;whiteSpace=wrap;html=1;arcSize=14;fillColor=#FFFFFF;strokeColor=#34495E;strokeWidth=1.5;shadow=1;fontSize=11;align=center;"
    S_ACTION_FRONT = "rounded=1;whiteSpace=wrap;html=1;arcSize=14;fillColor=#E8F6F3;strokeColor=#16A085;strokeWidth=1.5;shadow=1;fontSize=11;align=center;"
    S_ACTION_BACK = "rounded=1;whiteSpace=wrap;html=1;arcSize=14;fillColor=#FEFDE8;strokeColor=#B7950B;strokeWidth=1.5;shadow=1;fontSize=11;align=center;"
    S_ACTION_DB = "rounded=1;whiteSpace=wrap;html=1;arcSize=14;fillColor=#F4ECF7;strokeColor=#7D3C98;strokeWidth=1.5;shadow=1;fontSize=11;align=center;"
    S_DECISION = "rhombus;whiteSpace=wrap;html=1;fillColor=#FFF2CC;strokeColor=#D6B656;strokeWidth=1.5;fontSize=10;fontStyle=1;shadow=1;"
    S_START = "ellipse;whiteSpace=wrap;html=1;aspect=fixed;fillColor=#2ECC71;strokeColor=#27AE60;strokeWidth=2;shadow=1;"
    S_END = "ellipse;shape=doubleEllipse;whiteSpace=wrap;html=1;aspect=fixed;fillColor=#E74C3C;strokeColor=#C0392B;strokeWidth=2;shadow=1;"
    S_BANNER = "rounded=1;whiteSpace=wrap;html=1;fillColor=#2C3E50;fontColor=#FFFFFF;strokeColor=none;fontSize=11;fontStyle=1;align=center;"
    S_TRANS = "rounded=1;whiteSpace=wrap;html=1;fillColor=#EAEDED;strokeColor=#95A5A6;strokeWidth=1;fontSize=10;fontStyle=2;align=center;"

    # =========================================================================
    # กิจกรรมที่ 1: การนำเข้าไฟล์และตรวจสอบความปลอดภัยข้อมูล (Data Ingestion)
    # =========================================================================
    add_node("ban_act1", "lane_back", "&lt;b&gt;กิจกรรมที่ 1: การนำเข้าไฟล์และตรวจสอบความปลอดภัยข้อมูล (Data Ingestion &amp; Security Validation)&lt;/b&gt;", 10, 45, 460, 26, S_BANNER)

    add_node("start_1", "lane_user", "", 125, 80, 30, 30, S_START)
    add_node("act1_1", "lane_user", "&lt;b&gt;1. เลือกไฟล์ข้อมูล&lt;/b&gt;&lt;br&gt;กดปุ่มนำเข้าและเลือกไฟล์&lt;br&gt;(.csv, .xlsx, .xls, .tsv, .txt)", 40, 130, 200, 55, S_ACTION)
    add_edge("e1_0", "start_1", "act1_1")

    add_node("act1_2", "lane_front", "&lt;b&gt;2. ตรวจสอบไฟล์เบื้องต้น&lt;/b&gt;&lt;br&gt;ขนาดไฟล์ (&amp;le; 20MB)&lt;br&gt;และนามสกุลไฟล์ที่รองรับ", 70, 130, 200, 55, S_ACTION_FRONT)
    add_edge("e1_1", "act1_1", "act1_2")

    add_node("dec1_1", "lane_front", "ไฟล์ถูกต้อง&lt;br&gt;ตามเกณฑ์?", 110, 215, 120, 65, S_DECISION)
    add_edge("e1_2", "act1_2", "dec1_1")

    add_node("act1_err", "lane_front", "&lt;b&gt;แจ้งเตือนข้อผิดพลาด&lt;/b&gt;&lt;br&gt;ไฟล์เกินขนาด / นามสกุลผิด", 20, 305, 140, 45, "rounded=1;whiteSpace=wrap;html=1;fillColor=#FDEDEC;strokeColor=#E74C3C;strokeWidth=1.5;fontSize=10;")
    add_node("end_1a", "lane_front", "", 75, 375, 30, 30, S_END)
    add_edge("e1_err1", "dec1_1", "act1_err", "[ไม่ถูกต้อง]", exitX=0, exitY=0.5, entryX=0.5, entryY=0, is_red=True)
    add_edge("e1_err2", "act1_err", "end_1a", "", exitX=0.5, exitY=1, entryX=0.5, entryY=0, is_red=True)

    add_node("act1_req", "lane_front", "&lt;b&gt;ส่งคำขอ API&lt;/b&gt;&lt;br&gt;POST /upload-csv (Multipart)", 180, 305, 150, 45, S_ACTION_FRONT)
    add_edge("e1_ok", "dec1_1", "act1_req", "[ถูกต้อง]", exitX=1, exitY=0.5, entryX=0.5, entryY=0)

    add_node("act1_3", "lane_back", "&lt;b&gt;3. ตรวจจับ Encoding อัตโนมัติ&lt;/b&gt;&lt;br&gt;UTF-8, TIS-620, Windows-874", 115, 305, 250, 45, S_ACTION_BACK)
    add_edge("e1_3", "act1_req", "act1_3")

    add_node("act1_4", "lane_back", "&lt;b&gt;4. Type Inference&lt;/b&gt;&lt;br&gt;จำแนกประเภทข้อมูลอัตโนมัติ&lt;br&gt;(Integer, Float, DateTime, Text)", 115, 375, 250, 50, S_ACTION_BACK)
    add_edge("e1_4", "act1_3", "act1_4")

    add_node("act1_5", "lane_back", "&lt;b&gt;5. PII Detection (Regex)&lt;/b&gt;&lt;br&gt;ตรวจหาบัตร ปชช. 13 หลัก, เบอร์โทร,&lt;br&gt;อีเมล, และเลขบัตรเครดิต", 115, 450, 250, 55, S_ACTION_BACK)
    add_edge("e1_5", "act1_4", "act1_5")

    add_node("act1_6", "lane_back", "&lt;b&gt;6. Sanitize Column Names&lt;/b&gt;&lt;br&gt;จัดระเบียบและตัดอักขระพิเศษในชื่อคอลัมน์", 115, 530, 250, 45, S_ACTION_BACK)
    add_edge("e1_6", "act1_5", "act1_6")

    add_node("act1_7", "lane_db", "&lt;b&gt;7. DDL Operation&lt;/b&gt;&lt;br&gt;สร้างตารางใหม่ หรือ Overwrite&lt;br&gt;ทับตารางเดิม (DROP IF EXISTS)", 40, 530, 220, 50, S_ACTION_DB)
    add_edge("e1_7", "act1_6", "act1_7")

    add_node("act1_8", "lane_db", "&lt;b&gt;8. Insert Batch Data&lt;/b&gt;&lt;br&gt;บันทึกข้อมูลทุกแถวลงในตาราง SQLite&lt;br&gt;(เปิด WAL Mode ปลอดภัย)", 40, 605, 220, 50, S_ACTION_DB)
    add_edge("e1_8", "act1_7", "act1_8")

    add_node("act1_9", "lane_back", "&lt;b&gt;9. รวบรวมและส่งผลลัพธ์&lt;/b&gt;&lt;br&gt;ส่ง Response: table_name, row_count,&lt;br&gt;schema, pii_warnings", 115, 605, 250, 50, S_ACTION_BACK)
    add_edge("e1_9", "act1_8", "act1_9")

    add_node("act1_10", "lane_front", "&lt;b&gt;10. แสดงผลสำเร็จ&lt;/b&gt;&lt;br&gt;แสดงพรีวิว 10 แถวแรก, แจ้งเตือน PII,&lt;br&gt;และตั้งชื่อห้อง: &lt;i&gt;'ชุดข้อมูล: &amp;lt;table&amp;gt;'&lt;/i&gt;", 50, 600, 240, 60, S_ACTION_FRONT)
    add_edge("e1_10", "act1_9", "act1_10")

    add_node("trans_1_2", "lane_front", "&amp;#10148; ชุดข้อมูลพร้อมใช้งาน &amp;rarr; เริ่มต้นการสืบค้นข้อมูลในกิจกรรมที่ 2", 30, 690, 280, 26, S_TRANS)
    add_edge("e1_trans", "act1_10", "trans_1_2")

    # =========================================================================
    # กิจกรรมที่ 2: การแปลงคำถามเป็น SQL และ Self-Correction
    # =========================================================================
    add_node("ban_act2", "lane_back", "&lt;b&gt;กิจกรรมที่ 2: การแปลงคำถามภาษาธรรมชาติเป็น SQL และการซ่อมแซมคำสั่งอัตโนมัติ (NL-to-SQL &amp; Self-Correction)&lt;/b&gt;", 10, 730, 460, 26, S_BANNER)

    add_node("act2_1", "lane_user", "&lt;b&gt;11. พิมพ์คำถามภาษาไทย&lt;/b&gt;&lt;br&gt;เช่น &lt;i&gt;'แสดงยอดขาย 5 อันดับแรก&lt;br&gt;แยกตามภาค'&lt;/i&gt;", 40, 780, 200, 55, S_ACTION)
    add_edge("e2_0", "trans_1_2", "act2_1", exitX=0, exitY=0.5, entryX=0.5, entryY=0)

    add_node("act2_2", "lane_front", "&lt;b&gt;12. ตรวจสอบคำถาม&lt;/b&gt;&lt;br&gt;ข้อความไม่ว่าง และตัดช่องว่างส่วนเกิน", 70, 780, 200, 55, S_ACTION_FRONT)
    add_edge("e2_1", "act2_1", "act2_2")

    add_node("act2_3", "lane_front", "&lt;b&gt;13. ส่งคำขอ Query&lt;/b&gt;&lt;br&gt;แสดง Loading Animation + ยิง&lt;br&gt;POST /query (พร้อม Context 5 ข้อความ)", 70, 860, 200, 55, S_ACTION_FRONT)
    add_edge("e2_2", "act2_2", "act2_3")

    add_node("act2_4", "lane_back", "&lt;b&gt;14. Rate Limiter Guard&lt;/b&gt;&lt;br&gt;ตรวจสอบโควตา Client IP (&amp;le; 120 req/m)", 115, 860, 250, 45, S_ACTION_BACK)
    add_edge("e2_3", "act2_3", "act2_4")

    add_node("dec2_1", "lane_back", "เกินโควตา&lt;br&gt;Rate Limit?", 180, 930, 120, 60, S_DECISION)
    add_edge("e2_4", "act2_4", "dec2_1")

    add_node("act2_429", "lane_back", "&lt;b&gt;HTTP 429 Too Many Requests&lt;/b&gt;&lt;br&gt;แจ้งเตือนผู้ใช้ให้รอ 1 นาที", 20, 1010, 160, 45, "rounded=1;whiteSpace=wrap;html=1;fillColor=#FDEDEC;strokeColor=#E74C3C;strokeWidth=1.5;fontSize=10;")
    add_node("end_2a", "lane_back", "", 85, 1075, 30, 30, S_END)
    add_edge("e2_err1", "dec2_1", "act2_429", "[เกิน 120 req/m]", exitX=0, exitY=0.5, entryX=0.5, entryY=0, is_red=True)
    add_edge("e2_err2", "act2_429", "end_2a", "", is_red=True)

    add_node("act2_5", "lane_back", "&lt;b&gt;15. Schema Inspector&lt;/b&gt;&lt;br&gt;ดึงชื่อตาราง, คอลัมน์, ประเภทข้อมูล,&lt;br&gt;และสุ่มตัวอย่างข้อมูลจริง 3 แถว", 200, 1010, 260, 50, S_ACTION_BACK)
    add_edge("e2_ok1", "dec2_1", "act2_5", "[ไม่เกินโควตา]", exitX=1, exitY=0.5, entryX=0.5, entryY=0)

    add_node("act2_6", "lane_back", "&lt;b&gt;16. Prompt Builder&lt;/b&gt;&lt;br&gt;ประกอบ Schema + คำถามภาษาไทย +&lt;br&gt;กฎความปลอดภัย + ตัวอย่าง Few-shot", 200, 1085, 260, 55, S_ACTION_BACK)
    add_edge("e2_5", "act2_5", "act2_6")

    add_node("act2_7", "lane_back", "&lt;b&gt;17. LLM Synthesis (Groq API)&lt;/b&gt;&lt;br&gt;ส่งต่อไปยัง LLaMA 3.3 70B&lt;br&gt;สังเคราะห์คำสั่ง SQL อัตโนมัติ", 200, 1165, 260, 50, S_ACTION_BACK)
    add_edge("e2_6", "act2_6", "act2_7")

    add_node("act2_8", "lane_back", "&lt;b&gt;18. Security AST Validation&lt;/b&gt;&lt;br&gt;ตรวจสอบโครงสร้าง Abstract Syntax Tree&lt;br&gt;อนุญาตเฉพาะคำสั่ง SELECT เท่านั้น", 200, 1240, 260, 50, S_ACTION_BACK)
    add_edge("e2_7", "act2_7", "act2_8")

    add_node("dec2_sec", "lane_back", "ผ่านเกณฑ์&lt;br&gt;ความปลอดภัย?", 270, 1315, 120, 60, S_DECISION)
    add_edge("e2_8", "act2_8", "dec2_sec")

    add_node("act2_sec_err", "lane_back", "&lt;b&gt;บล็อกคำสั่งอันตราย&lt;/b&gt;&lt;br&gt;พบ DROP/DELETE/INSERT/ALTER&lt;br&gt;หรือ Multiple Statements", 80, 1395, 170, 55, "rounded=1;whiteSpace=wrap;html=1;fillColor=#FDEDEC;strokeColor=#E74C3C;strokeWidth=1.5;fontSize=10;")
    add_node("end_2b", "lane_back", "", 150, 1475, 30, 30, S_END)
    add_edge("e2_sec_no", "dec2_sec", "act2_sec_err", "[คำสั่งอันตราย]", exitX=0, exitY=0.5, entryX=0.5, entryY=0, is_red=True)
    add_edge("e2_sec_end", "act2_sec_err", "end_2b", "", is_red=True)

    add_node("act2_9", "lane_db", "&lt;b&gt;19. รันคำสั่ง SQL ใน Sandbox&lt;/b&gt;&lt;br&gt;SQLite Read-Only Connection&lt;br&gt;Timeout 5 วินาที (WAL Mode)", 40, 1395, 220, 55, S_ACTION_DB)
    add_edge("e2_sec_yes", "dec2_sec", "act2_9", "[เฉพาะ SELECT]", exitX=1, exitY=0.5, entryX=0.5, entryY=0)

    add_node("dec2_exec", "lane_back", "ผลการรัน SQL&lt;br&gt;สำเร็จหรือไม่?", 270, 1500, 120, 65, S_DECISION)
    add_edge("e2_9", "act2_9", "dec2_exec", exitX=0.5, exitY=1, entryX=1, entryY=0.5)

    add_node("dec2_retry", "lane_back", "จำนวน Retry&lt;br&gt;&amp;lt; 2 ครั้ง?", 120, 1585, 110, 60, S_DECISION)
    add_edge("e2_exec_err", "dec2_exec", "dec2_retry", "[เกิด Error]", exitX=0, exitY=0.5, entryX=0.5, entryY=0, is_red=True)

    add_node("act2_corr", "lane_back", "&lt;b&gt;20. Self-Correction Engine&lt;/b&gt;&lt;br&gt;นำ Error Message + SQL เดิม + Schema&lt;br&gt;ป้อนกลับให้ AI ปรับแก้ใหม่ (Retry+1)", 40, 1675, 200, 55, S_ACTION_BACK)
    add_edge("e2_retry_yes", "dec2_retry", "act2_corr", "[Retry &amp;lt; 2]", exitX=0.5, exitY=1, entryX=0.5, entryY=0)
    # Loop back to DB execute
    add_edge("e2_loop", "act2_corr", "act2_9", "ส่ง SQL ที่แก้แล้วรันใหม่", exitX=0, exitY=0.5, entryX=0, entryY=0.5)

    add_node("act2_fail", "lane_back", "&lt;b&gt;21. แจ้งเตือนข้อผิดพลาดสุภาพ&lt;/b&gt;&lt;br&gt;อธิบายสาเหตุและแนะนำปรับคำถาม", 170, 1675, 150, 50, "rounded=1;whiteSpace=wrap;html=1;fillColor=#FDEDEC;strokeColor=#E74C3C;strokeWidth=1.5;fontSize=10;")
    add_node("end_2c", "lane_back", "", 230, 1750, 30, 30, S_END)
    add_edge("e2_retry_no", "dec2_retry", "act2_fail", "[ครบ 2 รอบ]", exitX=1, exitY=0.5, entryX=0.5, entryY=0, is_red=True)
    add_edge("e2_fail_end", "act2_fail", "end_2c", "", is_red=True)

    add_node("act2_succ", "lane_back", "&lt;b&gt;22. ดึงชุดข้อมูลผลลัพธ์ (Result Rows)&lt;/b&gt;&lt;br&gt;ได้แถวข้อมูลผลลัพธ์จากการรันสำเร็จ", 260, 1675, 200, 50, S_ACTION_BACK)
    add_edge("e2_exec_ok", "dec2_exec", "act2_succ", "[รันสำเร็จ 100%]", exitX=0.5, exitY=1, entryX=0.5, entryY=0)

    add_node("trans_2_3", "lane_back", "&amp;#10148; ส่ง Result Rows เข้าสู่ระบบวิเคราะห์สถิติและการเลือกกราฟในกิจกรรมที่ 3", 50, 1750, 380, 26, S_TRANS)
    add_edge("e2_trans", "act2_succ", "trans_2_3")

    # =========================================================================
    # กิจกรรมที่ 3: การวิเคราะห์สถิติและการเลือกกราฟ (Analytics & Recommendation)
    # =========================================================================
    add_node("ban_act3", "lane_back", "&lt;b&gt;กิจกรรมที่ 3: การวิเคราะห์ข้อมูลสถิติและการเลือกกราฟอัตโนมัติ (Analytics &amp; Chart Recommendation)&lt;/b&gt;", 10, 1795, 460, 26, S_BANNER)

    add_node("act3_1", "lane_back", "&lt;b&gt;23. รับชุดข้อมูลผลลัพธ์ (Rows)&lt;/b&gt;&lt;br&gt;ตรวจสอบจำนวนแถวของข้อมูลที่ส่งมา", 115, 1840, 250, 45, S_ACTION_BACK)
    add_edge("e3_0", "trans_2_3", "act3_1")

    add_node("dec3_rows", "lane_back", "จำนวนแถว&lt;br&gt;&amp;gt; 0 แถว?", 180, 1910, 120, 60, S_DECISION)
    add_edge("e3_1", "act3_1", "dec3_rows")

    add_node("act3_empty", "lane_front", "&lt;b&gt;24. สรุปไม่พบข้อมูล&lt;/b&gt;&lt;br&gt;แจ้งเตือน &lt;i&gt;'ไม่พบข้อมูลที่ตรงเงื่อนไข'&lt;/i&gt;", 70, 1915, 200, 50, S_ACTION_FRONT)
    add_node("end_3a", "lane_front", "", 20, 1925, 30, 30, S_END)
    add_edge("e3_empty_edge", "dec3_rows", "act3_empty", "[0 แถว]", exitX=0, exitY=0.5, entryX=1, entryY=0.5, is_red=True)
    add_edge("e3_empty_end", "act3_empty", "end_3a", "", is_red=True)

    add_node("act3_2", "lane_back", "&lt;b&gt;25. EDA Analyzer&lt;/b&gt;&lt;br&gt;แยกแยะคอลัมน์ตัวเลข (Metrics)&lt;br&gt;และคอลัมน์หมวดหมู่/วันที่ (Dimensions)", 115, 1995, 250, 50, S_ACTION_BACK)
    add_edge("e3_has_rows", "dec3_rows", "act3_2", "[มีข้อมูล &amp;gt; 0]", exitX=0.5, exitY=1, entryX=0.5, entryY=0)

    add_node("act3_3", "lane_back", "&lt;b&gt;26. Smart Aggregation &amp;amp; Truncation&lt;/b&gt;&lt;br&gt;หากผลลัพธ์ &amp;gt; 20 แถว ให้รวมกลุ่ม/ตัดเหลือ&lt;br&gt;Top 20 พร้อมตั้งค่า is_truncated = true", 115, 2070, 250, 55, S_ACTION_BACK)
    add_edge("e3_2", "act3_2", "act3_3")

    add_node("act3_4", "lane_back", "&lt;b&gt;27. Chart Recommender Heuristics&lt;/b&gt;&lt;br&gt;&amp;bull; เปรียบเทียบ &amp;rarr; Bar Chart&lt;br&gt;&amp;bull; ช่วงเวลา/แนวโน้ม &amp;rarr; Line / Area Chart&lt;br&gt;&amp;bull; สัดส่วน (&amp;le; 7 ส่วน) &amp;rarr; Pie Chart&lt;br&gt;&amp;bull; ค่าเดี่ยว &amp;rarr; Summary Card", 115, 2150, 250, 75, S_ACTION_BACK)
    add_edge("e3_3", "act3_3", "act3_4")

    add_node("act3_5", "lane_back", "&lt;b&gt;28. Statistical Summarizer&lt;/b&gt;&lt;br&gt;คำนวณสถิติใช้งานจริง: ผลรวม (Total),&lt;br&gt;ค่าเฉลี่ย (Avg), สูงสุด (Max), ต่ำสุด (Min), จำนวน", 115, 2250, 250, 55, S_ACTION_BACK)
    add_edge("e3_4", "act3_4", "act3_5")

    add_node("act3_6", "lane_front", "&lt;b&gt;29. เรนเดอร์คำตอบและกล่อง SQL&lt;/b&gt;&lt;br&gt;แสดงบทสรุปภาษาไทย + กล่องคำสั่ง SQL&lt;br&gt;พร้อมตัววัดระดับความมั่นใจ (Confidence)", 50, 2250, 240, 55, S_ACTION_FRONT)
    add_edge("e3_5", "act3_5", "act3_6")

    add_node("act3_7", "lane_front", "&lt;b&gt;30. เรนเดอร์แท็บกราฟ (Interactive)&lt;/b&gt;&lt;br&gt;สลับ Bar / Line / Pie / Area ได้ทันที&lt;br&gt;+ &lt;b&gt;ปุ่ม 'ส่งออก PNG' (2x Retina พื้นหลังขาว)&lt;/b&gt;", 50, 2330, 240, 60, S_ACTION_FRONT)
    add_edge("e3_6", "act3_6", "act3_7")

    add_node("act3_8", "lane_front", "&lt;b&gt;31. เรนเดอร์แท็บตาราง (Data Table)&lt;/b&gt;&lt;br&gt;แสดงข้อมูลทุกแถว + ปุ่มดาวน์โหลด CSV&lt;br&gt;(ฟอร์แมต UTF-8 BOM ภาษาไทยสมบูรณ์)", 50, 2415, 240, 55, S_ACTION_FRONT)
    add_edge("e3_7", "act3_7", "act3_8")

    add_node("act3_9", "lane_front", "&lt;b&gt;32. แสดงปุ่ม '📌 ปักหมุด'&lt;/b&gt;&lt;br&gt;เปิดให้ผู้ใช้กดนำผลลัพธ์เข้าแดชบอร์ดรวม", 50, 2495, 240, 45, S_ACTION_FRONT)
    add_edge("e3_8", "act3_8", "act3_9")

    add_node("trans_3_4", "lane_user", "&amp;#10148; ผู้ใช้งานมีปฏิสัมพันธ์กับผลลัพธ์ในกิจกรรมที่ 4", 30, 2565, 220, 26, S_TRANS)
    add_edge("e3_trans", "act3_9", "trans_3_4", exitX=0, exitY=0.5, entryX=0.5, entryY=0)

    # =========================================================================
    # กิจกรรมที่ 4: การจัดการประวัติสนทนาและการปักหมุดแดชบอร์ด
    # =========================================================================
    add_node("ban_act4", "lane_back", "&lt;b&gt;กิจกรรมที่ 4: การจัดการประวัติการสนทนาและการปักหมุดแดชบอร์ด (Chat History &amp; Pinned Dashboard)&lt;/b&gt;", 10, 2615, 460, 26, S_BANNER)

    add_node("dec4_user", "lane_user", "ผู้ใช้เลือก&lt;br&gt;การทำงานใด?", 80, 2665, 120, 65, S_DECISION)
    add_edge("e4_0", "trans_3_4", "dec4_user")

    # Branch A: ถามคำถามในห้องใหม่ / สลับห้อง
    add_node("act4_a1", "lane_user", "&lt;b&gt;กรณี A: ถามคำถามในห้องใหม่&lt;/b&gt;&lt;br&gt;ผู้ใช้สร้างห้องใหม่แล้วพิมพ์ถาม", 30, 2760, 190, 50, S_ACTION)
    add_edge("e4_bra", "dec4_user", "act4_a1", "[ทางเลือก A]", exitX=0, exitY=0.5, entryX=0.5, entryY=0)

    add_node("act4_a2", "lane_front", "&lt;b&gt;33A. generateSessionTitle()&lt;/b&gt;&lt;br&gt;แปลงคำถามแรกเป็นชื่อหัวข้อกระชับ&lt;br&gt;(ตัดคำว่า ขอ, ช่วย, แสดง, ค้นหา)", 50, 2760, 240, 55, S_ACTION_FRONT)
    add_edge("e4_a1_2", "act4_a1", "act4_a2")

    add_node("act4_a3", "lane_back", "&lt;b&gt;34A. ซิงค์ชื่อลงฐานข้อมูล&lt;/b&gt;&lt;br&gt;ส่ง PUT /sessions/{id} บันทึกชื่อ&lt;br&gt;ลงตาราง chat_sessions ใน SQLite", 115, 2760, 250, 55, S_ACTION_BACK)
    add_edge("e4_a2_3", "act4_a2", "act4_a3")

    add_node("act4_a4", "lane_front", "&lt;b&gt;35A. อัปเดต Sidebar&lt;/b&gt;&lt;br&gt;แสดงชื่อห้องใหม่อย่างสะอาดตา&lt;br&gt;(ตัดคำว่า 'ล่าสุด' ออกเรียบร้อย)", 50, 2840, 240, 50, S_ACTION_FRONT)
    add_edge("e4_a3_4", "act4_a3", "act4_a4")

    # Branch B: ปักหมุด
    add_node("act4_b1", "lane_user", "&lt;b&gt;กรณี B: กดปุ่ม '📌 ปักหมุด'&lt;/b&gt;&lt;br&gt;ต้องการบันทึกการ์ดเข้าแดชบอร์ด", 40, 2920, 180, 50, S_ACTION)
    add_edge("e4_brb", "dec4_user", "act4_b1", "[ทางเลือก B]", exitX=0.5, exitY=1, entryX=0.5, entryY=0)

    add_node("act4_b2", "lane_front", "&lt;b&gt;33B. ส่ง POST /pinned-dashboard&lt;/b&gt;&lt;br&gt;ส่ง Payload: title, visualization,&lt;br&gt;sql, text summary, sessionId", 50, 2920, 240, 55, S_ACTION_FRONT)
    add_edge("e4_b1_2", "act4_b1", "act4_b2")

    add_node("act4_b3", "lane_db", "&lt;b&gt;34B. Insert pinned_items&lt;/b&gt;&lt;br&gt;บันทึกข้อมูลและ Content JSON&lt;br&gt;ลงตาราง pinned_items", 40, 2920, 220, 55, S_ACTION_DB)
    add_edge("e4_b2_3", "act4_b2", "act4_b3")

    add_node("act4_b4", "lane_front", "&lt;b&gt;35B. แสดง Toast ปักหมุดสำเร็จ&lt;/b&gt;&lt;br&gt;พร้อมเปิดให้ผู้ใช้กดดูในแท็บรวม", 50, 3000, 240, 45, S_ACTION_FRONT)
    add_edge("e4_b3_4", "act4_b3", "act4_b4")

    # Branch C: เปิดแท็บแดชบอร์ดรวม
    add_node("act4_c1", "lane_user", "&lt;b&gt;กรณี C: ดูแดชบอร์ดรวม&lt;/b&gt;&lt;br&gt;คลิกแท็บ 'แดชบอร์ดรวม'", 40, 3075, 180, 50, S_ACTION)
    add_edge("e4_brc", "dec4_user", "act4_c1", "[ทางเลือก C]", exitX=1, exitY=0.5, entryX=0.5, entryY=0)

    add_node("act4_c2", "lane_front", "&lt;b&gt;33C. ส่ง GET /pinned-dashboard&lt;/b&gt;&lt;br&gt;ดึงรายการปักหมุดทั้งหมดจาก Backend", 50, 3075, 240, 50, S_ACTION_FRONT)
    add_edge("e4_c1_2", "act4_c1", "act4_c2")

    add_node("act4_c3", "lane_db", "&lt;b&gt;34C. Query pinned_items&lt;/b&gt;&lt;br&gt;SELECT * FROM pinned_items&lt;br&gt;ORDER BY pinned_at DESC", 40, 3075, 220, 50, S_ACTION_DB)
    add_edge("e4_c2_3", "act4_c2", "act4_c3")

    add_node("act4_c4", "lane_front", "&lt;b&gt;35C. เรนเดอร์ Dynamic Grid&lt;/b&gt;&lt;br&gt;แสดงการ์ดสรุป + กราฟย่อย + รองรับ&lt;br&gt;ปลดหมุด (Unpin) และพิมพ์/PDF", 50, 3155, 240, 60, S_ACTION_FRONT)
    add_edge("e4_c3_4", "act4_c3", "act4_c4")

    # Merge point
    add_node("merge_final", "lane_front", "จุดรวมการทำงาน (Merge)", 120, 3255, 100, 40, "rhombus;whiteSpace=wrap;html=1;fillColor=#E5E8E8;strokeColor=#7F8C8D;fontSize=9;")
    add_edge("e4_m1", "act4_a4", "merge_final")
    add_edge("e4_m2", "act4_b4", "merge_final")
    add_edge("e4_m3", "act4_c4", "merge_final")

    add_node("act_ready", "lane_front", "&lt;b&gt;ระบบพร้อมรับคำสั่งถัดไป&lt;/b&gt;&lt;br&gt;ผู้ใช้สามารถพิมพ์ถามต่อหรือจัดการข้อมูลได้ทันที", 50, 3325, 240, 45, S_ACTION_FRONT)
    add_edge("e4_m_ready", "merge_final", "act_ready")

    add_node("end_final", "lane_front", "", 155, 3400, 30, 30, S_END)
    add_edge("e4_final_end", "act_ready", "end_final")

    # Format XML nicely
    xml_str = ET.tostring(mxfile, encoding="utf-8")
    return xml_str

if __name__ == "__main__":
    out_dir = r"D:\Project\team04-agentAI\docs"
    out_path = f"{out_dir}\\system_activity_diagram_end_to_end.drawio"
    content = build_drawio()
    with open(out_path, "wb") as f:
        f.write(content)
    print(f"Successfully generated drawio file at: {out_path} (size: {len(content)} bytes)")
