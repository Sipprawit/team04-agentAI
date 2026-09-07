import React, { useState } from 'react';
import { UploadCloud, FileSpreadsheet, CheckCircle2, AlertCircle, X, ArrowRight, Loader2 } from 'lucide-react';
import { uploadCsvFile } from '../../services/uploadService';

export default function FileUploadModal({ isOpen, onClose, onUploadSuccess }) {
  const [file, setFile] = useState(null);
  const [tableName, setTableName] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const [isDragOver, setIsDragOver] = useState(false);
  const [message, setMessage] = useState(null);

  if (!isOpen) return null;

  const processSelectedFile = (selectedFile) => {
    if (!selectedFile) return;

    if (!selectedFile.name.toLowerCase().endsWith('.csv')) {
      setMessage({ type: 'error', text: 'ระบบรองรับเฉพาะไฟล์นามสกุล .csv เท่านั้น' });
      return;
    }

    if (selectedFile.size > 10 * 1024 * 1024) {
      setMessage({ type: 'error', text: 'ขนาดไฟล์เกินขีดจำกัดสูงสุด 10 MB' });
      return;
    }

    setMessage(null);
    setFile(selectedFile);
    // แนะนำชื่อตารางตามชื่อไฟล์ (ตัด .csv ออก)
    const baseName = selectedFile.name.replace(/\.[^/.]+$/, '').replace(/[^a-zA-Z0-9_]/g, '_').toLowerCase();
    if (!tableName) {
      setTableName(baseName);
    }
  };

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    processSelectedFile(selectedFile);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (!isDragOver) setIsDragOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      processSelectedFile(e.dataTransfer.files[0]);
    }
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file || !tableName.trim()) {
      setMessage({ type: 'error', text: 'กรุณาเลือกไฟล์ CSV และระบุชื่อตารางในฐานข้อมูล' });
      return;
    }

    setIsUploading(true);
    setMessage(null);

    try {
      const result = await uploadCsvFile(file, tableName.trim());
      setMessage({
        type: 'success',
        text: `นำเข้าตาราง "${result.table_name}" สำเร็จ (${result.row_count.toLocaleString()} แถว)`,
      });
      setTimeout(() => {
        if (onUploadSuccess) onUploadSuccess(result);
        onClose();
      }, 1200);
    } catch (err) {
      const errorDetail = err.response?.data?.detail || err.message || 'เกิดข้อผิดพลาดในการประมวลผลไฟล์';
      setMessage({ type: 'error', text: errorDetail });
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div className="modal-header-title-group">
            <div className="modal-icon-badge">
              <UploadCloud size={18} />
            </div>
            <div>
              <h3>นำเข้าไฟล์ชุดข้อมูล (CSV Data Import)</h3>
              <p className="modal-header-subtitle">แปลงข้อมูลเป็นตารางฐานข้อมูล SQLite พร้อมตรวจสอบชนิดข้อมูลอัตโนมัติ</p>
            </div>
          </div>
          <button className="modal-close-btn" onClick={onClose} title="ปิดหน้าต่าง">
            <X size={16} />
          </button>
        </div>

        <form onSubmit={handleUpload} className="upload-form">
          <div className="form-group">
            <label className="form-label">
              <span>ไฟล์ข้อมูล CSV</span>
              <span className="form-label-hint">(รองรับ UTF-8 / Windows CP-874 / TIS-620 ขนาดสูงสุด 10 MB)</span>
            </label>
            <div
              className={`file-dropzone ${isDragOver ? 'drag-active' : ''}`}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
            >
              <input
                type="file"
                id="csvFileInput"
                accept=".csv"
                onChange={handleFileChange}
                disabled={isUploading}
                className="file-native-input"
              />
              <label htmlFor="csvFileInput" className="file-dropzone-label">
                <FileSpreadsheet size={24} className={isDragOver ? 'text-blue-600' : 'text-blue-500'} />
                <span className="dropzone-text">
                  {file ? file.name : isDragOver ? 'ปล่อยไฟล์ CSV เพื่ออัปโหลด' : 'ลากไฟล์ CSV มาวางที่นี่ หรือคลิกเพื่อเลือกไฟล์'}
                </span>
                {file && (
                  <span className="dropzone-subtext">
                    {(file.size / 1024).toFixed(1)} KB
                  </span>
                )}
              </label>
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">
              <span>ชื่อตารางในฐานข้อมูล (Table Identifier)</span>
              <span className="form-label-hint">(อักษรภาษาอังกฤษ ตัวเลข และขีดล่าง)</span>
            </label>
            <input
              type="text"
              placeholder="ตัวอย่าง: sales_data, inventory_survey"
              value={tableName}
              onChange={(e) => setTableName(e.target.value)}
              disabled={isUploading}
              className="form-text-input"
            />
          </div>

          {message && (
            <div className={`upload-status-alert alert-${message.type}`}>
              {message.type === 'success' ? (
                <CheckCircle2 size={16} className="text-emerald-500 flex-shrink-0" />
              ) : (
                <AlertCircle size={16} className="text-red-500 flex-shrink-0" />
              )}
              <span>{message.text}</span>
            </div>
          )}

          <div className="modal-actions">
            <button type="button" className="btn-secondary" onClick={onClose} disabled={isUploading}>
              ยกเลิก
            </button>
            <button type="submit" className="btn-primary" disabled={isUploading || !file}>
              {isUploading ? (
                <>
                  <Loader2 size={15} className="animate-spin" />
                  <span>กำลังนำเข้าและประมวลผล...</span>
                </>
              ) : (
                <>
                  <span>นำเข้าข้อมูล</span>
                  <ArrowRight size={14} />
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
