from fastapi import APIRouter, UploadFile, File, Form, HTTPException
import shutil
import os
from app.part1_data_security.integration.csv_uploader import upload_csv_to_db
from app.part1_data_security.integration.schema_inspector import get_database_schema_info

router = APIRouter(prefix="/part1", tags=["Part 1: Data & Security"])

@router.post("/upload-csv")
async def upload_csv(file: UploadFile = File(...), table_name: str = Form(...)):
    """อัปโหลดไฟล์ CSV และบันทึกลงฐานข้อมูล"""
    temp_dir = "temp_uploads"
    os.makedirs(temp_dir, exist_ok=True)
    file_path = os.path.join(temp_dir, file.filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    result = upload_csv_to_db(file_path, table_name)
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
