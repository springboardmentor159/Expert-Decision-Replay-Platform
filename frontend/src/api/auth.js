import { request } from './client';

export const authApi = {
  login: async (email, password) => {
    // FastAPI OAuth2PasswordRequestForm expects application/x-www-form-urlencoded
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);

    const data = await request('/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData,
    });

    return data;
  },

  register: async (userData) => {
    return await request('/auth/register', {
      method: 'POST',
      body: userData,
    });
  },

  getCurrentUser: async () => {
    return await request('/auth/me');
  },
};
