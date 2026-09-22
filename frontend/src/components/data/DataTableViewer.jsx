import React, { useState } from 'react';
import { Download, Table as TableIcon, ChevronLeft, ChevronRight } from 'lucide-react';

export default function DataTableViewer({
  data,
  title = "ตารางผลลัพธ์ข้อมูล",
}) {
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(25);

  if (!data || data.length === 0) {
    return (
      <div className="empty-table-state">
        <TableIcon size={36} className="empty-icon" />
        <p>ยังไม่มีข้อมูลตารางจากคำสั่ง SQL ล่าสุด</p>
      </div>
    );
  }

  const columns = Object.keys(data[0]);
  const effectivePageSize = pageSize === 0 ? data.length : pageSize;
  const totalPages = Math.ceil(data.length / effectivePageSize);
  const startIndex = (currentPage - 1) * effectivePageSize;
  const currentRows = data.slice(startIndex, startIndex + effectivePageSize);

  const handlePageSizeChange = (e) => {
    const val = Number(e.target.value);
    setPageSize(val);
    setCurrentPage(1);
  };

  const handleExportCsv = () => {
    if (!data || data.length === 0) return;
    const headers = columns.join(',');
    const rows = data.map(row =>
      columns.map(col => {
        let val = row[col];
        if (val === null || val === undefined) val = '';
        val = String(val).replace(/"/g, '""');
        return `"${val}"`;
      }).join(',')
    );
    const csvContent = '\uFEFF' + [headers, ...rows].join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `query_result_${Date.now()}.csv`;
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="data-table-container">
      <div className="data-table-header">
        <div className="table-title-group">
          <div className="table-title-main">
            <TableIcon size={18} className="table-title-icon text-blue-600" />
            <span className="table-title">{title}</span>
          </div>
          <span className="table-total-count-badge">{data.length.toLocaleString()} แถว</span>
        </div>

        <div className="table-header-actions-group">
          {/* Rows per page selector */}
          <div className="table-page-size-selector">
            <span className="page-size-label">แสดง:</span>
            <select
              value={pageSize}
              onChange={handlePageSizeChange}
              className="page-size-select"
            >
              <option value={10}>10 แถว</option>
              <option value={25}>25 แถว</option>
              <option value={50}>50 แถว</option>
              <option value={100}>100 แถว</option>
              <option value={0}>ทั้งหมด ({data.length})</option>
            </select>
          </div>

          {/* Export CSV Button */}
          <button onClick={handleExportCsv} className="table-export-btn" title="ดาวน์โหลดเป็นไฟล์ CSV">
            <Download size={14} />
            <span>ส่งออก CSV</span>
          </button>
        </div>
      </div>

      <div className="table-scroll-wrapper">
        <table className="custom-data-table">
          <thead>
            <tr>
              <th className="table-th-idx">#</th>
              {columns.map((col, idx) => (
                <th key={idx}>{col}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {currentRows.map((row, rIdx) => (
              <tr key={rIdx}>
                <td className="table-td-idx">{startIndex + rIdx + 1}</td>
                {columns.map((col, cIdx) => (
                  <td key={cIdx}>
                    {row[col] !== null && row[col] !== undefined
                      ? typeof row[col] === 'number'
                        ? row[col].toLocaleString()
                        : String(row[col])
                      : <span className="null-cell">-</span>}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {totalPages > 1 && (
        <div className="table-pagination">
          <span className="pagination-info">
            แสดงแถวที่ {startIndex + 1} - {Math.min(startIndex + effectivePageSize, data.length)} จากทั้งหมด {data.length.toLocaleString()} แถว (หน้า {currentPage}/{totalPages})
          </span>
          <div className="pagination-buttons">
            <button
              onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
              disabled={currentPage === 1}
              className="page-btn"
              title="หน้าก่อนหน้า"
            >
              <ChevronLeft size={16} />
            </button>
            <span className="current-page-display">{currentPage} / {totalPages}</span>
            <button
              onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
              disabled={currentPage === totalPages}
              className="page-btn"
              title="หน้าถัดไป"
            >
              <ChevronRight size={16} />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
