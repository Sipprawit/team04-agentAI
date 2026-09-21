"""
Unit Tests สำหรับ Part 4: Frontend & Dashboard APIs
ทดสอบ Chat Sessions, Chat History, และ Pinned Items ใน SQLite
"""
import pytest
from fastapi.testclient import TestClient
from main import app
from app.db.database import engine
from sqlalchemy import text

client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_part4_data():
    """ทำความสะอาดข้อมูลทดสอบของ Part 4 ก่อนและหลังรันแต่ละเคส"""
    with engine.connect() as conn:
        conn.execute(text("DELETE FROM chat_messages;"))
        conn.execute(text("DELETE FROM chat_sessions;"))
        conn.execute(text("DELETE FROM pinned_items;"))
        conn.commit()
    yield
    with engine.connect() as conn:
        conn.execute(text("DELETE FROM chat_messages;"))
        conn.execute(text("DELETE FROM chat_sessions;"))
        conn.execute(text("DELETE FROM pinned_items;"))
        conn.commit()


class TestChatSessions:
    """ทดสอบ API จัดการ Chat Sessions"""

    def test_create_and_list_sessions(self):
        resp = client.post("/part4/sessions", json={"session_id": "sess-1", "title": "ยอดขาย 2562"})
        assert resp.status_code == 200
        assert resp.json()["status"] == "success"

        list_resp = client.get("/part4/sessions")
        assert list_resp.status_code == 200
        sessions = list_resp.json()["sessions"]
        assert len(sessions) == 1
        assert sessions[0]["session_id"] == "sess-1"
        assert sessions[0]["title"] == "ยอดขาย 2562"

    def test_update_session_title(self):
        client.post("/part4/sessions", json={"session_id": "sess-1", "title": "หัวข้อเดิม"})
        resp = client.put("/part4/sessions/sess-1", json={"title": "หัวข้อใหม่"})
        assert resp.status_code == 200

        list_resp = client.get("/part4/sessions")
        sessions = list_resp.json()["sessions"]
        assert sessions[0]["title"] == "หัวข้อใหม่"

    def test_delete_session(self):
        client.post("/part4/sessions", json={"session_id": "sess-delete", "title": "จะถูกลบ"})
        resp = client.delete("/part4/sessions/sess-delete")
        assert resp.status_code == 200

        list_resp = client.get("/part4/sessions")
        assert len(list_resp.json()["sessions"]) == 0


class TestChatHistory:
    """ทดสอบ API จัดการ Chat History"""

    def test_save_and_get_chat_history(self):
        session_id = "sess-chat-1"
        # บันทึกข้อความแรกของผู้ใช้
        resp1 = client.post(f"/part4/chat-history/{session_id}", json={
            "role": "user",
            "content": "แสดงสินค้าทั้งหมด"
        })
        assert resp1.status_code == 200
        assert resp1.json()["count"] == 1

        # บันทึกข้อความตอบกลับของ AI พร้อม metadata
        resp2 = client.post(f"/part4/chat-history/{session_id}", json={
            "role": "assistant",
            "content": "นี่คือรายการสินค้าทั้งหมด 10 รายการ",
            "metadata": {"sql": "SELECT * FROM products;", "count": 10}
        })
        assert resp2.status_code == 200
        assert resp2.json()["count"] == 2

        # ดึงประวัติการแชท
        hist_resp = client.get(f"/part4/chat-history/{session_id}")
        assert hist_resp.status_code == 200
        data = hist_resp.json()
        assert data["session_id"] == session_id
        messages = data["messages"]
        assert len(messages) == 2
        assert messages[0]["role"] == "user"
        assert messages[0]["content"] == "แสดงสินค้าทั้งหมด"
        assert messages[1]["role"] == "assistant"
        assert messages[1]["metadata"]["count"] == 10


class TestPinnedItems:
    """ทดสอบ API ปักหมุดกราฟ/Insight (Pinned Items)"""

    def test_pin_and_get_and_unpin(self):
        # ปักหมุด item
        pin_resp = client.post("/part4/pin-item", json={
            "title": "กราฟยอดขาย",
            "type": "chart",
            "chart_type": "bar",
            "data": [{"name": "A", "value": 100}]
        })
        assert pin_resp.status_code == 200
        assert pin_resp.json()["status"] == "success"

        # ดึงรายการที่ปักหมุด
        get_resp = client.get("/part4/pinned-dashboard")
        assert get_resp.status_code == 200
        items = get_resp.json()["pinned_items"]
        assert len(items) == 1
        assert items[0]["title"] == "กราฟยอดขาย"
        item_id = items[0]["id"]

        # ถอนการปักหมุด (unpin)
        del_resp = client.delete(f"/part4/pin-item/{item_id}")
        assert del_resp.status_code == 200
        assert del_resp.json()["pinned_count"] == 0

        # ตรวจสอบว่าว่างเปล่าแล้ว
        get_resp2 = client.get("/part4/pinned-dashboard")
        assert len(get_resp2.json()["pinned_items"]) == 0

    def test_delete_session_removes_associated_pinned_items(self):
        session_id = "sess-to-be-deleted"
        # สร้าง session
        client.post("/part4/sessions", json={"session_id": session_id, "title": "ทดสอบปักหมุด"})

        # ปักหมุด item ที่ผูกกับ session นี้
        client.post("/part4/pin-item", json={
            "title": "กราฟที่ผูกกับเซสชันนี้",
            "sessionId": session_id,
            "data": [1, 2, 3]
        })

        # ปักหมุด item ที่ผูกกับอีก session
        client.post("/part4/pin-item", json={
            "title": "กราฟของอีกเซสชัน",
            "sessionId": "other-session",
            "data": [4, 5, 6]
        })

        # ตรวจว่ามี 2 items ใน dashboard
        list_resp = client.get("/part4/pinned-dashboard")
        assert len(list_resp.json()["pinned_items"]) == 2

        # ลบ session แรก
        del_sess_resp = client.delete(f"/part4/sessions/{session_id}")
        assert del_sess_resp.status_code == 200

        # ตรวจว่า item ของ session แรกถูกลบไปด้วย เหลือเฉพาะของ other-session
        after_resp = client.get("/part4/pinned-dashboard")
        after_items = after_resp.json()["pinned_items"]
        assert len(after_items) == 1
        assert after_items[0]["title"] == "กราฟของอีกเซสชัน"


class TestHealthAndProduction:
    """ทดสอบ Health Check Endpoint และ Production Readiness Configurations"""

    def test_health_check_endpoint(self):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"
        assert data["database"] == "connected"
        assert "app_name" in data
        assert "version" in data

    def test_rate_limiter_exempts_health_endpoint(self):
        # /health ต้องไม่ถูกนับในโควตา Rate Limit
        for _ in range(5):
            resp = client.get("/health")
            assert resp.status_code == 200

