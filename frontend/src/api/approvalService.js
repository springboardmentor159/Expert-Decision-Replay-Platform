import client from './client';

export const approvalService = {
  async getApprovals(params = {}) {
    const response = await client.get('/approvals', { params });
    return response.data;
  },

  async getApproval(id) {
    const response = await client.get(`/approvals/${id}`);
    return response.data;
  },

  async createApproval(data) {
    const response = await client.post('/approvals', data);
    return response.data;
  },

  async approveDecision(id, comments = '') {
    const response = await client.post(`/approvals/${id}/approve`, { comments });
    return response.data;
  },

  async rejectDecision(id, comments = '') {
    const response = await client.post(`/approvals/${id}/reject`, { comments });
    return response.data;
  },
};
