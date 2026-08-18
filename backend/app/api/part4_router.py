from fastapi import APIRouter, Body
from typing import List, Dict, Any

router = APIRouter(prefix="/part4", tags=["Part 4: Frontend & Dashboard APIs"])

# In-memory storage จำลองสำหรับ Chat History และ Pinned Dashboard items
chat_history_db: Dict[str, List[Dict[str, Any]]] = {}
pinned_items_db: List[Dict[str, Any]] = []

@router.get("/chat-history/{session_id}")
async def get_chat_history(session_id: str):
    """ดึงประวัติการแชทแยกตาม Session/Topic"""
    history = chat_history_db.get(session_id, [])
    return {"session_id": session_id, "messages": history}

@router.post("/chat-history/{session_id}")
async def save_chat_message(session_id: str, message: Dict[str, Any] = Body(...)):
    """บันทึกข้อความลงประวัติการแชท"""
    if session_id not in chat_history_db:
        chat_history_db[session_id] = []
    chat_history_db[session_id].append(message)
    return {"status": "success", "count": len(chat_history_db[session_id])}

@router.get("/pinned-dashboard")
async def get_pinned_items():
    """ดึงรายการกราฟ/Insight ที่ผู้ใช้ปักหมุด (Pin) ไว้"""
    return {"pinned_items": pinned_items_db}

@router.post("/pin-item")
async def pin_item_to_dashboard(item: Dict[str, Any] = Body(...)):
    """ปักหมุดการ์ดกราฟหรือสรุปข้อความลงบน Dashboard"""
    pinned_items_db.append(item)
    return {"status": "success", "pinned_count": len(pinned_items_db)}

@router.delete("/pin-item/{item_id}")
async def unpin_item(item_id: int):
    """ยกเลิกการปักหมุด"""
    global pinned_items_db
    pinned_items_db = [item for item in pinned_items_db if item.get("id") != item_id]
    return {"status": "success", "pinned_count": len(pinned_items_db)}
