import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://127.0.0.1:8000",
  headers: { "Content-Type": "application/json" },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 && !window.location.pathname.includes("/login")) {
      localStorage.removeItem("access_token");
    }
    return Promise.reject(error);
  }
);

const data = (r) => r.data;

export const authApi = {
  login: async (email, password) => {
    const body = new URLSearchParams();
    body.append("username", email);
    body.append("password", password);
    return data(await api.post("/auth/login", body, {
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
    }));
  },
  register: async (payload) => data(await api.post("/auth/register", payload)),
};

export const usersApi = {
  list: async () => data(await api.get("/users")),
  get: async (id) => data(await api.get(`/users/${id}`)),
  create: async (payload) => data(await api.post("/users", payload)),
  update: async (id, payload) => data(await api.put(`/users/${id}`, payload)),
  remove: async (id) => data(await api.delete(`/users/${id}`)),
};

export const decisionsApi = {
  list: async (params = {}) => data(await api.get("/decisions", { params })),
  get: async (id) => data(await api.get(`/decisions/${id}`)),
  create: async (payload) => data(await api.post("/decisions", payload)),
  update: async (id, payload) => data(await api.put(`/decisions/${id}`, payload)),
  updateStatus: async (id, status) => data(await api.patch(`/decisions/${id}/status`, { status })),
  versions: async (id) => data(await api.get(`/decisions/${id}/versions`)),
  version: async (id, version) => data(await api.get(`/decisions/${id}/versions/${version}`)),
  history: async (id) => data(await api.get(`/decisions/${id}/history`)),
};

export const alternativesApi = {
  list: async (decisionId) => data(await api.get(`/decisions/${decisionId}/alternatives`)),
  get: async (id) => data(await api.get(`/alternatives/${id}`)),
  create: async (decisionId, payload) => data(await api.post(`/decisions/${decisionId}/alternatives`, payload)),
  update: async (id, payload) => data(await api.put(`/alternatives/${id}`, payload)),
  compare: async (decisionId) => data(await api.get(`/decisions/${decisionId}/alternatives/compare`)),
};

export const commentsApi = {
  list: async (decisionId) => data(await api.get(`/decisions/${decisionId}/comments`)),
  get: async (id) => data(await api.get(`/comments/${id}`)),
  create: async (decisionId, payload) => data(await api.post(`/decisions/${decisionId}/comments`, payload)),
  update: async (id, payload) => data(await api.put(`/comments/${id}`, payload)),
  remove: async (id) => data(await api.delete(`/comments/${id}`)),
  reply: async (threadId, payload) => data(await api.post(`/comments/threads/${threadId}/comments`, payload)),
};

export const meetingNotesApi = {
  list: async (decisionId) => data(await api.get(`/decisions/${decisionId}/meeting-notes`)),
  get: async (id) => data(await api.get(`/meeting-notes/${id}`)),
  create: async (decisionId, payload) => data(await api.post(`/decisions/${decisionId}/meeting-notes`, payload)),
  update: async (id, payload) => data(await api.put(`/meeting-notes/${id}`, payload)),
  remove: async (id) => data(await api.delete(`/meeting-notes/${id}`)),
};

export const rationaleApi = {
  get: async (decisionId) => data(await api.get(`/decisions/${decisionId}/rationale`)),
  update: async (decisionId, rationale) => data(await api.put(`/decisions/${decisionId}/rationale`, { rationale })),
};

export const tagsApi = {
  list: async () => data(await api.get("/tags")),
  getDecisionTags: async (decisionId) => data(await api.get(`/decisions/${decisionId}/tags`)),
  create: async (name) => data(await api.post("/tags", { name })),
  remove: async (tagId) => data(await api.delete(`/tags/${tagId}`)),
  addToDecision: async (decisionId, tagId) => data(await api.post(`/decisions/${decisionId}/tags/${tagId}`)),
  removeFromDecision: async (decisionId, tagId) => data(await api.delete(`/decisions/${decisionId}/tags/${tagId}`)),
};

export const approvalsApi = {
  list: async () => data(await api.get("/approvals")),
  pending: async () => data(await api.get("/approvals/pending")),
  get: async (id) => data(await api.get(`/approvals/${id}`)),
  create: async (payload) => data(await api.post("/approvals", payload)),
  action: async (id, status) => data(await api.patch(`/approvals/${id}`, { status })),
};

export const dashboardApi = {
  employee: async () => data(await api.get("/dashboard/employee")),
  employeeActivities: async () => data(await api.get("/dashboard/employee/recent-activities")),
  manager: async () => data(await api.get("/dashboard/manager")),
  managerPending: async () => data(await api.get("/dashboard/manager/pending-approvals")),
  managerStats: async () => data(await api.get("/dashboard/manager/statistics")),
  managerActivities: async () => data(await api.get("/dashboard/manager/recent-activities")),
  admin: async () => data(await api.get("/dashboard/admin")),
  adminAnalytics: async (params) => data(await api.get("/dashboard/admin/analytics", { params })),
  adminDecisionActivity: async () => data(await api.get("/dashboard/admin/decision-activity")),
  adminApprovalStats: async () => data(await api.get("/dashboard/admin/approval-statistics")),
  adminActivities: async () => data(await api.get("/dashboard/admin/recent-activities")),
};

export const activitiesApi = {
  list: async (params = {}) => data(await api.get("/activities", { params })),
};

export const auditApi = {
  list: async (params = {}) => data(await api.get("/audit-logs", { params })),
};

export const reportsApi = {
  list: async (type, params = {}) => data(await api.get(`/reports/${type}`, { params })),
  download: async (type, format, params = {}) => {
    const response = await api.get(`/reports/${type}/${format}`, {
      params,
      responseType: "blob",
    });
    return response;
  },
};

export default api;
