# ==========================================
# Backend Dockerfile (FastAPI + Python 3.11)
# ==========================================
FROM python:3.11-slim

# ตั้งค่า Environment ให้ไม่บัฟเฟอร์ stdout/stderr และไม่สร้างไฟล์ .pyc
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# ติดตั้ง System dependencies ที่จำเป็น
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ติดตั้ง Python Dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# คัดลอกซอร์สโค้ดของแอปพลิเคชัน
COPY . .

# Expose พอร์ต 8000 สำหรับ FastAPI
EXPOSE 8000

# รัน Uvicorn ASGI Server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
