import api from './api';

export const getPinnedDashboard = async () => {
  const response = await api.get('/part4/pinned-dashboard');
  return response.data.pinned_items;
};

export const pinItemToDashboard = async (item) => {
  const response = await api.post('/part4/pin-item', item);
  return response.data;
};

export const unpinItem = async (itemId) => {
  const response = await api.delete(`/part4/pin-item/${itemId}`);
  return response.data;
};
