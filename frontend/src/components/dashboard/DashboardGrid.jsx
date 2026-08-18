import React from 'react';

export default function DashboardGrid({ pinnedItems, onUnpin }) {
  if (!pinnedItems || pinnedItems.length === 0) {
    return (
      <div className="empty-dashboard">
        <h2>📊 หน้าปัดรายงานพลวัต (Dynamic Dashboard)</h2>
        <p>ยังไม่มีรายการที่ปักหมุด คุณสามารถกดปุ่ม 📌 ปักหมุด บนการ์ดคำตอบในหน้าแชท เพื่อนำมาจัดเรียงรายงานตรงนี้ได้ครับ!</p>
      </div>
    );
  }

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <h2>📊 Dynamic Sales Dashboard</h2>
        <button onClick={() => alert("ระบบกำลังส่งออกรายงาน PDF/Image...")} className="export-btn">
          📥 Export รายงาน
        </button>
      </div>

      <div className="dashboard-grid">
        {pinnedItems.map((item, idx) => (
          <div key={idx} className="dashboard-card">
            <div className="card-top">
              <span className="card-title">📌 {item.title || "รายการปักหมุด"}</span>
              <button onClick={() => onUnpin(item.id)} className="unpin-btn">❌ ปลดหมุด</button>
            </div>
            <div className="card-content">
              <pre>{item.content}</pre>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
