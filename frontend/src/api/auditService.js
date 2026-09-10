import client from './client';

export const auditService = {
  async getAuditLogs(params = {}) {
    const response = await client.get('/audit-logs', { params });
    return response.data;
  },

  async getSecurityLogs(params = {}) {
    const response = await client.get('/security-logs', { params });
    return response.data;
  },

  async getAccessLogs(params = {}) {
    const response = await client.get('/access-logs', { params });
    return response.data;
  },

  async getActivities(params = {}) {
    const response = await client.get('/activities', { params });
    return response.data;
  },
};
