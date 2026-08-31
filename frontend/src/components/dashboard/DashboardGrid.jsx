import React from 'react';
import ChartRenderer from '../charts/ChartRenderer';

export default function DashboardGrid({ pinnedItems, onUnpin }) {
  if (!pinnedItems || pinnedItems.length === 0) {
    return (
      <div className="empty-dashboard">
        <h2>📊 หน้าปัดรายงานพลวัต (Dynamic Dashboard)</h2>
        <p>ยังไม่มีรายการที่ปักหมุด คุณสามารถกดปุ่ม 📌 ปักหมุด บนการ์ดคำตอบในหน้าแชท เพื่อนำกราฟและข้อความสรุปมาจัดเรียงรายงานตรงนี้ได้ครับ!</p>
      </div>
    );
  }

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <div>
          <h2>📊 Dynamic Sales Dashboard</h2>
          <p className="dashboard-subtitle">รวบรวมกราฟและข้อมูลวิเคราะห์สำคัญที่ปักหมุดไว้ ({pinnedItems.length} รายการ)</p>
        </div>
        <button onClick={() => window.print()} className="export-btn">
          📥 พิมพ์ / ส่งออกเป็น PDF
        </button>
      </div>

      <div className="dashboard-grid">
        {pinnedItems.map((item, idx) => (
          <div key={item.id || idx} className="dashboard-card">
            <div className="card-top">
              <span className="card-title">📌 {item.title || "รายการวิเคราะห์"}</span>
              <button onClick={() => onUnpin(item.id)} className="unpin-btn" title="ปลดหมุด">
                ✕
              </button>
            </div>
            
            {/* แสดงกราฟถ้ามีการปักหมุดกราฟ */}
            {item.visualization && (
              <div className="dashboard-chart-area">
                <ChartRenderer visualization={item.visualization} />
              </div>
            )}

            <div className="card-content">
              <div className="card-text-summary">{item.content}</div>
              {item.sql && (
                <details className="dashboard-sql-details">
                  <summary>ดูคำสั่ง SQL</summary>
                  <code>{item.sql}</code>
                </details>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
