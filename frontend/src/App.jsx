import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
  Send,
  Sparkles,
  Bot,
  User,
  Plus,
  Code,
  Pin,
  AlertCircle,
  RefreshCw,
  BarChart3,
  Table as TableIcon,
  CheckCircle2,
  ArrowRight,
  Download,
  Database,
  FileSpreadsheet
} from 'lucide-react';
import {
  sendQuery,
  listSessions,
  createSession,
  deleteSession,
  getChatHistory,
  saveChatMessage,
  fetchSchemaDict
} from './services/chatService';
import { pinItemToDashboard, unpinItem } from './services/dashboardService';
import ChatHistorySidebar from './components/chat/ChatHistorySidebar';
import AnalyticsPanel from './components/dashboard/AnalyticsPanel';
import MarkdownMessage from './components/chat/MarkdownMessage';
import FileUploadModal from './components/upload/FileUploadModal';
import Toast from './components/common/Toast';
import './App.css';

const LOCAL_STORAGE_SESSIONS_KEY = 'team04_chat_sessions_v4';
const LOCAL_STORAGE_MESSAGES_KEY = 'team04_chat_messages_v4';
const LOCAL_STORAGE_PINNED_KEY = 'team04_pinned_dashboard_v4';
const LOCAL_STORAGE_PANEL_WIDTH_KEY = 'team04_analytics_panel_width_v4';

const DEFAULT_SUGGESTED_QUERIES = [
  'นำเข้าไฟล์ CSV เพื่อเริ่มวิเคราะห์ (+)',
  'สรุปภาพรวมยอดขายและสินค้าตัวอย่าง',
  'แสดงสินค้า 5 อันดับแรกที่มีราคาสูงสุด',
  'แจกแจงจำนวนคำสั่งซื้อแยกตามลูกค้า',
];

const LOADING_STAGES = [
  'กำลังวิเคราะห์โครงสร้างคำถามและสังเคราะห์คำสั่ง SQL...',
  'กำลังประมวลผลข้อมูลในสภาพแวดล้อมความปลอดภัย (Secure Sandbox)...',
  'กำลังคำนวณสถิติเชิงลึกและจัดเตรียมแผนภูมิรายงาน...'
];

// ฟังก์ชันสร้างชื่อห้องแชทอัตโนมัติจากคำถามแรก
const generateSessionTitle = (query) => {
  let clean = query.trim().replace(/^(ขอ|ช่วย|ลอง|กรุณา|ค้นหา|แสดง)\s*/i, '');
  if (clean.length > 24) {
    clean = clean.slice(0, 24) + '...';
  }
  return clean || query.slice(0, 20);
};

