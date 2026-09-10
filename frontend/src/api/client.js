import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

const client = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Attach Authorization header if token exists
client.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Unified error normalization interceptor
client.interceptors.response.use(
  (response) => response,
  (error) => {
    let message = 'An unexpected error occurred. Please try again.';

    if (error.response) {
      const status = error.response.status;
      const data = error.response.data;

      // Extract FastAPI detail string or validation array
      if (data && data.detail) {
        if (Array.isArray(data.detail)) {
          message = data.detail.map((err) => `${err.loc?.slice(-1)[0] || 'Field'}: ${err.msg}`).join(', ');
        } else if (typeof data.detail === 'string') {
          message = data.detail;
        }
      } else if (status === 401) {
        message = 'Session expired or unauthorized. Please log in again.';
        // Clear auth on 401 if not already on login page
        if (!window.location.pathname.includes('/login')) {
          localStorage.removeItem('token');
          localStorage.removeItem('user');
        }
      } else if (status === 403) {
        message = 'Forbidden: You do not have permission to perform this action.';
      } else if (status === 404) {
        message = 'The requested resource was not found.';
      } else if (status >= 500) {
        message = 'Internal server error. Please try again later.';
      }
    } else if (error.request) {
      message = 'Unable to connect to the backend server. Please verify the API is running on port 8000.';
    }

    const enhancedError = new Error(message);
    enhancedError.status = error.response ? error.response.status : 0;
    enhancedError.originalResponse = error.response?.data;
    return Promise.reject(enhancedError);
  }
);

export default client;
