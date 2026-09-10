import api from './api';

export const decisionService = {
  // List decisions with optional filters
  getDecisions: async (params = {}) => {
    const response = await api.get('/decisions', { params });
    return response.data;
  },

  // Full-text search and knowledge repository filtering
  searchDecisions: async (params = {}) => {
    const response = await api.get('/decisions/search', { params });
    return response.data;
  },

  // Single decision details
  getDecisionById: async (id) => {
    const response = await api.get(`/decisions/${id}`);
    return response.data;
  },

  // Create new decision
  createDecision: async (decisionData) => {
    const response = await api.post('/decisions', decisionData);
    return response.data;
  },

  // Update existing decision
  updateDecision: async (id, decisionData) => {
    const response = await api.put(`/decisions/${id}`, decisionData);
    return response.data;
  },

  // Delete decision
  deleteDecision: async (id) => {
    const response = await api.delete(`/decisions/${id}`);
    return response.data;
  },

  // Update decision status
  updateStatus: async (id, status) => {
    const response = await api.patch(`/decisions/${id}/status`, { status });
    return response.data;
  },

  // Update rationale
  updateRationale: async (id, rationale) => {
    const response = await api.put(`/decisions/${id}/rationale`, { rationale });
    return response.data;
  },

  // Get rationale
  getRationale: async (id) => {
    const response = await api.get(`/decisions/${id}/rationale`);
    return response.data;
  },

  // Assign tags to decision
  assignTags: async (id, tags) => {
    const response = await api.post(`/decisions/${id}/tags`, { tags });
    return response.data;
  },

  // Get tags for decision
  getTags: async (id) => {
    const response = await api.get(`/decisions/${id}/tags`);
    return response.data;
  },

  // Get version history list
  getVersions: async (id) => {
    const response = await api.get(`/decisions/${id}/versions`);
    return response.data;
  },

  // Get specific version details
  getVersionDetails: async (id, versionNumber) => {
    const response = await api.get(`/decisions/${id}/versions/${versionNumber}`);
    return response.data;
  },

  // Get visual timeline of events
  getTimeline: async (id) => {
    const response = await api.get(`/decisions/${id}/timeline`);
    return response.data;
  },
};
