import api from './api';

export const alternativeService = {
  // Get all alternatives for a decision
  getAlternatives: async (decisionId) => {
    const response = await api.get(`/decisions/${decisionId}/alternatives`);
    return response.data;
  },

  // Create new alternative
  createAlternative: async (decisionId, alternativeData) => {
    const response = await api.post(`/decisions/${decisionId}/alternatives`, alternativeData);
    return response.data;
  },

  // Get single alternative
  getAlternativeById: async (id) => {
    const response = await api.get(`/alternatives/${id}`);
    return response.data;
  },

  // Update alternative
  updateAlternative: async (id, alternativeData) => {
    const response = await api.put(`/alternatives/${id}`, alternativeData);
    return response.data;
  },

  // Delete alternative
  deleteAlternative: async (id) => {
    const response = await api.delete(`/alternatives/${id}`);
    return response.data;
  },

  // Compare alternatives for a decision
  compareAlternatives: async (decisionId) => {
    const response = await api.get(`/decisions/${decisionId}/alternatives/compare`);
    return response.data;
  },
};
