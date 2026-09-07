import { request } from './client';

export const decisionsApi = {
  getDecisions: async (params = {}) => {
    const query = new URLSearchParams();
    if (params.q) query.append('q', params.q);
    if (params.keyword) query.append('keyword', params.keyword);
    if (params.category) query.append('category', params.category);
    if (params.status) query.append('status', params.status);
    if (params.tag) query.append('tag', params.tag);
    if (params.page) query.append('page', params.page);
    if (params.page_size) query.append('page_size', params.page_size);

    const queryString = query.toString();
    return await request(`/decisions${queryString ? `?${queryString}` : ''}`);
  },

  searchDecisions: async (params = {}) => {
    const query = new URLSearchParams();
    if (params.q) query.append('q', params.q);
    if (params.keyword) query.append('keyword', params.keyword);
    if (params.category) query.append('category', params.category);
    if (params.status) query.append('status', params.status);
    if (params.tag) query.append('tag', params.tag);
    if (params.page) query.append('page', params.page);
    if (params.page_size) query.append('page_size', params.page_size);

    const queryString = query.toString();
    return await request(`/decisions/search${queryString ? `?${queryString}` : ''}`);
  },

  getDecisionDetail: async (id) => {
    return await request(`/decisions/${id}/detail`);
  },

  getDecision: async (id) => {
    return await request(`/decisions/${id}`);
  },

  createDecision: async (data) => {
    return await request('/decisions', {
      method: 'POST',
      body: data,
    });
  },

  updateDecision: async (id, data) => {
    return await request(`/decisions/${id}`, {
      method: 'PUT',
      body: data,
    });
  },

  deleteDecision: async (id) => {
    return await request(`/decisions/${id}`, {
      method: 'DELETE',
    });
  },

  submitDecision: async (id) => {
    return await request(`/decisions/${id}/submit`, {
      method: 'POST',
    });
  },

  updateStatus: async (id, status) => {
    return await request(`/decisions/${id}/status`, {
      method: 'PATCH',
      body: { status },
    });
  },

  getTimeline: async (id) => {
    return await request(`/decisions/${id}/timeline`);
  },

  getVersions: async (id) => {
    return await request(`/decisions/${id}/versions`);
  },

  getVersion: async (id, versionNumber) => {
    return await request(`/decisions/${id}/versions/${versionNumber}`);
  },

  getTags: async (id) => {
    return await request(`/decisions/${id}/tags`);
  },

  addTag: async (id, name) => {
    return await request(`/decisions/${id}/tags`, {
      method: 'POST',
      body: { name },
    });
  },

  removeTag: async (id, tagId) => {
    return await request(`/decisions/${id}/tags/${tagId}`, {
      method: 'DELETE',
    });
  },
};
