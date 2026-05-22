import { api } from './api';

export const datasetService = {
  async uploadDataset(file) {
    const formData = new FormData();
    formData.append('file', file);
    return await api.upload('/dataset/upload', formData);
  },

  async getDatasetHistory() {
    return await api.get('/dataset/history');
  },
};
