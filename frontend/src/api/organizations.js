import { request } from './client';

export const organizationsApi = {
  getPublicList: async () => {
    return await request('/organizations/public/list');
  },

  getAll: async () => {
    return await request('/organizations');
  },

  getById: async (id) => {
    return await request(`/organizations/${id}`);
  },
};
