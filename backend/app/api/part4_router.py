import json
import logging
from datetime import datetime
from fastapi import APIRouter, Body, HTTPException
from typing import List, Dict, Any, Optional
from sqlalchemy import text
from app.db.database import engine

logger = logging.getLogger("Part4Router")

router = APIRouter(prefix="/part4", tags=["Part 4: Frontend & Dashboard APIs"])

# ============================================
# ระบบเก็บ Chat History และ Pinned Items ลงฐานข้อมูล SQLite
# ============================================

_tables_initialized = False


def _init_part4_tables():
    """สร้างตาราง chat_sessions, chat_messages, pinned_items หากยังไม่มี"""
    global _tables_initialized
    if _tables_initialized:
        return
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS chat_sessions (
                session_id TEXT PRIMARY KEY,
                title TEXT NOT NULL DEFAULT 'การสนทนาใหม่',
                table_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS chat_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'user',
                content TEXT NOT NULL,
                metadata_json TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES chat_sessions(session_id) ON DELETE CASCADE
            );
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS pinned_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                content_json TEXT NOT NULL,
                pinned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """))

        # เพิ่มคอลัมน์ table_name หากยังไม่มี (Migration)
        try:
            conn.execute(text("ALTER TABLE chat_sessions ADD COLUMN table_name TEXT;"))
        except Exception:
            pass

        # Backfill table_name จากข้อความนำเข้าชุดข้อมูลเดิม (uploadData)
        try:
            conn.execute(text("""
                UPDATE chat_sessions
                SET table_name = (
                    SELECT json_extract(metadata_json, '$.uploadData.table_name')
                    FROM chat_messages
                    WHERE chat_messages.session_id = chat_sessions.session_id
                      AND metadata_json LIKE '%uploadData%'
                    ORDER BY id DESC
                    LIMIT 1
                )
                WHERE table_name IS NULL;
            """))
        except Exception:
            pass

        # ทำความสะอาดชื่อ session เก่าที่เคยมีตัวเลขต่อท้าย หรือเป็น markdown
        try:
            conn.execute(text("""
                UPDATE chat_sessions 
                SET title = 'การสนทนาใหม่' 
                WHERE title LIKE 'การสนทนาใหม่ %';
            """))
            conn.execute(text("""
                UPDATE chat_sessions 
                SET title = 'ชุดข้อมูล: ' || substr(title, instr(title, '`') + 1, instr(substr(title, instr(title, '`') + 1), '`') - 1) 
                WHERE title LIKE '**นำเข้า%`%`%';
            """))
            conn.execute(text("""
                UPDATE chat_sessions 
                SET title = REPLACE(REPLACE(title, '**', ''), '`', '') 
                WHERE title LIKE '**%';
            """))
        except Exception:
            pass
        conn.commit()
    _tables_initialized = True


def _clean_session_title(title: str) -> str:
    """ทำความสะอาดชื่อหัวข้อสนทนา ป้องกันข้อความ Markdown ตกค้าง และตัดตัวเลขต่อท้ายการสนทนาใหม่"""
    if not title:
        return "การสนทนาใหม่"
    import re
    if re.match(r"^การสนทนาใหม่(\s*\d+)?$", title):
        return "การสนทนาใหม่"
    if title.startswith("**นำเข้าชุดข้อมูลเข้าสู่ตาราง `") or title.startswith("**นำเข้า"):
        m = re.search(r"`([^`]+)`", title)
        if m:
            return f"ชุดข้อมูล: {m.group(1)}"
        return "ชุดข้อมูลใหม่"
    if title.startswith("**"):
        return title.replace("**", "").replace("`", "").strip()[:30]
    return title


# ============================================
# Chat Session APIs
# ============================================

@router.get("/sessions")
def list_sessions():
    """ดึงรายชื่อ Session ทั้งหมด เรียงตามเวลาล่าสุด"""
    _init_part4_tables()
    with engine.connect() as conn:
        rows = conn.execute(text(
            "SELECT session_id, title, created_at, updated_at, table_name FROM chat_sessions ORDER BY updated_at DESC"
        )).fetchall()
    return {
        "sessions": [
            {
                "session_id": r[0],
                "title": _clean_session_title(r[1]),
                "created_at": r[2],
                "updated_at": r[3],
                "table_name": r[4] if len(r) > 4 else None,
            }
            for r in rows
        ]
    }


@router.post("/sessions")
def create_session(data: Dict[str, Any] = Body(...)):
    """สร้าง Session ใหม่"""
    _init_part4_tables()
    session_id = data.get("session_id", "")
    title = data.get("title", "การสนทนาใหม่")
    table_name = data.get("table_name")
    if not session_id:
        raise HTTPException(status_code=400, detail="session_id is required")
    with engine.connect() as conn:
        conn.execute(text(
            "INSERT OR IGNORE INTO chat_sessions (session_id, title, table_name) VALUES (:sid, :title, :tbl)"
        ), {"sid": session_id, "title": title, "tbl": table_name})
        conn.commit()
    return {"status": "success", "session_id": session_id, "table_name": table_name}


@router.put("/sessions/{session_id}")
def update_session(session_id: str, data: Dict[str, Any] = Body(...)):
    """อัปเดตชื่อ Session หรือ table_name"""
    _init_part4_tables()
    title = data.get("title")
    table_name = data.get("table_name")
    updates = []
    params = {"sid": session_id}
    if title is not None:
        updates.append("title = :title")
        params["title"] = title
    if "table_name" in data:
        updates.append("table_name = :tbl")
        params["tbl"] = table_name
    if not updates:
        return {"status": "success"}
    updates.append("updated_at = CURRENT_TIMESTAMP")
    sql = f"UPDATE chat_sessions SET {', '.join(updates)} WHERE session_id = :sid"
    with engine.connect() as conn:
        conn.execute(text(sql), params)
        conn.commit()
    return {"status": "success"}


@router.delete("/sessions/{session_id}")
def delete_session(session_id: str):
    """ลบ Session, ข้อความทั้งหมดใน Session นั้น และรายการปักหมุดที่เกี่ยวข้องกับ Session นี้"""
    _init_part4_tables()
    with engine.connect() as conn:
        conn.execute(text("DELETE FROM chat_messages WHERE session_id = :sid"), {"sid": session_id})
        conn.execute(text("DELETE FROM chat_sessions WHERE session_id = :sid"), {"sid": session_id})
        conn.execute(text("DELETE FROM pinned_items WHERE content_json LIKE :pattern"), {"pattern": f'%"sessionId": "{session_id}"%'})
        conn.commit()
    return {"status": "success"}


# ============================================
# Chat History APIs
# ============================================

@router.get("/chat-history/{session_id}")
def get_chat_history(session_id: str):
    """ดึงประวัติการแชทแยกตาม Session พร้อมข้อมูลชุดข้อมูลที่ผูกไว้"""
    _init_part4_tables()
    with engine.connect() as conn:
        session_row = conn.execute(text(
            "SELECT title, table_name FROM chat_sessions WHERE session_id = :sid"
        ), {"sid": session_id}).fetchone()

        rows = conn.execute(text(
            "SELECT id, role, content, metadata_json, created_at FROM chat_messages "
            "WHERE session_id = :sid ORDER BY id ASC"
        ), {"sid": session_id}).fetchall()
    messages = []
    for r in rows:
        msg = {"id": r[0], "role": r[1], "content": r[2], "created_at": r[4]}
        if r[3]:
            try:
                msg["metadata"] = json.loads(r[3])
            except (json.JSONDecodeError, TypeError):
                pass
        messages.append(msg)
    title = session_row[0] if session_row else "การสนทนาใหม่"
    table_name = session_row[1] if session_row else None
    return {
        "session_id": session_id,
        "title": _clean_session_title(title),
        "table_name": table_name,
        "messages": messages,
    }


@router.post("/chat-history/{session_id}")
def save_chat_message(session_id: str, message: Dict[str, Any] = Body(...)):
    """บันทึกข้อความลงประวัติการแชท (พร้อมสร้าง Session อัตโนมัติและผูก table_name หากมี)"""
    _init_part4_tables()
    role = message.get("role", "user")
    content = message.get("content") or message.get("text", "")
    metadata = message.get("metadata")
    metadata_json = json.dumps(metadata, ensure_ascii=False) if metadata else None

    # ตรวจหา table_name จาก metadata หรือ content
    detected_table = None
    if metadata and isinstance(metadata, dict) and metadata.get("uploadData"):
        upload_data = metadata.get("uploadData")
        detected_table = upload_data.get("table_name")
        default_title = f"ชุดข้อมูล: {detected_table}" if detected_table else "ชุดข้อมูลใหม่"
    elif content.startswith("**นำเข้า"):
        import re
        m = re.search(r"`([^`]+)`", content)
        if m:
            detected_table = m.group(1)
            default_title = f"ชุดข้อมูล: {detected_table}"
        else:
            default_title = "ชุดข้อมูลใหม่"
    elif content:
        clean_text = content.strip().lstrip("#* \t\n")
        default_title = clean_text[:30] if clean_text else "การสนทนาใหม่"
    else:
        default_title = "การสนทนาใหม่"

    with engine.connect() as conn:
        # สร้าง session ถ้ายังไม่มี
        conn.execute(text(
            "INSERT OR IGNORE INTO chat_sessions (session_id, title, table_name) VALUES (:sid, :title, :tbl)"
        ), {"sid": session_id, "title": default_title, "tbl": detected_table})

        # หากมีชุดข้อมูลที่นำเข้า ให้บันทึก table_name ผูกกับห้องสนทนานี้
        if detected_table:
            conn.execute(text(
                "UPDATE chat_sessions SET table_name = :tbl WHERE session_id = :sid AND (table_name IS NULL OR table_name = '')"
            ), {"tbl": detected_table, "sid": session_id})

        # หากเป็นข้อความคำถามจาก User (role == 'user') และชื่อห้องปัจจุบันยังเป็นชื่อเริ่มต้นหรือชื่อชุดข้อมูล
        # ให้อัปเดตชื่อห้องตามคำถามของผู้ใช้โดยอัตโนมัติ
        if role in ("user", "human") and content.strip():
            current_title = conn.execute(text(
                "SELECT title FROM chat_sessions WHERE session_id = :sid"
            ), {"sid": session_id}).scalar()

            if current_title:
                is_initial_title = (
                    current_title.startswith("การสนทนาใหม่") or
                    current_title.startswith("ชุดข้อมูล:") or
                    current_title.startswith("**") or
                    current_title in ("การวิเคราะห์ข้อมูลและสถิติ", "ชุดข้อมูลใหม่", "นำเข้าชุดข้อมูล")
                )
                if is_initial_title:
                    import re
                    user_clean = content.strip()
                    user_clean = re.sub(r"^(ขอ|ช่วย|ลอง|กรุณา|ค้นหา|แสดง)\s*", "", user_clean, flags=re.IGNORECASE)
                    new_title = (user_clean[:24] + "...") if len(user_clean) > 24 else (user_clean or content.strip()[:20])
                    conn.execute(text(
                        "UPDATE chat_sessions SET title = :title WHERE session_id = :sid"
                    ), {"title": new_title, "sid": session_id})

        # บันทึกข้อความ
        conn.execute(text(
            "INSERT INTO chat_messages (session_id, role, content, metadata_json) VALUES (:sid, :role, :content, :meta)"
        ), {"sid": session_id, "role": role, "content": content, "meta": metadata_json})

        # อัปเดต updated_at ของ session
        conn.execute(text(
            "UPDATE chat_sessions SET updated_at = CURRENT_TIMESTAMP WHERE session_id = :sid"
        ), {"sid": session_id})
        conn.commit()

        count = conn.execute(text(
            "SELECT COUNT(*) FROM chat_messages WHERE session_id = :sid"
        ), {"sid": session_id}).scalar()
    return {"status": "success", "count": count}


# ============================================
# Pinned Dashboard APIs
# ============================================

@router.get("/pinned-dashboard")
def get_pinned_items():
    """ดึงรายการกราฟ/Insight ที่ผู้ใช้ปักหมุด (Pin) ไว้"""
    _init_part4_tables()
    with engine.connect() as conn:
        rows = conn.execute(text(
            "SELECT id, title, content_json, pinned_at FROM pinned_items ORDER BY pinned_at DESC"
        )).fetchall()
    items = []
    for r in rows:
        item = {"id": r[0], "title": r[1], "pinned_at": r[3]}
        try:
            item["content"] = json.loads(r[2])
        except (json.JSONDecodeError, TypeError):
            item["content"] = r[2]
        items.append(item)
    return {"pinned_items": items}


@router.post("/pin-item")
def pin_item_to_dashboard(item: Dict[str, Any] = Body(...)):
    """ปักหมุดการ์ดกราฟหรือสรุปข้อความลงบน Dashboard"""
    _init_part4_tables()
    title = item.get("title", "Pinned Item")
    content_json = json.dumps(item, ensure_ascii=False)
    with engine.connect() as conn:
        conn.execute(text(
            "INSERT INTO pinned_items (title, content_json) VALUES (:title, :content)"
        ), {"title": title, "content": content_json})
        conn.commit()
        count = conn.execute(text("SELECT COUNT(*) FROM pinned_items")).scalar()
    return {"status": "success", "pinned_count": count}


@router.delete("/pin-item/{item_id}")
def unpin_item(item_id: int):
    """ยกเลิกการปักหมุด"""
    _init_part4_tables()
    with engine.connect() as conn:
        conn.execute(text("DELETE FROM pinned_items WHERE id = :id"), {"id": item_id})
        conn.commit()
        count = conn.execute(text("SELECT COUNT(*) FROM pinned_items")).scalar()
    return {"status": "success", "pinned_count": count}
