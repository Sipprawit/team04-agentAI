import React, { useState } from 'react';
import { BarChart3, Table as TableIcon, Bookmark, Download, Pin, Sparkles, AlertCircle } from 'lucide-react';
import ChartRenderer from '../charts/ChartRenderer';
import DataTableViewer from '../data/DataTableViewer';

export default function AnalyticsPanel({
  activeMessage,
  pinnedItems,
  onPinItem,
  onUnpinItem,
}) {
  const [activeTab, setActiveTab] = useState('insights'); // 'insights' | 'table' | 'pinned'

  const hasVisualization = activeMessage?.visualization && activeMessage.visualization.recommended_chart !== 'none';
  const hasRawData = activeMessage?.rawData && activeMessage.rawData.length > 0;

  return (
    <div className="analytics-panel">
      {/* Tab Navigation */}
      <div className="analytics-tabs-header">
        <div className="analytics-tabs-group">
          <button
            className={`analytics-tab-btn ${activeTab === 'insights' ? 'active' : ''}`}
            onClick={() => setActiveTab('insights')}
          >
            <BarChart3 size={15} />
            <span>กราฟ & วิเคราะห์ล่าสุด</span>
          </button>

          <button
            className={`analytics-tab-btn ${activeTab === 'table' ? 'active' : ''}`}
            onClick={() => setActiveTab('table')}
          >
            <TableIcon size={15} />
            <span>ตารางข้อมูล ({activeMessage?.rawData?.length || 0})</span>
          </button>

          <button
            className={`analytics-tab-btn ${activeTab === 'pinned' ? 'active' : ''}`}
            onClick={() => setActiveTab('pinned')}
          >
            <Bookmark size={15} />
            <span>หน้าปัดที่ปักหมุด ({pinnedItems.length})</span>
          </button>
        </div>
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
                    <h3 className="active-chart-title">📊 รายงานภาพรวมเชิงสถิติ (Visual Report)</h3>
                    <p className="active-chart-subtitle">สร้างอัตโนมัติจากคำสั่ง SQL ล่าสุด</p>
                  </div>
                  {activeMessage && (
                    <button
                      className="pin-active-btn"
                      onClick={() => onPinItem(activeMessage)}
                      title="ปักหมุดกราฟนี้ลงหน้าปัดรวม"
                    >
                      <Pin size={14} />
                      <span>ปักหมุด</span>
                    </button>
                  )}
                </div>

                {/* Render the Recharts Visualization */}
                <div className="chart-render-box">
                  <ChartRenderer visualization={activeMessage.visualization} />
                </div>

                {/* Executive Summary Snippet */}
                {activeMessage.text && (
                  <div className="chart-summary-snippet">
                    <div className="snippet-title">
                      <Sparkles size={14} className="text-blue-500" />
                      <span>ข้อสังเกตและข้อสรุปสำคัญ</span>
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
                  <TableIcon size={32} className="text-blue-500" />
                  <h4>คำถามนี้แสดงผลเป็นตารางข้อมูล</h4>
                  <p>ข้อมูลชุดนี้เป็นรายการที่เหมาะสมกับการอ่านในรูปแบบตาราง คุณสามารถดูและส่งออกเป็นไฟล์ CSV ได้</p>
                  <button className="view-table-trigger-btn" onClick={() => setActiveTab('table')}>
                    <TableIcon size={14} />
                    <span>เปิดดูตารางข้อมูลดิบ ({activeMessage.rawData.length} แถว)</span>
                  </button>
                </div>
              </div>
            ) : (
              <div className="empty-insights-state">
                <div className="empty-state-content">
                  <BarChart3 size={44} className="empty-state-icon" />
                  <h4>หน้าต่างแสดงผลกราฟและรายงานแบบ Live</h4>
                  <p>เมื่อคุณพิมพ์คำถามวิเคราะห์ข้อมูล เช่น <em>"สรุปยอดขายรวมของสินค้าแต่ละชิ้น"</em> กราฟและการวิเคราะห์เชิงลึกจะปรากฏขึ้นที่นี่อัตโนมัติ</p>
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
              title={`ผลลัพธ์จาก SQL: ${activeMessage?.sql ? activeMessage.sql.slice(0, 40) + '...' : 'คำสั่งล่าสุด'}`}
            />
          </div>
        )}

        {/* TAB 3: Pinned Dashboard Grid */}
        {activeTab === 'pinned' && (
          <div className="pinned-dashboard-wrapper">
            <div className="pinned-header-actions">
              <div>
                <h3>📌 Dynamic Sales Dashboard</h3>
                <span className="pinned-count">ปักหมุดไว้ทั้งหมด {pinnedItems.length} รายการ</span>
              </div>
              {pinnedItems.length > 0 && (
                <button onClick={() => window.print()} className="print-report-btn">
                  <Download size={14} />
                  <span>พิมพ์รายงาน (PDF)</span>
                </button>
              )}
            </div>

            {pinnedItems.length === 0 ? (
              <div className="empty-pinned-box">
                <Bookmark size={36} className="empty-pinned-icon" />
                <p>ยังไม่มีรายการที่ปักหมุด</p>
                <span>กดปุ่ม 📌 บนการ์ดคำตอบหรือกราฟเพื่อนำมาบันทึกไว้ในหน้านี้</span>
              </div>
            ) : (
              <div className="pinned-grid">
                {pinnedItems.map((item) => (
                  <div key={item.id} className="pinned-card">
                    <div className="pinned-card-top">
                      <span className="pinned-card-title">📌 {item.title}</span>
                      <button
                        onClick={() => onUnpinItem(item.id)}
                        className="unpin-card-btn"
                        title="ปลดหมุด"
                      >
                        ✕
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
                          <summary>SQL Query</summary>
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
