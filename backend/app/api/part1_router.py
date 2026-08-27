from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Query
import shutil
import os
from app.part1_data_security.integration.csv_uploader import upload_csv_to_db, validate_file_extension, ALLOWED_EXTENSIONS
from app.part1_data_security.integration.schema_inspector import get_database_schema_info
from app.part1_data_security.sandbox.audit_logger import get_audit_logs, get_audit_stats

router = APIRouter(prefix="/part1", tags=["Part 1: Data & Security"])


@router.post("/upload-csv")
async def upload_csv(file: UploadFile = File(...), table_name: str = Form(...)):
    """
    อัปโหลดไฟล์ CSV และบันทึกลงฐานข้อมูล
    - ตรวจสอบนามสกุลไฟล์ (เฉพาะ .csv)
    - ตรวจจับชนิดข้อมูลอัตโนมัติ (INTEGER, REAL, DATE, TEXT)
    """
    # --- ตรวจสอบนามสกุลไฟล์ก่อนบันทึก ---
    if not validate_file_extension(file.filename):
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Accepted: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    temp_dir = "temp_uploads"
    os.makedirs(temp_dir, exist_ok=True)
    file_path = os.path.join(temp_dir, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    result = upload_csv_to_db(file_path, table_name)

    # ลบไฟล์ temp เสมอ
    if os.path.exists(file_path):
        os.remove(file_path)

    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])

    return result


@router.get("/schema")
async def get_schema():
    """ดึงข้อมูลโครงสร้างตาราง (Schema Info)"""
    schema = get_database_schema_info()
    return {"schema": schema}


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
