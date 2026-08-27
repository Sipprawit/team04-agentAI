import api from './api';

export const sendQuery = async (queryText, chatHistory = []) => {
  const response = await api.post('/query', {
    q: queryText,
    chat_history: chatHistory,
  });
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
