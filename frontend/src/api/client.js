import axios from "axios";

// Centralized API/service layer (Part 16).
// Every page should go through this client instead of calling axios directly.

const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export const TOKEN_KEY = "edrp_access_token";

export function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token) {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
}

const client = axios.create({
  baseURL: BASE_URL,
});

// Attach JWT to every request if we have one.
client.interceptors.request.use((config) => {
  const token = getToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// A single place to normalize backend errors so every page can show a
// consistent, human-readable message (Part 16 / Part 17).
function extractMessage(error) {
  const data = error?.response?.data;
  if (!data) return "Network error. Please check your connection and try again.";
  if (typeof data.detail === "string") return data.detail;
  if (Array.isArray(data.detail)) {
    // FastAPI 422 validation errors come back as a list of {loc, msg, type}
    return data.detail
      .map((d) => (d.loc ? `${d.loc[d.loc.length - 1]}: ${d.msg}` : d.msg))
      .join(", ");
  }
  return "Something went wrong. Please try again.";
}

let onUnauthorized = null;
export function registerUnauthorizedHandler(fn) {
  onUnauthorized = fn;
}

client.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error?.response?.status;

    if (status === 401) {
      clearToken();
      if (onUnauthorized) onUnauthorized();
    }

    const normalized = {
      status: status || 0,
      message: extractMessage(error),
      raw: error,
    };

    return Promise.reject(normalized);
  }
);

export default client;
