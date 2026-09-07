from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Query
import shutil
import os
import uuid
from sqlalchemy import text
from app.db.database import engine
from app.part1_data_security.integration.csv_uploader import upload_csv_to_db, validate_file_extension, ALLOWED_EXTENSIONS, sanitize_identifier
from app.part1_data_security.integration.schema_inspector import get_database_schema_info, get_schema_dict
from app.part1_data_security.sandbox.audit_logger import get_audit_logs, get_audit_stats

router = APIRouter(prefix="/part1", tags=["Part 1: Data & Security"])


@router.post("/upload-csv")
async def upload_csv(file: UploadFile = File(...), table_name: str = Form(...)):
    """
    อัปโหลดไฟล์ CSV และบันทึกลงฐานข้อมูล
    - ตรวจสอบนามสกุลไฟล์ (เฉพาะ .csv)
    - ใช้ UUID สำหรับชื่อไฟล์ temp ป้องกัน Path Traversal
    - ตรวจจับชนิดข้อมูลอัตโนมัติ (INTEGER, REAL, DATE, TEXT)
    """
    if not validate_file_extension(file.filename):
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Accepted: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "temp_uploads")
    os.makedirs(temp_dir, exist_ok=True)
    safe_filename = f"{uuid.uuid4().hex}.csv"
    file_path = os.path.join(temp_dir, safe_filename)

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        result = upload_csv_to_db(file_path, table_name)

        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])

        # ดึง 10 แถวแรกเป็น preview_data ให้ผู้ใช้กดดูได้ทันที
        clean_name = result["table_name"]
        preview_rows = []
        try:
            with engine.connect() as conn:
                res = conn.execute(text(f'SELECT * FROM "{clean_name}" LIMIT 10;'))
                preview_rows = [dict(row._mapping) for row in res]
        except Exception:
            pass

        result["preview_data"] = preview_rows
        return result
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)


@router.get("/tables/{table_name}/preview")
async def preview_table(table_name: str, limit: int = Query(default=10, ge=1, le=100)):
    """ดึงตัวอย่างข้อมูล N แถวแรกของตาราง"""
    clean_name = sanitize_identifier(table_name)
    try:
        with engine.connect() as conn:
            res = conn.execute(text(f'SELECT * FROM "{clean_name}" LIMIT :limit;'), {"limit": limit})
            rows = [dict(row._mapping) for row in res]
            total_count = conn.execute(text(f'SELECT COUNT(*) FROM "{clean_name}";')).scalar() or 0
        return {
            "table_name": clean_name,
            "total_rows": total_count,
            "preview_count": len(rows),
            "data": rows
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"ไม่พบตารางหรือเกิดข้อผิดพลาด: {str(e)}")


@router.get("/schema")
async def get_schema():
    """ดึงข้อมูลโครงสร้างตาราง (Schema Info)"""
    schema = get_database_schema_info()
    return {"schema": schema}


@router.get("/schema-dict")
async def get_schema_details():
    """ดึงโครงสร้างตารางในรูปแบบ JSON Object"""
    return get_schema_dict()


@router.get("/audit-logs")
async def get_logs(
    limit: int = Query(default=50, ge=1, le=500, description="Max number of logs to return"),
    status: str = Query(default=None, description="Filter by status: 'success' or 'error'")
):
    """ดึงประวัติ Audit Logs พร้อมกรองตาม status ได้"""
    if status and status not in ("success", "error"):
        raise HTTPException(status_code=400, detail="status must be 'success' or 'error'")
    logs = get_audit_logs(limit=limit, status_filter=status)
    return {"count": len(logs), "logs": logs}


@router.get("/audit-stats")
async def get_stats():
    """สรุปสถิติ Audit Logs (จำนวนทั้งหมด / สำเร็จ / ผิดพลาด)"""
    stats = get_audit_stats()
    return stats
