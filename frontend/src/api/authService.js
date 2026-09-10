import client from './client';

export const authService = {
  async login(email, password) {
    const response = await client.post('/auth/login', { email, password });
    return response.data;
  },

  async register(userData) {
    const response = await client.post('/users', userData);
    return response.data;
  },

  async getProfile() {
    const response = await client.get('/users/me');
    return response.data;
  },
};

export const userService = {
  async getUsers() {
    const response = await client.get('/users');
    return response.data;
  },

  async getUser(id) {
    const response = await client.get(`/users/${id}`);
    return response.data;
  },

  async updateUser(id, data) {
    const response = await client.put(`/users/${id}`, data);
    return response.data;
  },

  async deleteUser(id) {
    const response = await client.delete(`/users/${id}`);
    return response.data;
  },
};
