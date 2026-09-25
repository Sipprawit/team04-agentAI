import api from './api';

export const sendQuery = async (queryText, chatHistory = [], sessionId = null, tableName = null) => {
  const payload = {
    q: queryText,
    chat_history: chatHistory,
  };
  if (sessionId) payload.session_id = sessionId;
  if (tableName) payload.table_name = tableName;
  const response = await api.post('/query', payload);
  return response.data;
};

export const listSessions = async () => {
  const response = await api.get('/part4/sessions');
  return response.data.sessions || [];
};

export const createSession = async (sessionId, title = 'การสนทนาใหม่', tableName = null) => {
  const payload = {
    session_id: sessionId,
    title,
  };
  if (tableName) payload.table_name = tableName;
  const response = await api.post('/part4/sessions', payload);
  return response.data;
};

export const updateSession = async (sessionId, title = null, tableName = null) => {
  const payload = {};
  if (title !== null && title !== undefined) payload.title = title;
  if (tableName !== null && tableName !== undefined) payload.table_name = tableName;
  const response = await api.put(`/part4/sessions/${sessionId}`, payload);
  return response.data;
};

export const deleteSession = async (sessionId) => {
  const response = await api.delete(`/part4/sessions/${sessionId}`);
  return response.data;
};

export const getChatHistory = async (sessionId) => {
  const response = await api.get(`/part4/chat-history/${sessionId}`);
  return response.data;
};

export const saveChatMessage = async (sessionId, message) => {
  const response = await api.post(`/part4/chat-history/${sessionId}`, message);
  return response.data;
};

export const fetchSchemaDict = async () => {
  const response = await api.get('/part1/schema-dict');
  return response.data;
};

