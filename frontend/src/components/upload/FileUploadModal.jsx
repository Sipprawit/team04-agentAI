import React, { useState, useEffect, useCallback } from 'react';
import {
  UploadCloud,
  FileSpreadsheet,
  CheckCircle2,
  AlertCircle,
  X,
  ArrowRight,
  Loader2,
  Database,
  Trash2,
  AlertTriangle,
  RefreshCw
} from 'lucide-react';
import { uploadCsvFile, fetchDatasets, deleteDatasetTable } from '../../services/uploadService';

export default function FileUploadModal({ isOpen, onClose, onUploadSuccess, onDatasetDeleted }) {
  const [activeTab, setActiveTab] = useState('upload'); // 'upload' | 'manage'
  const [file, setFile] = useState(null);
  const [tableName, setTableName] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const [isDragOver, setIsDragOver] = useState(false);
  const [message, setMessage] = useState(null);
  const [piiWarnings, setPiiWarnings] = useState([]);
  const [uploadResult, setUploadResult] = useState(null);

  // Datasets tab states
  const [datasets, setDatasets] = useState([]);
  const [isLoadingDatasets, setIsLoadingDatasets] = useState(false);
  const [deletingTable, setDeletingTable] = useState(null);
  const [confirmDeleteTable, setConfirmDeleteTable] = useState(null);

  const loadDatasets = useCallback(async () => {
    setIsLoadingDatasets(true);
    try {
      const res = await fetchDatasets();
      if (res && res.datasets) {
        setDatasets(res.datasets);
      }
    } catch {
      // Ignore or handle fallback
    } finally {
      setIsLoadingDatasets(false);
    }
  }, []);

  useEffect(() => {
    if (isOpen) {
      loadDatasets();
      // Reset upload states when opened
      setMessage(null);
      setPiiWarnings([]);
      setUploadResult(null);
      setConfirmDeleteTable(null);
    }
  }, [isOpen, loadDatasets]);

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
    setPiiWarnings([]);
    setFile(selectedFile);
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
    setPiiWarnings([]);

    try {
      const result = await uploadCsvFile(file, tableName.trim());
      setUploadResult(result);

      if (result.pii_warnings && result.pii_warnings.length > 0) {
        setPiiWarnings(result.pii_warnings);
        setMessage({
          type: 'warning',
          text: `นำเข้าตาราง "${result.table_name}" สำเร็จ (${result.row_count.toLocaleString()} แถว) แต่พบข้อมูลที่อาจเป็นข้อมูลส่วนบุคคล`,
        });
      } else {
        setMessage({
          type: 'success',
          text: `นำเข้าตาราง "${result.table_name}" สำเร็จ (${result.row_count.toLocaleString()} แถว)`,
        });
        setTimeout(() => {
          if (onUploadSuccess) onUploadSuccess(result);
          onClose();
        }, 1200);
      }
      loadDatasets();
    } catch (err) {
      const errorDetail = err.response?.data?.detail || err.message || 'เกิดข้อผิดพลาดในการประมวลผลไฟล์';
      setMessage({ type: 'error', text: errorDetail });
    } finally {
      setIsUploading(false);
    }
  };

  const handleProceedWithPii = () => {
    if (uploadResult && onUploadSuccess) {
      onUploadSuccess(uploadResult);
    }
    onClose();
  };

  const handleDeleteTable = async (targetTableName) => {
    setDeletingTable(targetTableName);
    try {
      await deleteDatasetTable(targetTableName);
      setConfirmDeleteTable(null);
      await loadDatasets();
      if (onDatasetDeleted) {
        onDatasetDeleted(targetTableName);
      }
    } catch (err) {
      const errDetail = err.response?.data?.detail || 'เกิดข้อผิดพลาดในการลบตาราง';
      alert(errDetail);
    } finally {
      setDeletingTable(null);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content modal-content-wide" onClick={(e) => e.stopPropagation()}>
        {/* Modal Header */}
        <div className="modal-header">
          <div className="modal-header-title-group">
            <div className="modal-icon-badge">
              {activeTab === 'upload' ? <UploadCloud size={18} /> : <Database size={18} />}
            </div>
            <div>
              <h3>จัดการชุดข้อมูล & นำเข้าไฟล์ (Dataset Management)</h3>
              <p className="modal-header-subtitle">แปลงข้อมูลเป็นตารางฐานข้อมูล SQLite และจัดการชุดข้อมูลที่มีอยู่ในระบบ</p>
            </div>
          </div>
          <button className="modal-close-btn" onClick={onClose} title="ปิดหน้าต่าง">
            <X size={16} />
          </button>
        </div>

        {/* Modal Tabs */}
        <div className="modal-tabs-header">
          <button
            type="button"
            className={`modal-tab-btn ${activeTab === 'upload' ? 'active' : ''}`}
            onClick={() => setActiveTab('upload')}
          >
            <UploadCloud size={14} />
            <span>นำเข้าไฟล์ CSV ใหม่</span>
          </button>
          <button
            type="button"
            className={`modal-tab-btn ${activeTab === 'manage' ? 'active' : ''}`}
            onClick={() => setActiveTab('manage')}
          >
            <Database size={14} />
            <span>ชุดข้อมูลในระบบ</span>
            <span className="modal-tab-badge">{datasets.length}</span>
          </button>
        </div>

        {/* TAB 1: Upload CSV Form */}
        {activeTab === 'upload' && (
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

            {/* Standard Upload Messages */}
            {message && !piiWarnings.length && (
              <div className={`upload-status-alert alert-${message.type}`}>
                {message.type === 'success' ? (
                  <CheckCircle2 size={16} className="text-emerald-500 flex-shrink-0" />
                ) : (
                  <AlertCircle size={16} className="text-red-500 flex-shrink-0" />
                )}
                <span>{message.text}</span>
              </div>
            )}

            {/* PII Detection Warning Alert Box */}
            {piiWarnings.length > 0 && (
              <div className="pii-warning-panel">
                <div className="pii-warning-title">
                  <AlertTriangle size={16} className="text-amber-600 flex-shrink-0" />
                  <strong>แจ้งเตือนข้อมูลส่วนบุคคล (PII Detection Warning)</strong>
                </div>
                <p className="pii-warning-desc">
                  ระบบตรวจพบคอลัมน์ที่มีลักษณะคล้ายข้อมูลระบุตัวบุคคล (PDPA):
                </p>
                <div className="pii-warning-tags">
                  {piiWarnings.map((w, idx) => (
                    <div key={idx} className="pii-tag-item">
                      <span className="pii-tag-type">
                        {w.type === 'citizen_id' ? 'เลขบัตร ปชช.' : w.type === 'phone_number' ? 'เบอร์โทรศัพท์' : 'อีเมล'}
                      </span>
                      <span className="pii-tag-column">{w.column}</span>
                    </div>
                  ))}
                </div>
                <p className="pii-warning-subhint">
                  นำเข้าตารางสำเร็จแล้ว โปรดใช้ความระมัดระวังในการแชร์หรือส่งออกข้อมูล
                </p>
                <button
                  type="button"
                  className="btn-primary pii-proceed-btn"
                  onClick={handleProceedWithPii}
                >
                  <span>รับทราบและเริ่มวิเคราะห์ข้อมูล</span>
                  <ArrowRight size={14} />
                </button>
              </div>
            )}

            {piiWarnings.length === 0 && (
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
            )}
          </form>
        )}

        {/* TAB 2: Datasets Management List */}
        {activeTab === 'manage' && (
          <div className="datasets-manage-panel">
            <div className="datasets-panel-header">
              <span className="datasets-count-label">
                ชุดข้อมูลที่พร้อมใช้งาน ({datasets.length} ตาราง)
              </span>
              <button
                type="button"
                className="datasets-refresh-btn"
                onClick={loadDatasets}
                disabled={isLoadingDatasets}
                title="รีเฟรชรายชื่อตาราง"
              >
                <RefreshCw size={13} className={isLoadingDatasets ? 'animate-spin' : ''} />
                <span>รีเฟรช</span>
              </button>
            </div>

            {isLoadingDatasets ? (
              <div className="datasets-loading-state">
                <Loader2 size={24} className="animate-spin text-blue-500" />
                <span>กำลังโหลดรายการชุดข้อมูล...</span>
              </div>
            ) : datasets.length === 0 ? (
              <div className="datasets-empty-state">
                <Database size={32} className="text-slate-300" />
                <p>ยังไม่มีชุดข้อมูลในระบบ</p>
                <button
                  type="button"
                  className="btn-secondary btn-sm"
                  onClick={() => setActiveTab('upload')}
                >
                  <UploadCloud size={13} />
                  <span>นำเข้าไฟล์ CSV ตอนนี้</span>
                </button>
              </div>
            ) : (
              <div className="datasets-list-container">
                {datasets.map((ds) => (
                  <div key={ds.table_name} className="dataset-item-row">
                    <div className="dataset-item-info">
                      <div className="dataset-item-header">
                        <span className="dataset-table-name">{ds.table_name}</span>
                        {ds.is_uploaded ? (
                          <span className="dataset-badge badge-uploaded">ตารางนำเข้า</span>
                        ) : (
                          <span className="dataset-badge badge-mock">ตารางตัวอย่าง</span>
                        )}
                      </div>
                      <div className="dataset-item-meta">
                        <span>{ds.row_count.toLocaleString()} แถว</span>
                        <span>•</span>
                        <span>{ds.columns.length} คอลัมน์ ({ds.columns.slice(0, 4).join(', ')}{ds.columns.length > 4 ? '...' : ''})</span>
                      </div>
                    </div>

                    <div className="dataset-item-actions">
                      {ds.is_deletable ? (
                        confirmDeleteTable === ds.table_name ? (
                          <div className="dataset-delete-confirm-group">
                            <span className="confirm-delete-text">ลบตาราง?</span>
                            <button
                              type="button"
                              className="btn-danger-confirm btn-sm"
                              onClick={() => handleDeleteTable(ds.table_name)}
                              disabled={deletingTable === ds.table_name}
                            >
                              {deletingTable === ds.table_name ? (
                                <Loader2 size={12} className="animate-spin" />
                              ) : (
                                'ยืนยัน'
                              )}
                            </button>
                            <button
                              type="button"
                              className="btn-cancel-confirm btn-sm"
                              onClick={() => setConfirmDeleteTable(null)}
                            >
                              ยกเลิก
                            </button>
                          </div>
                        ) : (
                          <button
                            type="button"
                            className="dataset-delete-btn"
                            onClick={() => setConfirmDeleteTable(ds.table_name)}
                            title={`ลบตาราง ${ds.table_name}`}
                          >
                            <Trash2 size={14} />
                            <span>ลบ</span>
                          </button>
                        )
                      ) : (
                        <span className="dataset-protected-label" title="ตารางระบบไม่สามารถลบได้">ตารางระบบ</span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
