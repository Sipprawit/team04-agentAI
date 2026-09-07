import React, { useState } from 'react';
import {
  BarChart3,
  Table as TableIcon,
  Bookmark,
  Download,
  Pin,
  Sparkles,
  PanelRightClose,
  X
} from 'lucide-react';
import ChartRenderer from '../charts/ChartRenderer';
import DataTableViewer from '../data/DataTableViewer';

export default function AnalyticsPanel({
  activeMessage,
  pinnedItems,
  onPinItem,
  onUnpinItem,
  onClose,
}) {
  const [activeTab, setActiveTab] = useState('insights'); // 'insights' | 'table' | 'pinned'

  const hasVisualization = activeMessage?.visualization && activeMessage.visualization.recommended_chart !== 'none';
  const hasRawData = activeMessage?.rawData && activeMessage.rawData.length > 0;
  const userQuestion = activeMessage?.userQuery || activeMessage?.text?.split('\n')[0] || "คำถามล่าสุด";

  // ฟังก์ชันดาวน์โหลด CSV แบบ UTF-8 BOM สำหรับเปิดใน Excel
  const handleExportCsv = (dataToExport, fileNamePrefix = "query_data") => {
    if (!dataToExport || dataToExport.length === 0) return;
    const columns = Object.keys(dataToExport[0]);
    const headers = columns.join(',');
    const rows = dataToExport.map(row =>
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
    link.download = `${fileNamePrefix}_${Date.now()}.csv`;
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="analytics-panel">
      {/* Tab Navigation with Close Toggle */}
      <div className="analytics-tabs-header">
        <div className="analytics-tabs-group">
          <button
            className={`analytics-tab-btn ${activeTab === 'insights' ? 'active' : ''}`}
            onClick={() => setActiveTab('insights')}
          >
            <BarChart3 size={14} />
            <span>รายงานวิเคราะห์</span>
          </button>

          <button
            className={`analytics-tab-btn ${activeTab === 'table' ? 'active' : ''}`}
            onClick={() => setActiveTab('table')}
          >
            <TableIcon size={14} />
            <span>ตารางข้อมูล</span>
            {activeMessage?.rawData?.length > 0 && (
              <span className="tab-count-badge">{activeMessage.rawData.length}</span>
            )}
          </button>

          <button
            className={`analytics-tab-btn ${activeTab === 'pinned' ? 'active' : ''}`}
            onClick={() => setActiveTab('pinned')}
          >
            <Bookmark size={14} />
            <span>หน้าปัดบันทึก</span>
            {pinnedItems.length > 0 && (
              <span className="tab-count-badge">{pinnedItems.length}</span>
            )}
          </button>
        </div>

        {onClose && (
          <button onClick={onClose} className="panel-close-toggle" title="ปิดแผงการแสดงผล">
            <PanelRightClose size={16} />
          </button>
        )}
      </div>

      {/* Tab Content */}
      <div className="analytics-tab-content">
        {/* TAB 1: Live Insights & Chart */}
        {activeTab === 'insights' && (
          <div className="insights-view-container">
            {hasVisualization ? (
              <div className="active-chart-card">
                <div className="active-chart-header">
                  <div>
                    <h3 className="active-chart-title">รายงานการวิเคราะห์เชิงสถิติ</h3>
                    <p className="active-chart-subtitle">อ้างอิงคำถาม: "{userQuestion}"</p>
                  </div>
                  <div className="chart-header-actions">
                    {hasRawData && (
                      <button
                        className="btn-export-quick"
                        onClick={() => handleExportCsv(activeMessage.rawData, "analytics_report")}
                        title="ส่งออกชุดข้อมูลเป็นไฟล์ CSV สำหรับ Excel"
                      >
                        <Download size={13} />
                        <span>ส่งออก CSV</span>
                      </button>
                    )}
                    {activeMessage && (
                      <button
                        className="pin-active-btn"
                        onClick={() => onPinItem(activeMessage)}
                        title="ปักหมุดรายงานนี้ไว้ในแดชบอร์ด"
                      >
                        <Pin size={13} />
                        <span>ปักหมุด</span>
                      </button>
                    )}
                  </div>
                </div>

                {/* Render the Recharts Visualization with Switcher */}
                <div className="chart-render-box">
                  <ChartRenderer visualization={activeMessage.visualization} />
                </div>

                {/* Executive Summary Snippet */}
                {activeMessage.text && (
                  <div className="chart-summary-snippet">
                    <div className="snippet-title">
                      <Sparkles size={14} className="text-blue-600" />
                      <span>ข้อสรุปและประเด็นสำคัญสำหรับผู้บริหาร</span>
                    </div>
                    <div className="snippet-text">
                      {activeMessage.text}
                    </div>
                  </div>
                )}
              </div>
            ) : hasRawData ? (
              <div className="no-chart-info-box">
                <div className="info-card">
                  <div className="info-icon-badge">
                    <TableIcon size={24} className="text-blue-600" />
                  </div>
                  <h4>ผลการสืบค้นข้อมูล</h4>
                  <p className="info-card-desc">ชุดข้อมูลนี้แสดงผลได้เหมาะสมที่สุดในรูปแบบตาราง ท่านสามารถเปิดดูและส่งออกเป็นไฟล์สเปรดชีตได้</p>
                  <div className="info-card-actions">
                    <button className="view-table-trigger-btn" onClick={() => setActiveTab('table')}>
                      <TableIcon size={14} />
                      <span>เปิดดูตารางข้อมูล ({activeMessage.rawData.length} รายการ)</span>
                    </button>
                    <button
                      className="export-table-trigger-btn"
                      onClick={() => handleExportCsv(activeMessage.rawData, "query_result")}
                    >
                      <Download size={14} />
                      <span>ส่งออกไฟล์ CSV</span>
                    </button>
                  </div>
                </div>
              </div>
            ) : (
              <div className="empty-insights-state">
                <div className="empty-state-content">
                  <div className="empty-state-icon-box">
                    <BarChart3 size={36} />
                  </div>
                  <h4>แผงแสดงผลกราฟและรายงานวิเคราะห์</h4>
                  <p>เมื่อท่านพิมพ์ข้อความสอบถามหรือวิเคราะห์ข้อมูล แผนภูมิสถิติและข้อสรุปเชิงลึกจะปรากฏบนหน้านี้โดยอัตโนมัติ</p>
                </div>
              </div>
            )}
          </div>
        )}

        {/* TAB 2: Raw SQL Data Table Viewer */}
        {activeTab === 'table' && (
          <div className="table-view-container">
            <DataTableViewer
              data={activeMessage?.rawData || []}
              title={`ผลการสืบค้น: "${userQuestion}"`}
            />
          </div>
        )}

        {/* TAB 3: Pinned Dashboard Grid */}
        {activeTab === 'pinned' && (
          <div className="pinned-dashboard-wrapper">
            <div className="pinned-header-actions">
              <div>
                <h3>แดชบอร์ดสรุปผลที่บันทึกไว้</h3>
                <span className="pinned-count">บันทึกไว้ทั้งหมด {pinnedItems.length} รายการ</span>
              </div>
              {pinnedItems.length > 0 && (
                <button onClick={() => window.print()} className="print-report-btn">
                  <Download size={13} />
                  <span>พิมพ์รายงาน (PDF)</span>
                </button>
              )}
            </div>

            {pinnedItems.length === 0 ? (
              <div className="empty-pinned-box">
                <div className="empty-pinned-icon-box">
                  <Bookmark size={28} />
                </div>
                <p className="empty-pinned-title">ยังไม่มีรายการที่ปักหมุด</p>
                <span className="empty-pinned-desc">กดปุ่ม "ปักหมุด" บนการ์ดคำตอบหรือกราฟเพื่อนำมาจัดเก็บบนหน้านี้</span>
              </div>
            ) : (
              <div className="pinned-grid">
                {pinnedItems.map((item) => (
                  <div key={item.id} className="pinned-card">
                    <div className="pinned-card-top">
                      <span className="pinned-card-title">{item.title}</span>
                      <button
                        onClick={() => onUnpinItem(item.id)}
                        className="unpin-card-btn"
                        title="นำรายการนี้ออก"
                      >
                        <X size={14} />
                      </button>
                    </div>

                    {item.visualization && (
                      <div className="pinned-chart-container">
                        <ChartRenderer visualization={item.visualization} />
                      </div>
                    )}

                    <div className="pinned-card-body">
                      <div className="pinned-text">{item.content}</div>
                      {item.sql && (
                        <details className="pinned-sql-box">
                          <summary>คำสั่ง SQL ที่ใช้ประมวลผล</summary>
                          <code>{item.sql}</code>
                        </details>
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
