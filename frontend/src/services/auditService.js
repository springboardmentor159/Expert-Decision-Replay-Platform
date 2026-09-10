import api from './api';

export const auditService = {
  // Get paginated audit logs (Admin only)
  getAuditLogs: async (params = {}) => {
    const response = await api.get('/audit-logs', { params });
    return response.data;
  },

  // Get system activities feed
  getActivities: async (limit = 30) => {
    const response = await api.get('/activities', { params: { limit } });
    return response.data;
  },

  // Get security logs (Admin only)
  getSecurityLogs: async (limit = 50) => {
    const response = await api.get('/security-logs', { params: { limit } });
    return response.data;
  },

  // Get access logs (Admin only)
  getAccessLogs: async (limit = 50) => {
    const response = await api.get('/access-logs', { params: { limit } });
    return response.data;
  },
};
