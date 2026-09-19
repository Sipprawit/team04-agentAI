import time
import os
from collections import defaultdict
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

# กำหนดโควตาสูงสุดต่อ IP ต่อ 1 นาที (Default 30 คำขอ/นาที)
RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "45"))
WINDOW_SECONDS = 60

# เก็บประวัติ timestamp ของแต่ละ Client IP: {ip: [ts1, ts2, ...]}
_IP_REQUEST_HISTORY = defaultdict(list)


def is_rate_limited(client_ip: str) -> tuple[bool, int]:
    """
    ตรวจสอบว่า Client IP เกินโควตาคำขอหรือไม่
    คืนค่า (is_blocked, seconds_to_wait)
    """
    now = time.time()
    history = _IP_REQUEST_HISTORY[client_ip]

    # กรองเฉพาะคำขอที่อยู่ในรอบ 60 วินาทีล่าสุด
    valid_history = [ts for ts in history if now - ts < WINDOW_SECONDS]
    _IP_REQUEST_HISTORY[client_ip] = valid_history

    if len(valid_history) >= RATE_LIMIT_PER_MINUTE:
        oldest_in_window = valid_history[0]
        retry_after = int(WINDOW_SECONDS - (now - oldest_in_window)) + 1
        return True, max(1, retry_after)

    valid_history.append(now)
    return False, 0


def clear_rate_limit_history():
    """ล้างประวัติการจำกัดคำขอ (สำหรับ Unit Testing)"""
    _IP_REQUEST_HISTORY.clear()


class ClientRateLimitMiddleware(BaseHTTPMiddleware):
    """
    FastAPI Middleware ตรวจสอบและจำกัดความถี่คำขอต่อ Client IP
    ป้องกันการสแปมและปกป้องโควตา Groq API ให้ใช้งานได้อย่างทั่วถึง
    """

    async def dispatch(self, request: Request, call_next):
        # ข้าม Static endpoints, OpenAPI docs, และ testclient
        path = request.url.path
        if path in ("/", "/docs", "/openapi.json", "/favicon.ico"):
            return await call_next(request)

        # ข้ามการตรวจสอบระหว่างรัน Unit Test อัตโนมัติ
        client_host = request.client.host if request.client else "unknown"
        if client_host in ("testclient", "127.0.0.1_bypass_test") or os.getenv("TESTING", "").lower() == "true":
            return await call_next(request)

        blocked, wait_sec = is_rate_limited(client_host)
        if blocked:
            return JSONResponse(
                status_code=429,
                content={
                    "status": "error",
                    "error_code": "RATE_LIMIT_EXCEEDED",
                    "detail": (
                        f"คุณส่งคำขอถี่เกินไป ({RATE_LIMIT_PER_MINUTE} ครั้ง/นาที) "
                        f"กรุณารอสักครู่ ({wait_sec} วินาที) ก่อนส่งใหม่อีกครั้งครับ"
                    ),
                    "retry_after_seconds": wait_sec
                },
                headers={"Retry-After": str(wait_sec)}
            )

        return await call_next(request)
