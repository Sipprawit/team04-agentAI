import React, { useState } from 'react';
import { Download, Table as TableIcon, ChevronLeft, ChevronRight } from 'lucide-react';

export default function DataTableViewer({ data, title = "ตารางผลลัพธ์ข้อมูล" }) {
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 8;

  if (!data || data.length === 0) {
    return (
      <div className="empty-table-state">
        <TableIcon size={36} className="empty-icon" />
        <p>ยังไม่มีข้อมูลตารางจากคำสั่ง SQL ล่าสุด</p>
      </div>
    );
  }

  const columns = Object.keys(data[0]);
  const totalPages = Math.ceil(data.length / pageSize);
  const startIndex = (currentPage - 1) * pageSize;
  const currentRows = data.slice(startIndex, startIndex + pageSize);

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
          <TableIcon size={18} className="text-blue-600" />
          <span className="table-title">{title} ({data.length} แถว)</span>
        </div>
        <button onClick={handleExportCsv} className="table-export-btn" title="ดาวน์โหลดเป็นไฟล์ CSV">
          <Download size={14} />
          <span>ส่งออก CSV</span>
        </button>
      </div>

      <div className="table-scroll-wrapper">
        <table className="custom-data-table">
          <thead>
            <tr>
              {columns.map((col, idx) => (
                <th key={idx}>{col}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {currentRows.map((row, rIdx) => (
              <tr key={rIdx}>
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
            แสดงหน้า {currentPage} จากทั้งหมด {totalPages} หน้า
          </span>
          <div className="pagination-buttons">
            <button
              onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
              disabled={currentPage === 1}
              className="page-btn"
            >
              <ChevronLeft size={16} />
            </button>
            <button
              onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
              disabled={currentPage === totalPages}
              className="page-btn"
            >
              <ChevronRight size={16} />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
