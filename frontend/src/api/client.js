import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor: Inject JWT token if present
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor: Global error handler & auth handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      const { status, data } = error.response;

      // Format FastAPI 422 validation errors or detail strings
      let formattedMessage = 'An unexpected error occurred';

      if (data?.detail) {
        if (typeof data.detail === 'string') {
          formattedMessage = data.detail;
        } else if (Array.isArray(data.detail)) {
          // FastAPI validation error list
          formattedMessage = data.detail
            .map((err) => {
              const field = err.loc ? err.loc[err.loc.length - 1] : 'field';
              return `${field}: ${err.msg}`;
            })
            .join('; ');
        }
      } else if (data?.message) {
        formattedMessage = data.message;
      }

      error.formattedMessage = formattedMessage;

      // Auto logout on 401 if not already on the login page
      if (status === 401 && !window.location.pathname.includes('/login')) {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        window.dispatchEvent(new CustomEvent('auth:unauthorized'));
      }
    } else if (error.request) {
      error.formattedMessage = 'Network error: Unable to connect to server. Please ensure the backend is running.';
    } else {
      error.formattedMessage = error.message;
    }

    return Promise.reject(error);
  }
);

export default apiClient;
