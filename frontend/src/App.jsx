import React, { useState, useEffect, useRef } from 'react';
import {
  Send,
  Sparkles,
  Bot,
  User,
  Database,
  Code,
  Pin,
  AlertCircle,
  RefreshCw,
  Table as TableIcon,
  CheckCircle2,
  Trash2
} from 'lucide-react';
import { sendQuery } from './services/chatService';
import { getPinnedDashboard, pinItemToDashboard, unpinItem } from './services/dashboardService';
import ChatHistorySidebar from './components/chat/ChatHistorySidebar';
import AnalyticsPanel from './components/dashboard/AnalyticsPanel';
import MarkdownMessage from './components/chat/MarkdownMessage';
import FileUploadModal from './components/upload/FileUploadModal';
import './App.css';

const LOCAL_STORAGE_SESSIONS_KEY = 'team04_chat_sessions_v2';
const LOCAL_STORAGE_MESSAGES_KEY = 'team04_chat_messages_v2';
const LOCAL_STORAGE_PINNED_KEY = 'team04_pinned_dashboard_v2';

const SUGGESTED_QUERIES = [
  'แสดงรายชื่อสินค้าทั้งหมด',
  'สรุปยอดขายรวมของสินค้าแต่ละชิ้น',
  'ลูกค้า 5 อันดับแรกที่มียอดสั่งซื้อสูงสุด',
  'สินค้าที่ขายดีที่สุดและยอดขายรวม',
];

const LOADING_STAGES = [
  '🤖 AI Core กำลังวิเคราะห์คำถามและแปลงเป็นคำสั่ง SQL...',
  '🛡️ รันคำสั่งใน Secure Sandbox และตรวจสอบความปลอดภัย...',
  '📊 วิเคราะห์ข้อมูลเชิงสถิติและจัดเตรียมแผนภูมิ...'
];

