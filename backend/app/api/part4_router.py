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
        conn.commit()
    _tables_initialized = True


# ============================================
# Chat Session APIs
# ============================================

@router.get("/sessions")
def list_sessions():
    """ดึงรายชื่อ Session ทั้งหมด เรียงตามเวลาล่าสุด"""
    _init_part4_tables()
    with engine.connect() as conn:
        rows = conn.execute(text(
            "SELECT session_id, title, created_at, updated_at FROM chat_sessions ORDER BY updated_at DESC"
        )).fetchall()
    return {
        "sessions": [
            {"session_id": r[0], "title": r[1], "created_at": r[2], "updated_at": r[3]}
            for r in rows
        ]
    }


@router.post("/sessions")
def create_session(data: Dict[str, Any] = Body(...)):
    """สร้าง Session ใหม่"""
    _init_part4_tables()
    session_id = data.get("session_id", "")
    title = data.get("title", "การสนทนาใหม่")
    if not session_id:
        raise HTTPException(status_code=400, detail="session_id is required")
    with engine.connect() as conn:
        conn.execute(text(
            "INSERT OR IGNORE INTO chat_sessions (session_id, title) VALUES (:sid, :title)"
        ), {"sid": session_id, "title": title})
        conn.commit()
    return {"status": "success", "session_id": session_id}


@router.put("/sessions/{session_id}")
def update_session(session_id: str, data: Dict[str, Any] = Body(...)):
    """อัปเดตชื่อ Session"""
    _init_part4_tables()
    title = data.get("title", "")
    with engine.connect() as conn:
        conn.execute(text(
            "UPDATE chat_sessions SET title = :title, updated_at = CURRENT_TIMESTAMP WHERE session_id = :sid"
        ), {"title": title, "sid": session_id})
        conn.commit()
    return {"status": "success"}


@router.delete("/sessions/{session_id}")
def delete_session(session_id: str):
    """ลบ Session และข้อความทั้งหมดใน Session นั้น"""
    _init_part4_tables()
    with engine.connect() as conn:
        conn.execute(text("DELETE FROM chat_messages WHERE session_id = :sid"), {"sid": session_id})
        conn.execute(text("DELETE FROM chat_sessions WHERE session_id = :sid"), {"sid": session_id})
        conn.commit()
    return {"status": "success"}


# ============================================
# Chat History APIs
# ============================================

@router.get("/chat-history/{session_id}")
def get_chat_history(session_id: str):
    """ดึงประวัติการแชทแยกตาม Session"""
    _init_part4_tables()
    with engine.connect() as conn:
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
    return {"session_id": session_id, "messages": messages}


@router.post("/chat-history/{session_id}")
def save_chat_message(session_id: str, message: Dict[str, Any] = Body(...)):
    """บันทึกข้อความลงประวัติการแชท (พร้อมสร้าง Session อัตโนมัติหากยังไม่มี)"""
    _init_part4_tables()
    role = message.get("role", "user")
    content = message.get("content") or message.get("text", "")
    metadata = message.get("metadata")
    metadata_json = json.dumps(metadata, ensure_ascii=False) if metadata else None

    with engine.connect() as conn:
        # สร้าง session ถ้ายังไม่มี
        conn.execute(text(
            "INSERT OR IGNORE INTO chat_sessions (session_id, title) VALUES (:sid, :title)"
        ), {"sid": session_id, "title": content[:50] if content else "การสนทนาใหม่"})
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
