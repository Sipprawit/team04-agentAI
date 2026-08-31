import { useState, useEffect, useRef } from 'react';
import { sendQuery } from './services/chatService';
import { getPinnedDashboard, pinItemToDashboard, unpinItem } from './services/dashboardService';
import ChatHistorySidebar from './components/chat/ChatHistorySidebar';
import DashboardGrid from './components/dashboard/DashboardGrid';
import ChartRenderer from './components/charts/ChartRenderer';
import FileUploadModal from './components/upload/FileUploadModal';
import './App.css';

const SUGGESTED_QUERIES = [
  'แสดงรายชื่อสินค้าทั้งหมด',
  'สรุปยอดขายรวมของสินค้าแต่ละชิ้น',
  'ลูกค้า 5 อันดับแรกที่มียอดสั่งซื้อสูงสุด',
  'สินค้าที่ขายดีที่สุดและยอดขายรวม',
];

function App() {
  const [activeTab, setActiveTab] = useState('chat'); // 'chat' or 'dashboard'
  const [messages, setMessages] = useState([
    {
      role: 'ai',
      text: 'สวัสดีครับ! ผมคือ Data Analyst AI Assistant 🚀\nคุณสามารถสอบถามข้อมูลยอดขาย สั่งสรุปรายงาน หรืออัปโหลดไฟล์ CSV เพื่อวิเคราะห์ข้อมูลชุดใหม่ได้ทันทีครับ!',
      visualization: null,
      sql: null,
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isUploadOpen, setIsUploadOpen] = useState(false);
  
  // Dashboard & Sessions
  const [pinnedItems, setPinnedItems] = useState([]);
  const [sessions, setSessions] = useState([
    { id: 'session_1', title: 'วิเคราะห์ยอดขาย E-Commerce' }
  ]);
  const [activeSession, setActiveSession] = useState('session_1');
  const user = { name: 'ทีม 04 Data Analyst' };

  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  useEffect(() => {
    fetchPinnedItems();
  }, []);

  const fetchPinnedItems = async () => {
    try {
      const items = await getPinnedDashboard();
      setPinnedItems(items || []);
    } catch (err) {
      console.log("Using local pinned storage");
    }
  };

  const handleSendMessage = async (e, queryTextOverride = null) => {
    if (e) e.preventDefault();
    const queryToSend = queryTextOverride || input;
    if (!queryToSend.trim()) return;

    const userMessage = { role: 'user', text: queryToSend };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      // ส่งประวัติแชทล่าสุด 5 ข้อความเพื่อให้ AI มี Context
      const recentHistory = messages.slice(-5).map(m => ({ role: m.role, text: m.text }));
      const data = await sendQuery(userMessage.text, recentHistory);

      const aiMessage = { 
        role: 'ai', 
        text: data.response,
        sql: data.sql,
        visualization: data.visualization,
        rawData: data.data,
      };
      setMessages((prev) => [...prev, aiMessage]);
    } catch (error) {
      console.error("Error fetching query:", error);
      const errorMsg = error.response?.data?.message || error.response?.data?.detail || "ขออภัยครับ ไม่สามารถเชื่อมต่อกับเซิร์ฟเวอร์ หรือเกิดข้อผิดพลาดในการดึงข้อมูล";
      const errorMessage = { 
        role: 'ai', 
        text: `❌ ${errorMsg}`,
        sql: null,
        visualization: null
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handlePin = async (msg) => {
    const newItem = {
      id: Date.now(),
      title: `รายงาน (${new Date().toLocaleTimeString('th-TH', { hour: '2-digit', minute: '2-digit' })})`,
      content: msg.text,
      sql: msg.sql,
      visualization: msg.visualization,
    };
    try {
      await pinItemToDashboard(newItem);
      setPinnedItems((prev) => [...prev, newItem]);
    } catch (err) {
      setPinnedItems((prev) => [...prev, newItem]);
    }
    alert("📌 ปักหมุดกราฟและข้อความลง Dashboard เรียบร้อยแล้ว!");
  };

  const handleUnpin = async (id) => {
    try {
      await unpinItem(id);
    } catch (err) {}
    setPinnedItems((prev) => prev.filter(item => item.id !== id));
  };

  const handleNewChat = () => {
    const newId = `session_${Date.now()}`;
    setSessions((prev) => [...prev, { id: newId, title: `หัวข้อสนทนาใหม่ ${sessions.length + 1}` }]);
    setActiveSession(newId);
    setMessages([
      {
        role: 'ai',
        text: 'สวัสดีครับ! เริ่มการสนทนาหัวข้อใหม่ สอบถามข้อมูลหรือสั่งสร้างกราฟได้เลยครับ 🚀',
        visualization: null,
        sql: null,
      }
    ]);
  };

  const handleUploadSuccess = (uploadResult) => {
    const aiNotice = {
      role: 'ai',
      text: `🎉 **นำเข้าข้อมูลสำเร็จแล้ว!**\n- ตาราง: \`${uploadResult.table_name}\`\n- จำนวน: **${uploadResult.row_count} แถว**\n- คอลัมน์: ${uploadResult.columns.join(', ')}\n\nคุณสามารถเริ่มถามคำถามเกี่ยวกับตารางนี้ได้ทันที เช่น *"สรุปข้อมูลในตาราง ${uploadResult.table_name}"*`,
      sql: null,
      visualization: null,
    };
    setMessages((prev) => [...prev, aiNotice]);
  };

  return (
    <div className="app-root">
      {/* Sidebar - System 7: Conversational History */}
      <ChatHistorySidebar
        sessions={sessions}
        activeSession={activeSession}
        onSelectSession={(id) => setActiveSession(id)}
        onNewChat={handleNewChat}
        user={user}
      />

      {/* Main Content Area */}
      <main className="main-content">
        <header className="navbar">
          <div className="nav-tabs">
            <button
              className={`nav-btn ${activeTab === 'chat' ? 'active' : ''}`}
              onClick={() => setActiveTab('chat')}
            >
              💬 ระบบสนทนาข้อมูล (Chat UI)
            </button>
            <button
              className={`nav-btn ${activeTab === 'dashboard' ? 'active' : ''}`}
              onClick={() => setActiveTab('dashboard')}
            >
              📊 Dynamic Dashboard ({pinnedItems.length})
            </button>
          </div>

          <div className="nav-actions">
            <button className="upload-nav-btn" onClick={() => setIsUploadOpen(true)}>
              📁 อัปโหลดไฟล์ CSV
            </button>
          </div>
        </header>

        {activeTab === 'chat' ? (
          <div className="chat-container">
            {/* Messages Scroll Area */}
            <div className="chat-messages">
              {messages.map((msg, index) => (
                <div key={index} className={`message-wrapper ${msg.role === 'user' ? 'user-wrapper' : 'ai-wrapper'}`}>
                  <div className={`message-bubble ${msg.role === 'user' ? 'user-bubble' : 'ai-bubble'}`}>
                    {/* ข้อความสรุป */}
                    <div className="message-text">
                      {msg.text.split('\n').map((line, lIdx) => (
                        <p key={lIdx} className="message-line">
                          {line.startsWith('#') || line.startsWith('**') ? (
                            <strong>{line.replace(/^#+\s*/, '').replace(/\*\*/g, '')}</strong>
                          ) : (
                            line
                          )}
                        </p>
                      ))}
                    </div>

                    {/* กราฟ Recharts Visualization (ถ้ามี) */}
                    {msg.role === 'ai' && msg.visualization && (
                      <div className="message-chart-container">
                        <ChartRenderer visualization={msg.visualization} />
                      </div>
                    )}

                    {/* SQL Query Collapsible Box */}
                    {msg.role === 'ai' && msg.sql && (
                      <details className="sql-details-box">
                        <summary>🔍 ดูคำสั่ง SQL ที่สร้างโดย AI</summary>
                        <pre className="sql-code-block">{msg.sql}</pre>
                      </details>
                    )}

                    {/* Action Bar: Pin to Dashboard */}
                    {msg.role === 'ai' && (msg.sql || msg.visualization) && (
                      <div className="pin-action">
                        <button onClick={() => handlePin(msg)} className="pin-btn">
                          📌 ปักหมุดลง Dashboard
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              ))}

              {isLoading && (
                <div className="message-wrapper ai-wrapper">
                  <div className="message-bubble ai-bubble loading-bubble">
                    <span className="dot"></span>
                    <span className="dot"></span>
                    <span className="dot"></span>
                    <span>AI Core กำลังประมวลผลคำสั่ง SQL และสร้างกราฟ...</span>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Suggested Quick Queries */}
            <div className="suggested-queries-bar">
              <span className="suggested-label">💡 คำถามแนะนำ:</span>
              {SUGGESTED_QUERIES.map((sq, sIdx) => (
                <button
                  key={sIdx}
                  className="suggested-chip"
                  onClick={() => handleSendMessage(null, sq)}
                  disabled={isLoading}
                >
                  {sq}
                </button>
              ))}
            </div>

            {/* Chat Input Form */}
            <form onSubmit={handleSendMessage} className="chat-input-form">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="พิมพ์คำถามวิเคราะห์ข้อมูล เช่น 'สรุปยอดขายแยกตามสินค้า'..."
                disabled={isLoading}
              />
              <button type="submit" disabled={isLoading || !input.trim()}>
                ส่งคำถาม 🚀
              </button>
            </form>
          </div>
        ) : (
          <DashboardGrid pinnedItems={pinnedItems} onUnpin={handleUnpin} />
        )}
      </main>

      {/* CSV File Upload Modal (Part 1 Integration) */}
      <FileUploadModal
        isOpen={isUploadOpen}
        onClose={() => setIsUploadOpen(false)}
        onUploadSuccess={handleUploadSuccess}
      />
    </div>
  );
}

export default App;