export default function App() {
  // 1. Session & History Persistence
  const [sessions, setSessions] = useState(() => {
    try {
      const saved = localStorage.getItem(LOCAL_STORAGE_SESSIONS_KEY);
      if (saved) return JSON.parse(saved);
    } catch (e) {}
    return [{ id: 'session_default', title: 'วิเคราะห์ยอดขาย E-Commerce', time: 'วันนี้' }];
  });

  const [activeSession, setActiveSession] = useState(() => {
    try {
      const saved = localStorage.getItem(LOCAL_STORAGE_SESSIONS_KEY);
      if (saved) {
        const parsed = JSON.parse(saved);
        if (parsed.length > 0) return parsed[0].id;
      }
    } catch (e) {}
    return 'session_default';
  });

  const [messagesBySession, setMessagesBySession] = useState(() => {
    try {
      const saved = localStorage.getItem(LOCAL_STORAGE_MESSAGES_KEY);
      if (saved) return JSON.parse(saved);
    } catch (e) {}
    return {
      session_default: [
        {
          id: 'welcome',
          role: 'ai',
          text: 'สวัสดีครับ! ผมคือ **Data Analyst AI Assistant** 🚀\n\nยินดีช่วยเหลือในการค้นหาข้อมูล สรุปยอดขาย และสร้างกราฟวิเคราะห์เชิงลึก คุณสามารถเลือกคำถามแนะนำด้านล่าง หรือพิมพ์ถามได้ทันทีครับ!',
          sql: null,
          visualization: null,
          rawData: [],
          timestamp: new Date().toLocaleTimeString('th-TH', { hour: '2-digit', minute: '2-digit' })
        }
      ]
    };
  });

  // 2. Pinned Items Persistence
  const [pinnedItems, setPinnedItems] = useState(() => {
    try {
      const saved = localStorage.getItem(LOCAL_STORAGE_PINNED_KEY);
      if (saved) return JSON.parse(saved);
    } catch (e) {}
    return [];
  });

  // 3. UI States
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [loadingStageIdx, setLoadingStageIdx] = useState(0);
  const [errorBanner, setErrorBanner] = useState(null);
  const [isUploadOpen, setIsUploadOpen] = useState(false);
  const [activeMessage, setActiveMessage] = useState(null);

  const messagesEndRef = useRef(null);
  const user = { name: 'ทีม 04 Data Analyst' };

  // Current session messages
  const currentMessages = messagesBySession[activeSession] || [];

  // Update activeMessage to latest AI message if not set
  useEffect(() => {
    if (currentMessages.length > 0) {
      const lastAiMsg = [...currentMessages].reverse().find(m => m.role === 'ai' && (m.visualization || (m.rawData && m.rawData.length > 0)));
      if (lastAiMsg) {
        setActiveMessage(lastAiMsg);
      }
    }
  }, [activeSession, messagesBySession]);

  // Save to localStorage when state updates
  useEffect(() => {
    try {
      localStorage.setItem(LOCAL_STORAGE_SESSIONS_KEY, JSON.stringify(sessions));
      localStorage.setItem(LOCAL_STORAGE_MESSAGES_KEY, JSON.stringify(messagesBySession));
      localStorage.setItem(LOCAL_STORAGE_PINNED_KEY, JSON.stringify(pinnedItems));
    } catch (e) {}
  }, [sessions, messagesBySession, pinnedItems]);

  // Auto scroll chat
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [currentMessages, isLoading]);

  // Multi-phase loading animation timer
  useEffect(() => {
    let interval;
    if (isLoading) {
      setLoadingStageIdx(0);
      interval = setInterval(() => {
        setLoadingStageIdx(prev => (prev + 1) % LOADING_STAGES.length);
      }, 1800);
    }
    return () => clearInterval(interval);
  }, [isLoading]);

  // Handle Send Query
  const handleSendMessage = async (e, queryTextOverride = null) => {
    if (e) e.preventDefault();
    const queryToSend = queryTextOverride || input;
    if (!queryToSend.trim() || isLoading) return;

    const userMessage = {
      id: `usr_${Date.now()}`,
      role: 'user',
      text: queryToSend.trim(),
      timestamp: new Date().toLocaleTimeString('th-TH', { hour: '2-digit', minute: '2-digit' })
    };

    // Update messages in current session
    setMessagesBySession(prev => ({
      ...prev,
      [activeSession]: [...(prev[activeSession] || []), userMessage]
    }));

    setInput('');
    setIsLoading(true);
    setErrorBanner(null);

    try {
      // Send last 5 messages as context
      const historyContext = (currentMessages.slice(-5) || []).map(m => ({
        role: m.role,
        text: m.text
      }));

      const data = await sendQuery(userMessage.text, historyContext);

      const aiMessage = {
        id: `ai_${Date.now()}`,
        role: 'ai',
        text: data.response || 'ประมวลผลข้อมูลเรียบร้อยแล้ว',
        sql: data.sql || null,
        visualization: data.visualization || null,
        rawData: data.data || [],
        timestamp: new Date().toLocaleTimeString('th-TH', { hour: '2-digit', minute: '2-digit' })
      };

      setMessagesBySession(prev => ({
        ...prev,
        [activeSession]: [...(prev[activeSession] || []), aiMessage]
      }));

      // Update active insight on right panel
      setActiveMessage(aiMessage);

      // Auto update session title if default
      if (sessions.find(s => s.id === activeSession)?.title === 'วิเคราะห์ยอดขาย E-Commerce' && currentMessages.length <= 2) {
        const shortTitle = queryToSend.length > 28 ? queryToSend.slice(0, 28) + '...' : queryToSend;
        setSessions(prev => prev.map(s => s.id === activeSession ? { ...s, title: shortTitle } : s));
      }
    } catch (error) {
      console.error("Query execution error:", error);
      const errorMsg = error.response?.data?.message || error.response?.data?.detail || error.message || "ไม่สามารถเชื่อมต่อกับเซิร์ฟเวอร์ได้ กรุณาตรวจสอบการเชื่อมต่อ Backend";
      
      const errorAiMsg = {
        id: `err_${Date.now()}`,
        role: 'ai',
        isError: true,
        text: `⚠️ **เกิดข้อผิดพลาดในการประมวลผล**\n\n${errorMsg}\n\n*ข้อแนะนำ: ลองพิมพ์คำถามใหม่ให้ชัดเจนขึ้น หรือระบุชื่อตารางที่ต้องการค้นหา เช่น "แสดงรายชื่อสินค้า"*`,
        sql: null,
        visualization: null,
        rawData: [],
        timestamp: new Date().toLocaleTimeString('th-TH', { hour: '2-digit', minute: '2-digit' })
      };

      setMessagesBySession(prev => ({
        ...prev,
        [activeSession]: [...(prev[activeSession] || []), errorAiMsg]
      }));

      setErrorBanner(errorMsg);
    } finally {
      setIsLoading(false);
    }
  };

  // Pin / Unpin Dashboard
  const handlePinItem = async (msg) => {
    if (!msg) return;
    const newItem = {
      id: Date.now(),
      title: `วิเคราะห์ (${msg.timestamp || new Date().toLocaleTimeString('th-TH')})`,
      content: msg.text,
      sql: msg.sql,
      visualization: msg.visualization,
      rawData: msg.rawData,
    };

    try {
      await pinItemToDashboard(newItem);
    } catch (e) {}

    setPinnedItems(prev => [newItem, ...prev]);
    alert("📌 ปักหมุดรายการนี้ลงบน Dashboard เรียบร้อยแล้ว!");
  };

  const handleUnpinItem = async (id) => {
    try {
      await unpinItem(id);
    } catch (e) {}
    setPinnedItems(prev => prev.filter(item => item.id !== id));
  };

  // New Chat Session
  const handleNewChat = () => {
    const newId = `session_${Date.now()}`;
    const newSession = {
      id: newId,
      title: `การสนทนาใหม่ ${sessions.length + 1}`,
      time: 'เพิ่งสร้าง'
    };

    setSessions(prev => [newSession, ...prev]);
    setActiveSession(newId);
    setMessagesBySession(prev => ({
      ...prev,
      [newId]: [
        {
          id: `welcome_${Date.now()}`,
          role: 'ai',
          text: 'สวัสดีครับ! เริ่มต้นหัวข้อการสนทนาใหม่ คุณต้องการให้ช่วยวิเคราะห์ข้อมูลส่วนไหน สอบถามได้เลยครับ 🚀',
          sql: null,
          visualization: null,
          rawData: [],
          timestamp: new Date().toLocaleTimeString('th-TH', { hour: '2-digit', minute: '2-digit' })
        }
      ]
    }));
    setActiveMessage(null);
  };

  // Delete Session
  const handleDeleteSession = (sessId) => {
    if (sessions.length <= 1) {
      alert("ต้องมีบทสนทนาอย่างน้อย 1 รายการครับ");
      return;
    }
    const remaining = sessions.filter(s => s.id !== sessId);
    setSessions(remaining);
    if (activeSession === sessId) {
      setActiveSession(remaining[0].id);
    }
    setMessagesBySession(prev => {
      const copy = { ...prev };
      delete copy[sessId];
      return copy;
    });
  };

  // Clear current chat
  const handleClearCurrentChat = () => {
    if (window.confirm("คุณต้องการล้างข้อความทั้งหมดในบทสนทนานี้ใช่หรือไม่?")) {
      setMessagesBySession(prev => ({
        ...prev,
        [activeSession]: [
          {
            id: `welcome_${Date.now()}`,
            role: 'ai',
            text: 'ล้างการสนทนาเรียบร้อยครับ สามารถเริ่มพิมพ์คำถามใหม่ได้ทันที! 🚀',
            sql: null,
            visualization: null,
            rawData: [],
            timestamp: new Date().toLocaleTimeString('th-TH', { hour: '2-digit', minute: '2-digit' })
          }
        ]
      }));
      setActiveMessage(null);
    }
  };

  // CSV Upload Success
  const handleUploadSuccess = (res) => {
    const noticeMsg = {
      id: `up_${Date.now()}`,
      role: 'ai',
      text: `🎉 **นำเข้าข้อมูลสำเร็จแล้ว!**\n\n- **ชื่อตาราง:** \`${res.table_name}\`\n- **จำนวนข้อมูล:** **${res.row_count} แถว**\n- **การเข้ารหัส:** \`${res.encoding || 'UTF-8'}\`\n- **คอลัมน์ที่ตรวจพบ:** ${res.columns.map(c => `\`${c}\``).join(', ')}\n\nคุณสามารถเริ่มถามคำถามเพื่อวิเคราะห์ตารางนี้ได้ทันที เช่น *"แสดงข้อมูลในตาราง ${res.table_name}"* หรือ *"สรุปภาพรวม ${res.table_name}"*`,
      sql: null,
      visualization: null,
      rawData: [],
      timestamp: new Date().toLocaleTimeString('th-TH', { hour: '2-digit', minute: '2-digit' })
    };

    setMessagesBySession(prev => ({
      ...prev,
      [activeSession]: [...(prev[activeSession] || []), noticeMsg]
    }));
  };

  return (
    <div className="app-container">
      {/* 1. Leftmost Navigation & Session Sidebar */}
      <ChatHistorySidebar
        sessions={sessions}
        activeSession={activeSession}
        onSelectSession={(id) => setActiveSession(id)}
        onNewChat={handleNewChat}
        onDeleteSession={handleDeleteSession}
        onOpenUpload={() => setIsUploadOpen(true)}
        user={user}
      />

      {/* 2. Main Workspace (Split-Screen Layout) */}
      <div className="workspace-split-root">
        {/* Top Navbar */}
        <header className="workspace-navbar">
          <div className="navbar-left">
            <div className="session-title-tag">
              <Sparkles size={16} className="text-blue-600" />
              <h2>{sessions.find(s => s.id === activeSession)?.title || 'การวิเคราะห์ข้อมูล'}</h2>
            </div>
          </div>

          <div className="navbar-right">
            <button
              onClick={() => setIsUploadOpen(true)}
              className="nav-btn-upload"
              title="อัปโหลดไฟล์ CSV เพื่อนำเข้าสู่ SQLite"
            >
              <Database size={15} />
              <span>อัปโหลด CSV</span>
            </button>

            <button
              onClick={handleClearCurrentChat}
              className="nav-btn-clear"
              title="ล้างข้อความในห้องแชทนี้"
            >
              <Trash2 size={15} />
            </button>
          </div>
        </header>

        {/* Split Panes: Left Chat | Right Live Dashboard */}
        <div className="split-view-body">
          {/* LEFT PANE: Chat Interface */}
          <section className="chat-pane">
            <div className="chat-messages-scroll">
              {currentMessages.map((msg) => (
                <div
                  key={msg.id}
                  className={`message-item-wrapper ${msg.role === 'user' ? 'user-align' : 'ai-align'}`}
                  onClick={() => msg.role === 'ai' && (msg.visualization || msg.rawData?.length > 0) && setActiveMessage(msg)}
                >
                  <div className={`message-avatar ${msg.role === 'user' ? 'user-av' : 'ai-av'}`}>
                    {msg.role === 'user' ? <User size={16} /> : <Bot size={16} />}
                  </div>

                  <div className={`message-card ${msg.role === 'user' ? 'user-card' : 'ai-card'} ${msg.isError ? 'error-card' : ''}`}>
                    {/* Message Header */}
                    <div className="message-card-header">
                      <span className="sender-name">{msg.role === 'user' ? 'คุณ' : 'Data Analyst Assistant'}</span>
                      <span className="message-time">{msg.timestamp}</span>
                    </div>

                    {/* Markdown Rendered Content */}
                    <div className="message-card-body">
                      <MarkdownMessage content={msg.text} />
                    </div>

                    {/* SQL Query Collapsible Snippet */}
                    {msg.role === 'ai' && msg.sql && (
                      <details className="sql-snippet-box">
                        <summary>
                          <Code size={13} />
                          <span>คำสั่ง SQL ที่ AI ใช้งาน</span>
                        </summary>
                        <pre className="sql-code-display">{msg.sql}</pre>
                      </details>
                    )}

                    {/* Action Bar */}
                    {msg.role === 'ai' && !msg.isError && (msg.sql || msg.visualization || msg.rawData?.length > 0) && (
                      <div className="message-actions-bar">
                        {msg.visualization && msg.visualization.recommended_chart !== 'none' && (
                          <span className="badge-has-chart">📊 มีกราฟประกอบ</span>
                        )}
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handlePinItem(msg);
                          }}
                          className="pin-card-btn"
                        >
                          <Pin size={12} />
                          <span>ปักหมุด Dashboard</span>
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              ))}

              {/* Instant Feedback Loading Animation */}
              {isLoading && (
                <div className="message-item-wrapper ai-align">
                  <div className="message-avatar ai-av">
                    <Bot size={16} />
                  </div>
                  <div className="message-card ai-card loading-card">
                    <div className="loading-spinner-row">
                      <RefreshCw size={16} className="animate-spin text-blue-600" />
                      <span className="loading-stage-text">{LOADING_STAGES[loadingStageIdx]}</span>
                    </div>
                    <div className="loading-progress-bar">
                      <div className="loading-progress-fill"></div>
                    </div>
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>

            {/* Error Banner Alert */}
            {errorBanner && (
              <div className="error-alert-banner">
                <AlertCircle size={16} className="text-red-500 flex-shrink-0" />
                <span className="error-text">{errorBanner}</span>
                <button onClick={() => setErrorBanner(null)} className="error-dismiss-btn">✕</button>
              </div>
            )}

            {/* Suggested Queries Chips */}
            <div className="suggested-queries-panel">
              <span className="suggested-queries-label">💡 คำถามแนะนำ:</span>
              <div className="suggested-chips-scroll">
                {SUGGESTED_QUERIES.map((sq, idx) => (
                  <button
                    key={idx}
                    className="query-chip-btn"
                    onClick={() => handleSendMessage(null, sq)}
                    disabled={isLoading}
                  >
                    {sq}
                  </button>
                ))}
              </div>
            </div>

            {/* Input Bar */}
            <form onSubmit={handleSendMessage} className="chat-input-container">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="พิมพ์คำถามวิเคราะห์ข้อมูล เช่น 'สรุปยอดขายแยกตามสินค้า' หรือ 'แสดงรายชื่อลูกค้า'..."
                disabled={isLoading}
                className="chat-text-input"
              />
              <button
                type="submit"
                disabled={isLoading || !input.trim()}
                className="chat-send-btn"
                title="ส่งคำถาม"
              >
                <Send size={16} />
                <span>ส่งคำถาม</span>
              </button>
            </form>
          </section>

          {/* RIGHT PANE: Live Analytics Dashboard & Data Workspace */}
          <section className="analytics-pane">
            <AnalyticsPanel
              activeMessage={activeMessage}
              pinnedItems={pinnedItems}
              onPinItem={handlePinItem}
              onUnpinItem={handleUnpinItem}
            />
          </section>
        </div>
      </div>

      {/* CSV File Upload Modal (Part 1 Ingestion) */}
      <FileUploadModal
        isOpen={isUploadOpen}
        onClose={() => setIsUploadOpen(false)}
        onUploadSuccess={handleUploadSuccess}
      />
    </div>
  );
}
