import axios from "axios";

const api = axios.create({
  baseURL:
    import.meta.env.VITE_API_BASE_URL ||
    "http://localhost:8000",
  headers: {
    "Content-Type": "application/json",
  },
});

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("access_token");

    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
  },
  (error) => {
    return Promise.reject(error);
  },
);

api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    const status = error?.response?.status;

    // =========================
    // 401 — UNAUTHORIZED
    // =========================

    if (status === 401) {
      localStorage.removeItem("access_token");
      localStorage.removeItem("user");

      if (window.location.pathname !== "/login") {
        window.location.href = "/login";
      }
    }

    // =========================
    // 403 — FORBIDDEN
    // =========================

    if (status === 403) {
      if (window.location.pathname !== "/forbidden") {
        window.location.href = "/forbidden";
      }
    }

    return Promise.reject(error);
  },
);

export default api;