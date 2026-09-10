import axios from 'axios';

// Direct backend API URL (FastAPI running on port 8000)
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to automatically attach JWT Bearer token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor to handle errors gracefully
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      const { status, data } = error.response;

      // 401 Unauthorized: token expired or invalid
      if (status === 401) {
        // Prevent redirect loop if already on login
        if (!window.location.pathname.includes('/login') && !window.location.pathname.includes('/register')) {
          localStorage.removeItem('token');
          localStorage.removeItem('user');
          window.location.href = '/login?expired=true';
        }
      }

      // Format clean error message from FastAPI HTTPException detail
      let errorMessage = 'An unexpected server error occurred.';
      if (typeof data?.detail === 'string') {
        errorMessage = data.detail;
      } else if (Array.isArray(data?.detail)) {
        // Pydantic validation error array
        errorMessage = data.detail.map((err) => `${err.loc?.slice(-1)[0] || 'Field'}: ${err.msg}`).join(', ');
      } else if (data?.message) {
        errorMessage = data.message;
      }

      error.userMessage = errorMessage;
    } else if (error.request) {
      error.userMessage = 'Cannot reach the backend server. Please ensure the API is running at http://localhost:8000.';
    } else {
      error.userMessage = error.message || 'Request configuration error.';
    }

    return Promise.reject(error);
  }
);

export default api;
