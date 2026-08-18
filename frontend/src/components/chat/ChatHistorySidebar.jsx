import React from 'react';

export default function ChatHistorySidebar({ sessions, activeSession, onSelectSession, onNewChat, user }) {
  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <h2>👤 {user ? user.name : "ผู้ใช้งาน"}</h2>
        <button onClick={onNewChat} className="new-chat-btn">+ สนทนาใหม่</button>
      </div>

      <div className="history-section">
        <h3>💬 ประวัติการสนทนา</h3>
        <ul className="history-list">
          {sessions.map((sess) => (
            <li
              key={sess.id}
              className={`history-item ${activeSession === sess.id ? 'active' : ''}`}
              onClick={() => onSelectSession(sess.id)}
            >
              📌 {sess.title}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
