import React from 'react';
import { Plus, MessageSquare, Database, Trash2, Bot, Sparkles } from 'lucide-react';

export default function ChatHistorySidebar({
  sessions,
  activeSession,
  onSelectSession,
  onNewChat,
  onDeleteSession,
  onOpenUpload,
  user
}) {
  return (
    <aside className="sidebar">
      {/* Brand Header */}
      <div className="sidebar-brand">
        <div className="brand-icon-wrapper">
          <Bot size={22} className="brand-icon" />
        </div>
        <div className="brand-text">
          <h2>DataAgent AI</h2>
          <span className="brand-badge">Team 04</span>
        </div>
      </div>

      {/* New Chat Action */}
      <div className="sidebar-action-container">
        <button onClick={onNewChat} className="new-chat-btn">
          <Plus size={16} />
          <span>เริ่มสนทนาใหม่</span>
        </button>
      </div>

      {/* Sessions / Conversation History */}
      <div className="sidebar-section">
        <div className="section-title">
          <MessageSquare size={14} />
          <span>ประวัติการสนทนา</span>
        </div>

        <div className="sessions-list">
          {sessions.map((sess) => (
            <div
              key={sess.id}
              className={`session-item ${activeSession === sess.id ? 'active' : ''}`}
              onClick={() => onSelectSession(sess.id)}
            >
              <div className="session-item-content">
                <span className="session-title">{sess.title}</span>
                <span className="session-time">{sess.time || 'ล่าสุด'}</span>
              </div>
              {sessions.length > 1 && onDeleteSession && (
                <button
                  className="delete-session-btn"
                  onClick={(e) => {
                    e.stopPropagation();
                    onDeleteSession(sess.id);
                  }}
                  title="ลบการสนทนานี้"
                >
                  <Trash2 size={13} />
                </button>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Quick Database / CSV Tool */}
      <div className="sidebar-quick-tool">
        <button onClick={onOpenUpload} className="quick-upload-btn">
          <Database size={15} />
          <span>อัปโหลดข้อมูล (CSV)</span>
        </button>
      </div>

      {/* User Footer Profile */}
      <div className="sidebar-footer">
        <div className="user-avatar">
          {user?.name ? user.name.slice(0, 2).toUpperCase() : '04'}
        </div>
        <div className="user-info">
          <span className="user-name">{user ? user.name : "ผู้ใช้งาน"}</span>
          <span className="user-status">● ระบบพร้อมวิเคราะห์</span>
        </div>
      </div>
    </aside>
  );
}
