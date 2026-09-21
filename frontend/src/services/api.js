import axios from 'axios';

const getBaseURL = () => {
  // หากมีการกำหนด VITE_API_BASE_URL ไว้อย่างชัดเจน (รวมถึงค่าว่าง "" สำหรับ Docker Nginx reverse proxy)
  if (import.meta.env.VITE_API_BASE_URL !== undefined && import.meta.env.VITE_API_BASE_URL !== null) {
    return import.meta.env.VITE_API_BASE_URL;
  }
  // ในโหมด Development ปกติ (npm run dev) ให้ยิงไปที่พอร์ต 8000
  return import.meta.env.DEV ? 'http://127.0.0.1:8000' : '';
};

const api = axios.create({
  baseURL: getBaseURL(),
  headers: {
    'Content-Type': 'application/json',
  },
});

export default api;
