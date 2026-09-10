import { request } from './client';

export const usersApi = {
  getUsers: async () => {
    return await request('/users');
  },

  getReviewers: async () => {
    return await request('/users/reviewers');
  },

  createUser: async (userData) => {
    return await request('/users', {
      method: 'POST',
      body: userData,
    });
  },

  getUserById: async (id) => {
    return await request(`/users/${id}`);
  },

  updateUser: async (id, userData) => {
    return await request(`/users/${id}`, {
      method: 'PUT',
      body: userData,
    });
  },

  deleteUser: async (id) => {
    return await request(`/users/${id}`, {
      method: 'DELETE',
    });
  },

  getMyProfile: async () => {
    return await request('/users/me');
  },

  getMyStatistics: async () => {
    return await request('/users/me/statistics');
  },
};
