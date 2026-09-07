import { request } from './client';

export const alternativesApi = {
  getByDecisionId: async (decisionId) => {
    return await request(`/decisions/${decisionId}/alternatives`);
  },

  create: async (decisionId, data) => {
    return await request(`/decisions/${decisionId}/alternatives`, {
      method: 'POST',
      body: data,
    });
  },

  getById: async (id) => {
    return await request(`/alternatives/${id}`);
  },

  update: async (id, data) => {
    return await request(`/alternatives/${id}`, {
      method: 'PUT',
      body: data,
    });
  },

  delete: async (id) => {
    return await request(`/alternatives/${id}`, {
      method: 'DELETE',
    });
  },

  compare: async (decisionId) => {
    return await request(`/decisions/${decisionId}/alternatives/compare`);
  },
};
