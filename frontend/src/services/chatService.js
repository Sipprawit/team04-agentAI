import api from './api';

export const sendQuery = async (queryText, chatHistory = []) => {
  const response = await api.post('/query', {
    q: queryText,
    chat_history: chatHistory,
  });
  return response.data;
};

export const listSessions = async () => {
  const response = await api.get('/part4/sessions');
  return response.data.sessions || [];
};

export const createSession = async (sessionId, title = 'การสนทนาใหม่') => {
  const response = await api.post('/part4/sessions', {
    session_id: sessionId,
    title,
  });
  return response.data;
};

export const updateSession = async (sessionId, title) => {
  const response = await api.put(`/part4/sessions/${sessionId}`, { title });
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

