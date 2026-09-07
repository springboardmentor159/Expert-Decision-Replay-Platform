import { request } from './client';

export const auditApi = {
  getLogs: async (params = {}) => {
    const q = new URLSearchParams();
    if (params.user_id) q.append('user_id', params.user_id);
    if (params.action) q.append('action', params.action);
    if (params.entity_type) q.append('entity_type', params.entity_type);
    if (params.entity_id) q.append('entity_id', params.entity_id);
    if (params.start_date) q.append('start_date', params.start_date);
    if (params.end_date) q.append('end_date', params.end_date);
    if (params.page) q.append('page', params.page);
    if (params.page_size) q.append('page_size', params.page_size);

    const str = q.toString();
    return await request(`/audit-logs${str ? `?${str}` : ''}`);
  },

  getLogById: async (id) => {
    return await request(`/audit-logs/${id}`);
  },

  getAccessLogs: async (params = {}) => {
    const q = new URLSearchParams();
    if (params.page) q.append('page', params.page);
    if (params.page_size) q.append('page_size', params.page_size);
    const str = q.toString();
    return await request(`/access-logs${str ? `?${str}` : ''}`);
  },

  getSecurityLogs: async (params = {}) => {
    const q = new URLSearchParams();
    if (params.page) q.append('page', params.page);
    if (params.page_size) q.append('page_size', params.page_size);
    const str = q.toString();
    return await request(`/security-logs${str ? `?${str}` : ''}`);
  },
};
