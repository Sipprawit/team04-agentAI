import React, { useState } from 'react';
import { uploadCsvFile } from '../../services/uploadService';

export default function FileUploadModal({ isOpen, onClose, onUploadSuccess }) {
  const [file, setFile] = useState(null);
  const [tableName, setTableName] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const [message, setMessage] = useState(null);

  if (!isOpen) return null;

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      // แนะนำชื่อตารางตามชื่อไฟล์ (ตัด .csv ออก)
      const baseName = selectedFile.name.replace(/\.[^/.]+$/, '').replace(/[^a-zA-Z0-9_]/g, '_').toLowerCase();
      if (!tableName) {
        setTableName(baseName);
      }
    }
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file || !tableName.trim()) {
      setMessage({ type: 'error', text: 'กรุณาเลือกไฟล์ CSV และระบุชื่อตาราง' });
      return;
    }

    setIsUploading(true);
    setMessage(null);

    try {
      const result = await uploadCsvFile(file, tableName.trim());
      setMessage({
        type: 'success',
        text: `✅ นำเข้าตาราง "${result.table_name}" สำเร็จ (${result.row_count} แถว)!`,
      });
      setTimeout(() => {
        if (onUploadSuccess) onUploadSuccess(result);
        onClose();
      }, 1500);
    } catch (err) {
      const errorDetail = err.response?.data?.detail || err.message || 'เกิดข้อผิดพลาดในการอัปโหลด';
      setMessage({ type: 'error', text: `❌ ${errorDetail}` });
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h3>📁 อัปโหลดไฟล์ CSV เข้าสู่ระบบ (Part 1: Data Integration)</h3>
          <button className="modal-close-btn" onClick={onClose}>&times;</button>
        </div>

        <form onSubmit={handleUpload} className="upload-form">
          <div className="form-group">
            <label>เลือกไฟล์ CSV (.csv เท่านั้น, สูงสุด 10MB):</label>
            <input
              type="file"
              accept=".csv"
              onChange={handleFileChange}
              disabled={isUploading}
            />
          </div>

          <div className="form-group">
            <label>ชื่อตารางในฐานข้อมูล (ภาษาอังกฤษ):</label>
            <input
              type="text"
              placeholder="เช่น sales_2024, inventory_q1"
              value={tableName}
              onChange={(e) => setTableName(e.target.value)}
              disabled={isUploading}
            />
          </div>

          {message && (
            <div className={`upload-message ${message.type}`}>
              {message.text}
            </div>
          )}

          <div className="modal-actions">
            <button type="button" className="btn-secondary" onClick={onClose} disabled={isUploading}>
              ยกเลิก
            </button>
            <button type="submit" className="btn-primary" disabled={isUploading || !file}>
              {isUploading ? 'กำลังประมวลผล & ตรวจจับโครงสร้าง...' : '🚀 อัปโหลดและสร้างตาราง'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
