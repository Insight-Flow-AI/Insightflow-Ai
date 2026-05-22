import { api } from './api';

export const analyticsService = {
  async getCharts(datasetId = '') {
    const queryParam = datasetId ? `?datasetId=${datasetId}` : '';
    return await api.get(`/charts${queryParam}`);
  },

  async getReport(datasetId = '') {
    const queryParam = datasetId ? `?datasetId=${datasetId}` : '';
    return await api.get(`/analytics/report${queryParam}`);
  },

  async getPredictions(datasetId = '') {
    const queryParam = datasetId ? `?datasetId=${datasetId}` : '';
    return await api.get(`/predictions${queryParam}`);
  },

  async askChatbot(query, datasetId = '') {
    const queryParam = datasetId ? `?datasetId=${datasetId}` : '';
    return await api.post(`/chat${queryParam}`, { query });
  },
};
