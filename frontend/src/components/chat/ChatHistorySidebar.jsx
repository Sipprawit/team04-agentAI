import React, { useState, useEffect } from 'react';
import { Plus, MessageSquare, Trash2, Bot, PanelLeftClose, PanelLeftOpen } from 'lucide-react';

export default function ChatHistorySidebar({
  isOpen,
  onToggle,
  sessions,
  activeSession,
  onSelectSession,
  onNewChat,
  onDeleteSession,
  user
}) {
  const [contextMenu, setContextMenu] = useState({ visible: false, x: 0, y: 0, sessionId: null });

  // Close context menu when clicking outside
  useEffect(() => {
    const handleOutsideClick = () => setContextMenu({ visible: false, x: 0, y: 0, sessionId: null });
    if (contextMenu.visible) {
      window.addEventListener('click', handleOutsideClick);
    }
    return () => window.removeEventListener('click', handleOutsideClick);
  }, [contextMenu.visible]);

  const handleContextMenu = (e, sessionId) => {
    e.preventDefault();
    e.stopPropagation();
    setContextMenu({
      visible: true,
      x: e.clientX,
      y: e.clientY,
      sessionId
    });
  };

  const handleDeleteFromMenu = (e) => {
    e.stopPropagation();
    if (contextMenu.sessionId && onDeleteSession) {
      onDeleteSession(contextMenu.sessionId);
    }
    setContextMenu({ visible: false, x: 0, y: 0, sessionId: null });
  };

  if (!isOpen) {
    return (
      <aside className="sidebar-collapsed">
        <button onClick={onToggle} className="sidebar-toggle-btn" title="เปิดแถบประวัติ (Sidebar)">
          <PanelLeftOpen size={18} />
        </button>
        <button onClick={onNewChat} className="sidebar-collapsed-new-btn" title="เริ่มสนทนาใหม่">
          <Plus size={18} />
        </button>
      </aside>
    );
  }

  return (
    <aside className="sidebar">
      {/* Brand Header with Close Toggle */}
      <div className="sidebar-brand">
        <div className="brand-title-group">
          <div className="brand-icon-wrapper">
            <Bot size={20} className="brand-icon" />
          </div>
          <div className="brand-text">
            <h2>DataAgent AI</h2>
            <span className="brand-badge">Team 04</span>
          </div>
        </div>
        <button onClick={onToggle} className="sidebar-close-toggle" title="ย่อแถบประวัติ">
          <PanelLeftClose size={18} />
        </button>
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
          <MessageSquare size={13} />
          <span>ประวัติการสนทนา (คลิกขวาเพื่อลบ)</span>
        </div>

        <div className="sessions-list">
          {sessions.map((sess) => (
            <div
              key={sess.id}
              className={`session-item ${activeSession === sess.id ? 'active' : ''}`}
              onClick={() => onSelectSession(sess.id)}
              onContextMenu={(e) => handleContextMenu(e, sess.id)}
              title="คลิกเพื่อเปิดบทสนทนานี้ หรือคลิกขวาเพื่อลบ"
            >
              <div className="session-item-content">
                <span className="session-title">{sess.title}</span>
                <span className="session-time">{sess.time || 'ล่าสุด'}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* User Footer Profile */}
      <div className="sidebar-footer">
        <div className="user-avatar">
          {user?.name ? user.name.slice(0, 2).toUpperCase() : '04'}
        </div>
        <div className="user-info">
          <span className="user-name">{user ? user.name : "ผู้ใช้งาน"}</span>
          <span className="user-status">● ระบบพร้อมใช้งาน</span>
        </div>
      </div>

      {/* Floating Right-Click Context Menu */}
      {contextMenu.visible && (
        <div
          className="context-menu-popup"
          style={{ top: `${contextMenu.y}px`, left: `${contextMenu.x}px` }}
          onClick={(e) => e.stopPropagation()}
        >
          <button className="context-menu-delete-btn" onClick={handleDeleteFromMenu}>
            <Trash2 size={14} className="text-red-500" />
            <span>ลบการสนทนานี้</span>
          </button>
        </div>
      )}
    </aside>
  );
}
