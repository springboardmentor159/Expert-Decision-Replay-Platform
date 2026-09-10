import client from './client';

export const alternativeService = {
  async getAlternatives(decisionId) {
    const response = await client.get(`/decisions/${decisionId}/alternatives`);
    return response.data;
  },

  async createAlternative(decisionId, data) {
    const response = await client.post(`/decisions/${decisionId}/alternatives`, data);
    return response.data;
  },

  async compareAlternatives(decisionId) {
    const response = await client.get(`/decisions/${decisionId}/alternatives/compare`);
    return response.data;
  },

  async updateAlternative(alternativeId, data) {
    const response = await client.put(`/alternatives/${alternativeId}`, data);
    return response.data;
  },

  async deleteAlternative(alternativeId) {
    const response = await client.delete(`/alternatives/${alternativeId}`);
    return response.data;
  },
};
