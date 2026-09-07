# คู่มือการรันระบบด้วย Docker & Docker Compose
## โครงการ team04-agentAI

---

### 1. ข้อกำหนดเบื้องต้น (Prerequisites)
- มีโปรแกรม **Docker Desktop** (หรือ Docker Engine & Docker Compose) ติดตั้งอยู่บนเครื่อง และเปิดใช้งานอยู่
- มีไฟล์ `.env` ที่ระบุ `GROQ_API_KEY` อยู่ที่ root ของโฟลเดอร์ `backend/` หรือที่ root ของโปรเจค

---

### 2. ขั้นตอนการรันระบบ (Quick Start)

#### 2.1 คัดลอกและตั้งค่า Environment
คัดลอกไฟล์ `.env.example` ไปเป็น `.env` ที่ root ของโปรเจค:
```bash
cp .env.example .env
```
และระบุ `GROQ_API_KEY` ให้เรียบร้อย

#### 2.2 สั่ง Build และเริ่มต้นระบบ
รันคำสั่ง Docker Compose ที่โฟลเดอร์หลักของโปรเจค:
```bash
docker compose up --build -d
```
> คำสั่งนี้จะทำการ:
> 1. Build Backend (Python FastAPI) และเปิดพอร์ต `8000`
> 2. Build Frontend (React Vite) และเสิร์ฟผ่าน Nginx ที่พอร์ต `3000`
> 3. ทำ Nginx Reverse Proxy เชื่อมต่อระหว่างหน้าบ้านและหลังบ้านโดยอัตโนมัติ ไม่ติดปัญหา CORS
> 4. สร้าง Volume `team04_sqlite_data` เพื่อเก็บฐานข้อมูล SQLite ไม่ให้ประวัติแชทหาย

#### 2.3 เข้าใช้งานระบบผ่านเว็บเบราว์เซอร์
- **หน้าเว็บแอปพลิเคชัน (Frontend UI):** [http://localhost:3000](http://localhost:3000)
- **ระบบทดสอบ API เอกสาร (FastAPI Swagger UI):** [http://localhost:8000/docs](http://localhost:8000/docs)

---

### 3. คำสั่งที่ใช้บ่อย (Useful Commands)

- **ดูสถานะการทำงานของ Container:**
  ```bash
  docker compose ps
  ```

- **ดู Log การทำงาน (รวมทั้งสองบริการ):**
  ```bash
  docker compose logs -f
  ```

- **ดู Log เฉพาะ Backend:**
  ```bash
  docker compose logs -f backend
  ```

- **สั่งหยุดการทำงานของระบบ:**
  ```bash
  docker compose down
  ```

- **สั่งหยุดและลบ Volume ฐานข้อมูล (หากต้องการรีเซ็ตข้อมูลใหม่ทั้งหมด):**
  ```bash
  docker compose down -v
  ```

---

### 4. แนวทางการนำขึ้น Production Server (แนวทางที่ 1)
1. ติดตั้ง Docker บน Server (เช่น Ubuntu VPS):
   ```bash
   curl -fsSL https://get.docker.com -o get-docker.sh
   sh get-docker.sh
   ```
2. โคลน Git Repository ลงบน Server:
   ```bash
   git clone https://github.com/Sipprawit/team04-agentAI.git
   cd team04-agentAI
   ```
3. สร้างไฟล์ `.env` พร้อมใส่ API Key
4. หากต้องการให้เว็บรันที่พอร์ต 80 โดยตรง ให้เปลี่ยนใน `docker-compose.yml` จาก `"3000:80"` เป็น `"80:80"`
5. สั่งรันด้วยคำสั่ง:
   ```bash
   docker compose up -d --build
   ```
ระบบจะพร้อมให้บริการผ่าน IP Address หรือโดเมนของ Server ทันที
