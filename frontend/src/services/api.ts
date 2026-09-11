import axios from "axios";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Attach JWT token automatically to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("access_token");

    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
  },
  (error) => Promise.reject(error),
);

// Centralized response/error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      const status = error.response.status;

      switch (status) {
        case 400:
          console.error("Bad request:", error.response.data);
          break;

        case 401:
          console.error("Unauthorized request");
          break;

        case 403:
          console.error("Forbidden request");
          break;

        case 404:
          console.error("Resource not found");
          break;

        case 422:
          console.error("Validation error:", error.response.data);
          break;

        case 500:
          console.error("Internal server error");
          break;

        default:
          console.error("API error:", error.response.data);
      }
    } else if (error.request) {
      console.error("No response from server");
    } else {
      console.error("Request error:", error.message);
    }

    return Promise.reject(error);
  },
);

export default api;