import api from './api';

export const authService = {
  // Login with credentials
  login: async (email, password) => {
    const response = await api.post('/auth/login', { email, password });
    return response.data;
  },

  // Register new user
  register: async (userData) => {
    const response = await api.post('/users', userData);
    return response.data;
  },

  // Fetch current user profile
  getCurrentUser: async () => {
    const response = await api.get('/users/me');
    return response.data;
  },

  // List all users (Protected)
  getUsers: async () => {
    const response = await api.get('/users');
    return response.data;
  },

  // Update user profile (Admin / Manager / Self)
  updateUser: async (userId, data) => {
    const response = await api.put(`/users/${userId}`, data);
    return response.data;
  },

  // Delete user (Admin only)
  deleteUser: async (userId) => {
    const response = await api.delete(`/users/${userId}`);
    return response.data;
  },
};