// ฟังก์ชันดาวน์โหลดไฟล์ CSV แบบ UTF-8 BOM
const exportDataToCsv = (data, filename = 'query_result') => {
  if (!data || data.length === 0) return;
  const columns = Object.keys(data[0]);
  const headers = columns.join(',');
  const rows = data.map(row =>
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
  link.download = `${filename}_${Date.now()}.csv`;
  link.click();
  URL.revokeObjectURL(url);
};

export default function App() {
  // 1. Session & History State
  const [sessions, setSessions] = useState(() => {
    try {
      const saved = localStorage.getItem(LOCAL_STORAGE_SESSIONS_KEY);
      if (saved) return JSON.parse(saved);
    } catch (_e) {}
    return [{ id: 'session_default', title: 'การวิเคราะห์ข้อมูลและสถิติ', time: 'ล่าสุด' }];
  });

  const [activeSession, setActiveSession] = useState(() => {
    try {
      const saved = localStorage.getItem(LOCAL_STORAGE_SESSIONS_KEY);
      if (saved) {
        const parsed = JSON.parse(saved);
        if (parsed.length > 0) return parsed[0].id;
      }
    } catch (_e) {}
    return 'session_default';
  });

  const [messagesBySession, setMessagesBySession] = useState(() => {
    try {
      const saved = localStorage.getItem(LOCAL_STORAGE_MESSAGES_KEY);
      if (saved) return JSON.parse(saved);
    } catch (_e) {}
    return {
      session_default: [
        {
          id: 'welcome',
          role: 'ai',
          text: 'ระบบผู้ช่วยวิเคราะห์ข้อมูลอัจฉริยะ (Data Analyst AI Assistant) พร้อมให้บริการสืบค้น สรุปผลเชิงคุณภาพ และสร้างแผนภูมิเชิงปริมาณ ท่านสามารถกดปุ่ม **`+`** เพื่อนำเข้าไฟล์ชุดข้อมูล (CSV) หรือพิมพ์คำถามเพื่อเริ่มต้นการวิเคราะห์',
          sql: null,
          visualization: null,
          rawData: [],
          followUpQuestions: DEFAULT_SUGGESTED_QUERIES.slice(0, 3),
          timestamp: new Date().toLocaleTimeString('th-TH', { hour: '2-digit', minute: '2-digit' })
        }
      ]
    };
  });

  // 2. Pinned Items State
  const [pinnedItems, setPinnedItems] = useState(() => {
    try {
      const saved = localStorage.getItem(LOCAL_STORAGE_PINNED_KEY);
      if (saved) return JSON.parse(saved);
    } catch (_e) {}
    return [];
  });

  // 3. UI Panes Toggle & Resizing States
  const [isLeftSidebarOpen, setIsLeftSidebarOpen] = useState(true);
  const [isRightPanelOpen, setIsRightPanelOpen] = useState(true);
  const [rightPanelWidth, setRightPanelWidth] = useState(() => {
    try {
      const saved = localStorage.getItem(LOCAL_STORAGE_PANEL_WIDTH_KEY);
      if (saved) return Number(saved);
    } catch (_e) {}
    return 540; // Default width in px
  });
  const [isDraggingResizer, setIsDraggingResizer] = useState(false);
  const splitContainerRef = useRef(null);

  // 4. Toast Notification State
  const [toast, setToast] = useState(null);

  // 5. Input & Modal States
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [loadingStageIdx, setLoadingStageIdx] = useState(0);
  const [errorBanner, setErrorBanner] = useState(null);
  const [isUploadOpen, setIsUploadOpen] = useState(false);
  const [activeMessage, setActiveMessage] = useState(null);
  const [analyticsTab, setAnalyticsTab] = useState('insights'); // 'insights' | 'table' | 'pinned'
  const [suggestedQueries, setSuggestedQueries] = useState(DEFAULT_SUGGESTED_QUERIES);

  const messagesEndRef = useRef(null);
  const user = { name: 'ทีม 04 Data Analyst' };

  // Current session messages
  const currentMessages = messagesBySession[activeSession] || [];

  // ============================================
  // Resizable Split Pane Logic
  // ============================================

  const handleResizerMouseDown = (e) => {
    e.preventDefault();
    setIsDraggingResizer(true);
  };

  useEffect(() => {
    const handleMouseMove = (e) => {
      if (!isDraggingResizer) return;
      const container = splitContainerRef.current;
      if (!container) return;
      const rect = container.getBoundingClientRect();
      const newWidth = rect.right - e.clientX;
      const minW = 340;
      const maxW = Math.max(minW, rect.width - 380);
      const clamped = Math.min(Math.max(newWidth, minW), maxW);
      setRightPanelWidth(clamped);
    };

    const handleMouseUp = () => {
      if (isDraggingResizer) {
        setIsDraggingResizer(false);
        try {
          localStorage.setItem(LOCAL_STORAGE_PANEL_WIDTH_KEY, String(rightPanelWidth));
        } catch (_e) {}
      }
    };

    if (isDraggingResizer) {
      window.addEventListener('mousemove', handleMouseMove);
      window.addEventListener('mouseup', handleMouseUp);
    }
    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isDraggingResizer, rightPanelWidth]);

  // ============================================
  // Auto-Sync with Backend SQLite (Part 4)
  // ============================================

  // ดึงรายชื่อ Sessions จาก SQLite ตอนเริ่มต้น
  useEffect(() => {
    const syncSessionsFromBackend = async () => {
      try {
        const backendSessions = await listSessions();
        if (backendSessions && backendSessions.length > 0) {
          const formatted = backendSessions.map(s => ({
            id: s.session_id,
            title: s.title || 'การสนทนา',
            time: 'ล่าสุด'
          }));
          setSessions(formatted);
          if (!backendSessions.some(s => s.session_id === activeSession)) {
            setActiveSession(backendSessions[0].session_id);
          }
        }
      } catch (_err) {}
    };
    syncSessionsFromBackend();
  }, []);

  // ตรวจสอบโครงสร้างฐานข้อมูลตอนเริ่มต้น เพื่อตั้งคำถามแนะนำให้ตรงกับข้อมูลจริง (Context-Aware)
  useEffect(() => {
    const detectInitialSuggestedQueries = async () => {
      try {
        const schemaDict = await fetchSchemaDict();
        if (schemaDict && typeof schemaDict === 'object' && !schemaDict.error) {
          const uploadedEntries = Object.entries(schemaDict).filter(
            ([_name, info]) => !info.is_system && !info.is_mock
          );
          if (uploadedEntries.length > 0) {
            const [firstTableName, firstTableInfo] = uploadedEntries[0];
            const previewCols = firstTableInfo.columns ? firstTableInfo.columns.map(c => c.name) : [];
            const ignoredCols = ['id', 'ลำดับ', 'ที่ตั้ง', 'โทรศัพท์', 'อีเมลล์', 'เว็บไซต์', 'link', 'url', 'phone', 'address', 'desc', 'description'];
            const bestCatCol = previewCols.find(c => {
              const cl = c.toLowerCase();
              return !ignoredCols.some(ign => cl.includes(ign)) && (cl.includes('หมวด') || cl.includes('ประเภท') || cl.includes('อำเภอ') || cl.includes('กลุ่ม') || cl.includes('status') || cl.includes('type') || cl.includes('category'));
            }) || previewCols.find(c => !ignoredCols.some(ign => c.toLowerCase().includes(ign))) || '';

            const breakdownQuery = bestCatCol
              ? `แจกแจงจำนวนรายการตามแต่ละ${bestCatCol}ในตาราง ${firstTableName}`
              : `แจกแจงจำนวนรายการตามแต่ละหมวดหมู่ในตาราง ${firstTableName}`;

            setSuggestedQueries([
              `แสดงข้อมูลทั้งหมดในตาราง ${firstTableName}`,
              breakdownQuery,
              `สรุปภาพรวมและสถิติสำคัญในตาราง ${firstTableName}`,
              `ค้นหา 5 อันดับแรกในตาราง ${firstTableName}`,
            ]);
          }
        }
      } catch (_e) {}
    };
    detectInitialSuggestedQueries();
  }, []);

  // ดึงประวัติการแชทของ Session จาก SQLite
  const fetchSessionHistory = useCallback(async (sessionId) => {
    try {
      const historyData = await getChatHistory(sessionId);
      if (historyData?.messages && historyData.messages.length > 0) {
        const loadedMessages = historyData.messages.map(m => {
          const isAi = m.role === 'assistant' || m.role === 'ai';
          return {
            id: `db_${m.id}`,
            role: isAi ? 'ai' : m.role,
            text: m.content,
            isUploadNotice: !!m.metadata?.uploadData,
            uploadData: m.metadata?.uploadData || null,
            sql: m.metadata?.sql || null,
            visualization: m.metadata?.visualization || null,
            rawData: m.metadata?.rawData || [],
            followUpQuestions: m.metadata?.followUpQuestions || [],
            userQuery: m.metadata?.userQuery || null,
            timestamp: m.created_at ? new Date(m.created_at).toLocaleTimeString('th-TH', { hour: '2-digit', minute: '2-digit' }) : 'ล่าสุด'
          };
        });
        setMessagesBySession(prev => ({
          ...prev,
          [sessionId]: loadedMessages
        }));

        // อัปเดต activeMessage ให้ตรงกับข้อความ AI ล่าสุดของห้องนี้
        const lastAi = [...loadedMessages].reverse().find(
          msg => msg.role === 'ai' && ((msg.visualization && msg.visualization.recommended_chart !== 'none') || (msg.rawData && msg.rawData.length > 0) || msg.sql)
        );
        if (lastAi) {
          setActiveMessage(lastAi);
          if (lastAi.visualization && lastAi.visualization.recommended_chart !== 'none') {
            setAnalyticsTab('insights');
          } else if (lastAi.rawData && lastAi.rawData.length > 0) {
            setAnalyticsTab('table');
          }
        } else {
          setActiveMessage(null);
        }
      }
    } catch (_err) {}
  }, []);

  // เมื่อเลือก Session: เปลี่ยน activeSession และอัปเดต activeMessage ทันที ไม่ค้างของห้องก่อนหน้า
  const handleSelectSession = (sessionId) => {
    setActiveSession(sessionId);
    const sessionMsgs = messagesBySession[sessionId] || [];
    const lastAi = [...sessionMsgs].reverse().find(
      msg => msg.role === 'ai' && ((msg.visualization && msg.visualization.recommended_chart !== 'none') || (msg.rawData && msg.rawData.length > 0) || msg.sql)
    );
    if (lastAi) {
      setActiveMessage(lastAi);
      if (lastAi.visualization && lastAi.visualization.recommended_chart !== 'none') {
        setAnalyticsTab('insights');
      } else if (lastAi.rawData && lastAi.rawData.length > 0) {
        setAnalyticsTab('table');
      }
    } else {
      setActiveMessage(null);
    }
    fetchSessionHistory(sessionId);
  };

  // ซิงค์ activeMessage เมื่อ currentMessages มีการเปลี่ยนแปลง
  useEffect(() => {
    const msgs = messagesBySession[activeSession] || [];
    const lastAi = [...msgs].reverse().find(
      msg => msg.role === 'ai' && ((msg.visualization && msg.visualization.recommended_chart !== 'none') || (msg.rawData && msg.rawData.length > 0))
    );
    setActiveMessage(lastAi || null);
  }, [activeSession, messagesBySession]);

  // Save to localStorage as quick cache
  useEffect(() => {
    try {
      localStorage.setItem(LOCAL_STORAGE_SESSIONS_KEY, JSON.stringify(sessions));
      localStorage.setItem(LOCAL_STORAGE_MESSAGES_KEY, JSON.stringify(messagesBySession));
      localStorage.setItem(LOCAL_STORAGE_PINNED_KEY, JSON.stringify(pinnedItems));
    } catch (_e) {}
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

  // ============================================
  // Chat Actions & Pipeline
  // ============================================

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

    // Update local state
    setMessagesBySession(prev => ({
      ...prev,
      [activeSession]: [...(prev[activeSession] || []), userMessage]
    }));

    setInput('');
    setIsLoading(true);
    setErrorBanner(null);

    // Persist user message to SQLite in background
    saveChatMessage(activeSession, {
      role: 'user',
      content: userMessage.text,
      metadata: null
    }).catch(() => {});

    // Auto-update session title based on first query
    const newTitle = generateSessionTitle(queryToSend);
    setSessions(prev => prev.map(s => {
      if (s.id === activeSession && (s.title.startsWith('การสนทนาใหม่') || s.title === 'การวิเคราะห์ข้อมูลและสถิติ')) {
        return { ...s, title: newTitle };
      }
      return s;
    }));

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
        userQuery: userMessage.text,
        text: data.response || 'ประมวลผลข้อมูลเรียบร้อยแล้ว',
        sql: data.sql || null,
        visualization: data.visualization || null,
        rawData: data.data || [],
        followUpQuestions: data.follow_up_questions || [],
        timestamp: new Date().toLocaleTimeString('th-TH', { hour: '2-digit', minute: '2-digit' })
      };

      setMessagesBySession(prev => ({
        ...prev,
        [activeSession]: [...(prev[activeSession] || []), aiMessage]
      }));

      // Persist AI message to SQLite in background
      saveChatMessage(activeSession, {
        role: 'assistant',
        content: aiMessage.text,
        metadata: {
          sql: aiMessage.sql,
          visualization: aiMessage.visualization,
          rawData: aiMessage.rawData,
          followUpQuestions: aiMessage.followUpQuestions,
          userQuery: aiMessage.userQuery
        }
      }).catch(() => {});

      setActiveMessage(aiMessage);
      if (aiMessage.visualization && aiMessage.visualization.recommended_chart !== 'none') {
        setAnalyticsTab('insights');
        setIsRightPanelOpen(true);
      }
      if (data.follow_up_questions && data.follow_up_questions.length > 0) {
        setSuggestedQueries(data.follow_up_questions);
      }
    } catch (error) {
      console.error("Query execution error:", error);
      const errorMsg = error.response?.data?.message || error.response?.data?.detail || error.message || "ไม่สามารถเชื่อมต่อกับระบบได้ กรุณาตรวจสอบสถานะเซิร์ฟเวอร์";
      
      const errorAiMsg = {
        id: `err_${Date.now()}`,
        role: 'ai',
        isError: true,
        userQuery: userMessage.text,
        text: `**เกิดข้อผิดพลาดในการประมวลผลคำสั่ง**\n\n${errorMsg}\n\n*ข้อแนะนำ: กรุณาตรวจสอบคำถามหรือระบุชื่อข้อมูลที่ต้องการสืบค้นให้เจาะจงยิ่งขึ้น*`,
        sql: null,
        visualization: null,
        rawData: [],
        followUpQuestions: ["แสดงรายชื่อตารางและข้อมูลที่มีทั้งหมด", "แสดงตัวอย่างข้อมูล 10 แถวแรก"],
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

  const handleSuggestedChipClick = (sq) => {
    if (!sq) return;
    if (sq.includes('นำเข้าไฟล์ CSV') || sq.includes('(+)')) {
      setIsUploadOpen(true);
      return;
    }
    handleSendMessage(null, sq);
  };

  // คลิกเลือกข้อความ AI เพื่อเรียกดูข้อมูล กราฟ และตารางย้อนหลังในแผงวิเคราะห์
  const handleSelectMessage = (msg) => {
    if (!msg || msg.role !== 'ai') return;
    if (!msg.visualization && (!msg.rawData || msg.rawData.length === 0) && !msg.sql) return;

    setActiveMessage(msg);
    setIsRightPanelOpen(true);

    if (msg.visualization && msg.visualization.recommended_chart && msg.visualization.recommended_chart !== 'none') {
      setAnalyticsTab('insights');
    } else if (msg.rawData && msg.rawData.length > 0) {
      setAnalyticsTab('table');
    }
  };

  // Pin / Unpin Dashboard
  const handlePinItem = async (msg) => {
    if (!msg) return;
    const newItem = {
      id: Date.now(),
      title: `รายงานการวิเคราะห์ (${msg.timestamp || new Date().toLocaleTimeString('th-TH')})`,
      content: msg.text,
      sql: msg.sql,
      visualization: msg.visualization,
      rawData: msg.rawData,
      userQuery: msg.userQuery,
    };

    try {
      await pinItemToDashboard(newItem);
    } catch (_e) {}

    setPinnedItems(prev => [newItem, ...prev]);
    setToast({
      type: 'pin',
      title: 'ปักหมุดสำเร็จ',
      message: 'บันทึกรายงานและแผนภูมิเข้าสู่แดชบอร์ดเรียบร้อยแล้ว'
    });
  };

  const handleUnpinItem = async (id) => {
    try {
      await unpinItem(id);
    } catch (_e) {}
    setPinnedItems(prev => prev.filter(item => item.id !== id));
    setToast({
      type: 'info',
      title: 'นำรายการออกแล้ว',
      message: 'ลบรายการออกจากแดชบอร์ดเรียบร้อย'
    });
  };

  // New Chat Session
  const handleNewChat = async () => {
    const newId = `session_${Date.now()}`;
    const newTitle = `การสนทนาใหม่ ${sessions.length + 1}`;
    const newSession = {
      id: newId,
      title: newTitle,
      time: 'ล่าสุด'
    };

    try {
      await createSession(newId, newTitle);
    } catch (_e) {}

    setSessions(prev => [newSession, ...prev]);
    setActiveSession(newId);
    setMessagesBySession(prev => ({
      ...prev,
      [newId]: [
        {
          id: `welcome_${Date.now()}`,
          role: 'ai',
          text: 'ยินดีต้อนรับสู่หัวข้อการสนทนาใหม่ ท่านสามารถพิมพ์คำถามหรือเลือกประเด็นที่ต้องการสืบค้นข้อมูลได้ทันที',
          sql: null,
          visualization: null,
          rawData: [],
          followUpQuestions: DEFAULT_SUGGESTED_QUERIES.slice(0, 3),
          timestamp: new Date().toLocaleTimeString('th-TH', { hour: '2-digit', minute: '2-digit' })
        }
      ]
    }));
    setActiveMessage(null);
  };

  // Delete Session (via right-click context menu in sidebar)
  const handleDeleteSession = async (sessId) => {
    if (sessions.length <= 1) {
      setToast({
        type: 'error',
        title: 'ไม่สามารถลบได้',
        message: 'ระบบต้องการบทสนทนาอย่างน้อย 1 รายการ'
      });
      return;
    }

    try {
      await deleteSession(sessId);
    } catch (_e) {}

    const remaining = sessions.filter(s => s.id !== sessId);
    setSessions(remaining);
    if (activeSession === sessId) {
      const nextSessionId = remaining[0].id;
      setActiveSession(nextSessionId);
      const nextMsgs = messagesBySession[nextSessionId] || [];
      const nextLastAi = [...nextMsgs].reverse().find(
        m => m.role === 'ai' && ((m.visualization && m.visualization.recommended_chart !== 'none') || (m.rawData && m.rawData.length > 0))
      );
      setActiveMessage(nextLastAi || null);
    }
    setMessagesBySession(prev => {
      const copy = { ...prev };
      delete copy[sessId];
      return copy;
    });
    setToast({
      type: 'info',
      title: 'ลบข้อมูลสำเร็จ',
      message: 'ลบหัวข้อการสนทนาเรียบร้อยแล้ว'
    });
  };

  // CSV Upload Success
  const handleUploadSuccess = (res) => {
    const uploadAiMsg = {
      id: `up_${Date.now()}`,
      role: 'ai',
      isUploadNotice: true,
      uploadData: res,
      userQuery: `นำเข้าไฟล์ชุดข้อมูล: ${res.table_name}`,
      text: `**นำเข้าชุดข้อมูลเข้าสู่ตาราง \`${res.table_name}\` สำเร็จ**`,
      sql: `SELECT * FROM "${res.table_name}" LIMIT 10;`,
      visualization: null,
      rawData: res.preview_data || [],
      followUpQuestions: [
        `แสดงข้อมูลทั้งหมดในตาราง ${res.table_name}`,
        `จัดกลุ่มและสรุปข้อมูลในตาราง ${res.table_name}`
      ],
      timestamp: new Date().toLocaleTimeString('th-TH', { hour: '2-digit', minute: '2-digit' })
    };

    setMessagesBySession(prev => ({
      ...prev,
      [activeSession]: [...(prev[activeSession] || []), uploadAiMsg]
    }));

    // Persist to SQLite
    saveChatMessage(activeSession, {
      role: 'assistant',
      content: uploadAiMsg.text,
      metadata: {
        sql: uploadAiMsg.sql,
        rawData: uploadAiMsg.rawData,
        uploadData: res
      }
    }).catch(() => {});

    setActiveMessage(uploadAiMsg);
    setAnalyticsTab('table');
    setIsRightPanelOpen(true);

    // อัปเดตคำถามแนะนำด้านล่างให้ตรงกับตารางและคอลัมน์ที่เพิ่งอัปโหลด
    const previewCols = res.preview_data && res.preview_data.length > 0 ? Object.keys(res.preview_data[0]) : [];
    const ignoredCols = ['id', 'ลำดับ', 'ที่ตั้ง', 'โทรศัพท์', 'อีเมลล์', 'เว็บไซต์', 'link', 'url', 'phone', 'address', 'desc', 'description'];
    const bestCatCol = previewCols.find(c => {
      const cl = c.toLowerCase();
      return !ignoredCols.some(ign => cl.includes(ign)) && (cl.includes('หมวด') || cl.includes('ประเภท') || cl.includes('อำเภอ') || cl.includes('กลุ่ม') || cl.includes('status') || cl.includes('type') || cl.includes('category'));
    }) || previewCols.find(c => !ignoredCols.some(ign => c.toLowerCase().includes(ign))) || '';

    const breakdownQuery = bestCatCol
      ? `แจกแจงจำนวนรายการตามแต่ละ${bestCatCol}ในตาราง ${res.table_name}`
      : `แจกแจงจำนวนรายการตามแต่ละหมวดหมู่ในตาราง ${res.table_name}`;

    setSuggestedQueries([
      `แสดงข้อมูลทั้งหมดในตาราง ${res.table_name}`,
      breakdownQuery,
      `สรุปภาพรวมและสถิติสำคัญในตาราง ${res.table_name}`,
      `ค้นหา 5 อันดับแรกในตาราง ${res.table_name}`,
    ]);

    setToast({
      type: 'upload',
      title: 'นำเข้าข้อมูลเรียบร้อย',
      message: `สร้างตาราง "${res.table_name}" จำนวน ${res.row_count.toLocaleString()} แถว พร้อมใช้งาน`
    });
  };

  // Helper for Column Type Badge colors
  const getTypeBadgeClass = (type) => {
    switch (type?.toUpperCase()) {
      case 'INTEGER': return 'badge-type-int';
      case 'REAL': return 'badge-type-real';
      case 'DATE': return 'badge-type-date';
      default: return 'badge-type-text';
    }
  };

  return (
    <div className="app-container">
      {/* Floating Toast Notification */}
      <Toast toast={toast} onClose={() => setToast(null)} />

      {/* 1. Left Sidebar (Collapsible with right-click delete) */}
      <ChatHistorySidebar
        isOpen={isLeftSidebarOpen}
        onToggle={() => setIsLeftSidebarOpen(!isLeftSidebarOpen)}
        sessions={sessions}
        activeSession={activeSession}
        onSelectSession={handleSelectSession}
        onNewChat={handleNewChat}
        onDeleteSession={handleDeleteSession}
        user={user}
      />

      {/* 2. Main Workspace (Split-Screen Layout with Resizable Divider) */}
      <div className="workspace-split-root">
        {/* Top Navbar */}
        <header className="workspace-navbar">
          <div className="navbar-left">
            <div className="session-title-tag">
              <Database size={15} className="text-blue-600" />
              <h2>{sessions.find(s => s.id === activeSession)?.title || 'การวิเคราะห์ข้อมูล'}</h2>
            </div>
          </div>

          <div className="navbar-right">
            {!isRightPanelOpen && (
              <button
                onClick={() => setIsRightPanelOpen(true)}
                className="nav-btn-open-analytics"
                title="เปิดแผงวิเคราะห์และกราฟ"
              >
                <BarChart3 size={14} />
                <span>เปิดแผงวิเคราะห์</span>
              </button>
            )}
          </div>
        </header>

        {/* Split Panes: Left Chat | Resizer Bar | Right Live Dashboard */}
        <div
          ref={splitContainerRef}
          className={`split-view-body ${isDraggingResizer ? 'is-resizing' : ''}`}
        >
          {/* LEFT PANE: Chat Interface */}
          <section
            className={`chat-pane ${!isRightPanelOpen ? 'full-width' : ''}`}
            style={isRightPanelOpen ? { flex: 1, width: 'auto' } : { width: '100%' }}
          >
            <div className="chat-messages-scroll">
              {currentMessages.map((msg) => {
                const isAiWithData = msg.role === 'ai' && (msg.visualization || (msg.rawData && msg.rawData.length > 0) || msg.sql);
                const isCurrentlyActive = activeMessage?.id === msg.id;
                return (
                  <div
                    key={msg.id}
                    className={`message-item-wrapper ${msg.role === 'user' ? 'user-align' : 'ai-align'} ${
                      isAiWithData ? 'clickable-ai-msg' : ''
                    } ${isCurrentlyActive ? 'active-inspected-msg' : ''}`}
                    onClick={() => handleSelectMessage(msg)}
                    title={
                      isAiWithData
                        ? 'คลิกเพื่อเรียกดูแผนภูมิ ตารางข้อมูล และคำสั่ง SQL ในแผงรายงานวิเคราะห์'
                        : undefined
                    }
                  >
                  <div className={`message-avatar ${msg.role === 'user' ? 'user-av' : 'ai-av'}`}>
                    {msg.role === 'user' ? <User size={15} /> : <Bot size={15} />}
                  </div>

                  <div className={`message-card ${msg.role === 'user' ? 'user-card' : 'ai-card'} ${msg.isError ? 'error-card' : ''}`}>
                    {/* Message Header */}
                    <div className="message-card-header">
                      <span className="sender-name">{msg.role === 'user' ? 'ผู้สอบถาม' : 'ผู้ช่วยวิเคราะห์ข้อมูล'}</span>
                      <span className="message-time">{msg.timestamp}</span>
                    </div>

                    {/* Special Upload Card View */}
                    {msg.isUploadNotice && msg.uploadData ? (
                      <div className="upload-success-card-content">
                        <div className="upload-card-top">
                          <CheckCircle2 size={18} className="text-emerald-500 flex-shrink-0" />
                          <div>
                            <div className="upload-main-title">
                              นำเข้าตาราง <strong>"{msg.uploadData.table_name}"</strong> สำเร็จ
                            </div>
                            <div className="upload-meta-row">
                              <span className="upload-meta-pill">
                                <TableIcon size={12} />
                                <span>{msg.uploadData.row_count.toLocaleString()} แถว</span>
                              </span>
                              <span className="upload-meta-pill">
                                <FileSpreadsheet size={12} />
                                <span>{msg.uploadData.encoding || 'UTF-8'}</span>
                              </span>
                            </div>
                          </div>
                        </div>

                        {/* Column Badges Grid */}
                        <div className="upload-columns-section">
                          <div className="columns-section-title">โครงสร้างคอลัมน์ที่ตรวจพบ:</div>
                          <div className="columns-badges-grid">
                            {msg.uploadData.columns.map((colName, cIdx) => {
                              const colType = msg.uploadData.detected_types?.[colName] || 'TEXT';
                              return (
                                <div key={cIdx} className="column-badge-item">
                                  <span className="column-name">{colName}</span>
                                  <span className={`column-type-tag ${getTypeBadgeClass(colType)}`}>
                                    {colType}
                                  </span>
                                </div>
                              );
                            })}
                          </div>
                        </div>

                        {/* Preview Table Action Button */}
                        <div className="upload-action-box">
                          <button
                            className="preview-table-action-btn"
                            onClick={(e) => {
                              e.stopPropagation();
                              setActiveMessage(msg);
                              setAnalyticsTab('table');
                              setIsRightPanelOpen(true);
                            }}
                          >
                            <TableIcon size={14} />
                            <span>ดูตัวอย่างข้อมูลตาราง (10 แถวแรก)</span>
                            <ArrowRight size={13} />
                          </button>
                        </div>
                      </div>
                    ) : (
                      /* Standard Markdown Rendered Content (ปุ่มคัดลอกเฉพาะข้อความของ AI เท่านั้น) */
                      <div className="message-card-body">
                        <MarkdownMessage content={msg.text} allowCopy={msg.role === 'ai'} />
                      </div>
                    )}

                    {/* SQL Query Collapsible Snippet */}
                    {msg.role === 'ai' && msg.sql && !msg.isUploadNotice && (
                      <details className="sql-snippet-box">
                        <summary>
                          <Code size={13} />
                          <span>คำสั่ง SQL ที่ใช้ประมวลผล</span>
                        </summary>
                        <pre className="sql-code-display">{msg.sql}</pre>
                      </details>
                    )}

                    {/* Action Bar: View Table, Export CSV & Pin to Dashboard */}
                    {msg.role === 'ai' && !msg.isError && !msg.isUploadNotice && (msg.sql || msg.visualization || msg.rawData?.length > 0) && (
                      <div className="message-actions-bar">
                        {/* Direct Table View Button from Chat Message */}
                        {msg.rawData && msg.rawData.length > 0 && (
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              setActiveMessage(msg);
                              setAnalyticsTab('table');
                              setIsRightPanelOpen(true);
                            }}
                            className="view-msg-table-btn"
                            title="เปิดดูตารางข้อมูลในแผงด้านข้าง"
                          >
                            <TableIcon size={12} />
                            <span>ดูตารางข้อมูล ({msg.rawData.length.toLocaleString()} รายการ)</span>
                          </button>
                        )}

                        {/* Direct CSV Export from Chat Message */}
                        {msg.rawData && msg.rawData.length > 0 && (
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              exportDataToCsv(msg.rawData, 'query_result');
                            }}
                            className="export-msg-btn"
                            title="ส่งออกผลลัพธ์เป็นไฟล์ CSV สำหรับ Excel"
                          >
                            <Download size={12} />
                            <span>ส่งออก CSV</span>
                          </button>
                        )}

                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handlePinItem(msg);
                          }}
                          className="pin-card-btn"
                          title="บันทึกกราฟและรายงานลงในแดชบอร์ด"
                        >
                          <Pin size={12} />
                          <span>ปักหมุดรายงาน</span>
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              );
            })}

              {/* Instant Feedback Loading Animation */}
              {isLoading && (
                <div className="message-item-wrapper ai-align">
                  <div className="message-avatar ai-av">
                    <Bot size={15} />
                  </div>
                  <div className="message-card ai-card loading-card">
                    <div className="loading-spinner-row">
                      <RefreshCw size={15} className="animate-spin text-blue-600" />
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
                <AlertCircle size={15} className="text-red-500 flex-shrink-0" />
                <span className="error-text">{errorBanner}</span>
                <button onClick={() => setErrorBanner(null)} className="error-dismiss-btn">✕</button>
              </div>
            )}

            {/* Suggested Queries Chips */}
            <div className="suggested-queries-panel">
              <div className="suggested-queries-label">
                <Sparkles size={13} className="text-blue-600" />
                <span>คำถามที่แนะนำ:</span>
              </div>
              <div className="suggested-chips-scroll">
                {suggestedQueries.map((sq, idx) => (
                  <button
                    key={idx}
                    className="query-chip-btn"
                    onClick={() => handleSuggestedChipClick(sq)}
                    disabled={isLoading}
                  >
                    {sq}
                  </button>
                ))}
              </div>
            </div>

            {/* Chat Input Bar with '+' CSV Upload Button */}
            <form onSubmit={handleSendMessage} className="chat-input-container">
              {/* CSV Upload '+' Button */}
              <button
                type="button"
                onClick={() => setIsUploadOpen(true)}
                className="chat-upload-plus-btn"
                title="นำเข้าไฟล์ข้อมูล CSV (+)"
                disabled={isLoading}
              >
                <Plus size={18} />
              </button>

              {/* Text Input */}
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="พิมพ์คำถามวิเคราะห์ข้อมูล เช่น 'แจกแจงจำนวนรายการตามหมวดหมู่' หรือ 'สรุปสถิติสำคัญ'..."
                disabled={isLoading}
                className="chat-text-input"
              />

              {/* Send Button */}
              <button
                type="submit"
                disabled={isLoading || !input.trim()}
                className="chat-send-btn"
                title="ส่งคำถาม"
              >
                <Send size={15} />
                <span>ส่งคำถาม</span>
              </button>
            </form>
          </section>

          {/* DRAGGABLE RESIZER DIVIDER */}
          {isRightPanelOpen && (
            <div
              className={`pane-resizer ${isDraggingResizer ? 'active' : ''}`}
              onMouseDown={handleResizerMouseDown}
              title="คลิกและลากเพื่อปรับขนาดความกว้างของแผงวิเคราะห์ (Resize)"
            >
              <div className="resizer-handle-line"></div>
            </div>
          )}

          {/* RIGHT PANE: Live Analytics Dashboard & Data Workspace (Resizable) */}
          {isRightPanelOpen && (
            <section
              className="analytics-pane"
              style={{ width: `${rightPanelWidth}px`, flexShrink: 0 }}
            >
              <AnalyticsPanel
                activeMessage={activeMessage}
                pinnedItems={pinnedItems}
                onPinItem={handlePinItem}
                onUnpinItem={handleUnpinItem}
                onClose={() => setIsRightPanelOpen(false)}
                activeTab={analyticsTab}
                onTabChange={setAnalyticsTab}
              />
            </section>
          )}
        </div>
      </div>

      {/* CSV File Upload Modal (Opened via '+' button) */}
      <FileUploadModal
        isOpen={isUploadOpen}
        onClose={() => setIsUploadOpen(false)}
        onUploadSuccess={handleUploadSuccess}
      />
    </div>
  );
}
