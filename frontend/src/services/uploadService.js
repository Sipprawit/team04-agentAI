import api from './api';

export const uploadCsvFile = async (file, tableName) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('table_name', tableName);

  const response = await api.post('/part1/upload-csv', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const getDatabaseSchema = async () => {
  const response = await api.get('/part1/schema');
  return response.data;
};

export const getAuditStats = async () => {
  const response = await api.get('/part1/audit-stats');
  return response.data;
};
