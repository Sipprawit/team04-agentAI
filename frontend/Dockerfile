# ==========================================
# Frontend Multi-Stage Dockerfile (Vite React + Nginx)
# ==========================================

# --- Stage 1: Build Application ---
FROM node:20-alpine AS builder

WORKDIR /app

# ติดตั้ง Dependencies
COPY package.json package-lock.json* ./
RUN npm install

# คัดลอกซอร์สโค้ดและ Build โปรเจค
COPY . .

# Argument สำหรับ API Base URL (หากเว้นว่างไว้จะใช้ Relative Path ผ่าน Nginx Proxy)
ARG VITE_API_BASE_URL=""
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

RUN npm run build

# --- Stage 2: Serve with Nginx Alpine ---
FROM nginx:alpine

# คัดลอกไฟล์ Build ไปที่โฟลเดอร์ Web Root ของ Nginx
COPY --from=builder /app/dist /usr/share/nginx/html

# คัดลอกการตั้งค่า Nginx Reverse Proxy
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
