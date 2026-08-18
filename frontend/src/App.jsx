import { useState, useEffect } from 'react';
import { sendQuery } from './services/chatService';
import { getPinnedDashboard, pinItemToDashboard, unpinItem } from './services/dashboardService';
import ChatHistorySidebar from './components/chat/ChatHistorySidebar';
import DashboardGrid from './components/dashboard/DashboardGrid';
import './App.css';

function App() {
  const [activeTab, setActiveTab] = useState('chat'); // 'chat' or 'dashboard'
  const [messages, setMessages] = useState([
    { role: 'ai', text: 'สวัสดีครับ! ผมคือ Data Analyst Assistant สอบถามข้อมูลหรือสั่งวิเคราะห์ยอดขายได้เลยครับ 🚀' }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  
  // Dashboard & Sessions
  const [pinnedItems, setPinnedItems] = useState([]);
  const [sessions, setSessions] = useState([
    { id: 'session_1', title: 'วิเคราะห์ยอดขายประจำวัน' }
  ]);
  const [activeSession, setActiveSession] = useState('session_1');
  const user = { name: 'ทีม 04 Data Analyst' };

  useEffect(() => {
    // โหลดรายการปักหมุดเมื่อเริ่มต้น
    fetchPinnedItems();
  }, []);

  const fetchPinnedItems = async () => {
    try {
      const items = await getPinnedDashboard();
      setPinnedItems(items || []);
    } catch (err) {
      console.log("Not connected to backend dashboard yet");
    }
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage = { role: 'user', text: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const data = await sendQuery(userMessage.text);
      const aiMessage = { 
        role: 'ai', 
        text: data.response,
        sql: data.sql,
        visualization: data.visualization
      };
      setMessages((prev) => [...prev, aiMessage]);
    } catch (error) {
      console.error("Error fetching query:", error);
      const errorMessage = { role: 'ai', text: "ขออภัยครับ ไม่สามารถเชื่อมต่อกับเซิร์ฟเวอร์ หรือเกิดข้อผิดพลาดในการดึงข้อมูล ❌" };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handlePin = async (msg) => {
    const newItem = {
      id: Date.now(),
      title: `ข้อความสรุป (${new Date().toLocaleTimeString('th-TH')})`,
      content: msg.text
    };
    try {
      await pinItemToDashboard(newItem);
      setPinnedItems((prev) => [...prev, newItem]);
      alert("📌 ปักหมุดลงบน Dynamic Dashboard เรียบร้อยแล้ว!");
    } catch (err) {
      alert("ปักหมุดสำเร็จในโหมดออฟไลน์!");
      setPinnedItems((prev) => [...prev, newItem]);
    }
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
      { role: 'ai', text: 'สวัสดีครับ! เริ่มการสนทนาหัวข้อใหม่ สอบถามข้อมูลยอดขายได้เลยครับ 🚀' }
    ]);
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
        </header>

        {activeTab === 'chat' ? (
          <div className="chat-container">
            <div className="chat-messages">
              {messages.map((msg, index) => (
                <div key={index} className={`message-wrapper ${msg.role === 'user' ? 'user-wrapper' : 'ai-wrapper'}`}>
                  <div className={`message-bubble ${msg.role === 'user' ? 'user-bubble' : 'ai-bubble'}`}>
                    {msg.text}
                    {msg.role === 'ai' && msg.sql && (
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
                    AI Core & Analytics กำลังประมวลผล...
                  </div>
                </div>
              )}
            </div>

            <form onSubmit={handleSendMessage} className="chat-input-form">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="พิมพ์คำถามวิเคราะห์ข้อมูล เช่น 'สรุปยอดขายทั้งหมด'..."
                disabled={isLoading}
              />
              <button type="submit" disabled={isLoading || !input.trim()}>
                ส่งคำถาม
              </button>
            </form>
          </div>
        ) : (
          <DashboardGrid pinnedItems={pinnedItems} onUnpin={handleUnpin} />
        )}
      </main>
    </div>
  );
}

export default App;
