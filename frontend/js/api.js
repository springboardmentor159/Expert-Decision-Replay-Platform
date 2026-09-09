// Centralized API Client & Service Layer

const API_BASE = '';

export class ApiError extends Error {
  constructor(message, status, data = null) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.data = data;
  }
}

let onUnauthorizedCallback = null;
export function setUnauthorizedHandler(callback) {
  onUnauthorizedCallback = callback;
}

export async function request(endpoint, options = {}) {
  const token = sessionStorage.getItem('edr_token');
  const headers = { ...(options.headers || {}) };

  const isFormData = options.body instanceof FormData || options.body instanceof URLSearchParams;
  if (!isFormData && options.body && typeof options.body === 'object') {
    headers['Content-Type'] = 'application/json';
    options.body = JSON.stringify(options.body);
  }

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
  });

  if (response.status === 401) {
    if (onUnauthorizedCallback) {
      onUnauthorizedCallback();
    }
    throw new ApiError('Your session has expired. Please sign in again.', 401);
  }

  if (response.status === 403) {
    throw new ApiError('You do not have permission to perform this action.', 403);
  }

  if (response.status === 404) {
    throw new ApiError('The requested resource was not found.', 404);
  }

  if (response.status === 204) {
    return null;
  }

  if (!response.ok) {
    let errorMsg = `Server error (${response.status})`;
    let errData = null;
    try {
      errData = await response.json();
      if (errData && errData.detail) {
        if (Array.isArray(errData.detail)) {
          errorMsg = errData.detail.map(e => e.msg || e.message || JSON.stringify(e)).join(', ');
        } else if (typeof errData.detail === 'string') {
          errorMsg = errData.detail;
        }
      }
    } catch {
      // response wasn't json
    }
    throw new ApiError(errorMsg, response.status, errData);
  }

  const contentType = response.headers.get('content-type') || '';
  if (contentType.includes('application/json')) {
    return response.json();
  }

  return response.blob();
}

// Auth APIs
export const authApi = {
  login: async (email, password) => {
    const body = new URLSearchParams();
    body.append('username', email);
    body.append('password', password);
    return request('/token', {
      method: 'POST',
      body,
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
  },
  register: async (userData) => {
    return request('/users', {
      method: 'POST',
      body: userData,
    });
  },
  getProfile: async () => {
    try {
      return await request('/users/me');
    } catch {
      return null;
    }
  },
  listUsers: async () => {
    return request('/users');
  },
};

// Decision APIs
export const decisionsApi = {
  list: async (filters = {}) => {
    const params = new URLSearchParams();
    if (filters.status) params.set('status', filters.status);
    if (filters.category) params.set('category', filters.category);
    if (filters.tag) params.set('tag', filters.tag);
    if (filters.page) params.set('page', filters.page);
    if (filters.page_size) params.set('page_size', filters.page_size);
    if (filters.sort) params.set('sort', filters.sort);
    if (filters.order) params.set('order', filters.order);
    const query = params.toString();
    return request(`/decisions${query ? `?${query}` : ''}`);
  },
  search: async (q, filters = {}) => {
    const params = new URLSearchParams({ q });
    if (filters.status) params.set('status', filters.status);
    if (filters.category) params.set('category', filters.category);
    if (filters.tag) params.set('tag', filters.tag);
    if (filters.page) params.set('page', filters.page);
    if (filters.page_size) params.set('page_size', filters.page_size);
    return request(`/decisions/search?${params.toString()}`);
  },
  get: async (id) => {
    return request(`/decisions/${id}`);
  },
  create: async (data) => {
    return request('/decisions', {
      method: 'POST',
      body: data,
    });
  },
  update: async (id, data) => {
    return request(`/decisions/${id}`, {
      method: 'PUT',
      body: data,
    });
  },
  updateStatus: async (id, status) => {
    return request(`/decisions/${id}/status`, {
      method: 'PATCH',
      body: { status },
    });
  },
  updateRationale: async (id, rationale) => {
    return request(`/decisions/${id}/rationale`, {
      method: 'PUT',
      body: { rationale },
    });
  },
  delete: async (id) => {
    return request(`/decisions/${id}`, {
      method: 'DELETE',
    });
  },
  getTimeline: async (id) => {
    return request(`/decisions/${id}/timeline`);
  },
  getTags: async (id) => {
    return request(`/decisions/${id}/tags`);
  },
  assignTags: async (id, tagIds) => {
    return request(`/decisions/${id}/tags`, {
      method: 'POST',
      body: { tag_ids: tagIds },
    });
  },
  removeTag: async (id, tagId) => {
    return request(`/decisions/${id}/tags/${tagId}`, {
      method: 'DELETE',
    });
  },
  getVersions: async (id) => {
    return request(`/decisions/${id}/versions`);
  },
  getHistory: async (id) => {
    return request(`/decisions/${id}/history`);
  },
};

// Alternatives APIs
export const alternativesApi = {
  listForDecision: async (decisionId) => {
    return request(`/decisions/${decisionId}/alternatives`);
  },
  compare: async (decisionId) => {
    return request(`/decisions/${decisionId}/alternatives/compare`);
  },
  createForDecision: async (decisionId, data) => {
    return request(`/decisions/${decisionId}/alternatives`, {
      method: 'POST',
      body: data,
    });
  },
  get: async (id) => {
    return request(`/alternatives/${id}`);
  },
  update: async (id, data) => {
    return request(`/alternatives/${id}`, {
      method: 'PUT',
      body: data,
    });
  },
  delete: async (id) => {
    return request(`/alternatives/${id}`, {
      method: 'DELETE',
    });
  },
};

// Discussions, Comments & Meeting Notes
export const discussionsApi = {
  getComments: async (decisionId) => {
    return request(`/decisions/${decisionId}/comments`);
  },
  addComment: async (decisionId, content) => {
    return request(`/decisions/${decisionId}/comments`, {
      method: 'POST',
      body: { content },
    });
  },
  deleteComment: async (commentId) => {
    return request(`/comments/${commentId}`, {
      method: 'DELETE',
    });
  },
  getThreads: async (decisionId) => {
    return request(`/decisions/${decisionId}/threads`);
  },
  createThread: async (decisionId, data) => {
    return request(`/decisions/${decisionId}/threads`, {
      method: 'POST',
      body: data,
    });
  },
  getThreadComments: async (threadId) => {
    return request(`/threads/${threadId}/comments`);
  },
  addThreadComment: async (threadId, content) => {
    return request(`/threads/${threadId}/comments`, {
      method: 'POST',
      body: { content },
    });
  },
  getMeetingNotes: async (decisionId) => {
    return request(`/decisions/${decisionId}/meeting-notes`);
  },
  createMeetingNote: async (decisionId, data) => {
    return request(`/decisions/${decisionId}/meeting-notes`, {
      method: 'POST',
      body: data,
    });
  },
};

// Approvals
export const approvalsApi = {
  assign: async (decisionId, reviewerId) => {
    return request(`/decisions/${decisionId}/approvals`, {
      method: 'POST',
      body: { reviewer_id: reviewerId },
    });
  },
  list: async () => {
    return request('/approvals');
  },
  listPending: async () => {
    return request('/approvals/pending');
  },
  action: async (approvalId, status, comments = '') => {
    return request(`/approvals/${approvalId}`, {
      method: 'PATCH',
      body: { status, comments },
    });
  },
};

// Dashboards
export const dashboardApi = {
  getEmployee: async () => request('/dashboard/employee'),
  getEmployeeDecisions: async () => request('/dashboard/employee/decisions'),
  getEmployeePendingReviews: async () => request('/dashboard/employee/pending-reviews'),
  getEmployeeRecentActivities: async () => request('/dashboard/employee/recent-activities'),
  getManager: async () => request('/dashboard/manager'),
  getManagerTeamDecisions: async () => request('/dashboard/manager/team-decisions'),
  getManagerPendingApprovals: async () => request('/dashboard/manager/pending-approvals'),
  getManagerStatistics: async () => request('/dashboard/manager/statistics'),
  getAdmin: async () => request('/dashboard/admin'),
  getAdminAnalytics: async (startDate, endDate) => {
    const params = new URLSearchParams();
    if (startDate) params.set('start_date', startDate);
    if (endDate) params.set('end_date', endDate);
    const q = params.toString();
    return request(`/dashboard/admin/analytics${q ? `?${q}` : ''}`);
  },
  getAdminApprovalStats: async () => request('/dashboard/admin/approval-statistics'),
  getAdminDecisionActivity: async () => request('/dashboard/admin/decision-activity'),
  getAdminUserActivity: async () => request('/dashboard/admin/user-activity'),
};

// Reports & File Export
export const reportsApi = {
  decisions: async (filters = {}) => {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([k, v]) => { if (v) params.set(k, v); });
    const q = params.toString();
    return request(`/reports/decisions${q ? `?${q}` : ''}`);
  },
  exportDecisions: async (format, filters = {}) => {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([k, v]) => { if (v) params.set(k, v); });
    const q = params.toString();
    return request(`/reports/decisions/export/${format}${q ? `?${q}` : ''}`);
  },
  approvals: async (filters = {}) => {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([k, v]) => { if (v) params.set(k, v); });
    const q = params.toString();
    return request(`/reports/approvals${q ? `?${q}` : ''}`);
  },
  exportApprovals: async (format, filters = {}) => {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([k, v]) => { if (v) params.set(k, v); });
    const q = params.toString();
    return request(`/reports/approvals/export/${format}${q ? `?${q}` : ''}`);
  },
  teams: async (filters = {}) => {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([k, v]) => { if (v) params.set(k, v); });
    const q = params.toString();
    return request(`/reports/teams${q ? `?${q}` : ''}`);
  },
  exportTeams: async (format, filters = {}) => {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([k, v]) => { if (v) params.set(k, v); });
    const q = params.toString();
    return request(`/reports/teams/export/${format}${q ? `?${q}` : ''}`);
  },
  audit: async (filters = {}) => {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([k, v]) => { if (v) params.set(k, v); });
    const q = params.toString();
    return request(`/reports/audit${q ? `?${q}` : ''}`);
  },
  exportAudit: async (format, filters = {}) => {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([k, v]) => { if (v) params.set(k, v); });
    const q = params.toString();
    return request(`/reports/audit/export/${format}${q ? `?${q}` : ''}`);
  },
};

// Audit & Compliance
export const auditApi = {
  getLogs: async (filters = {}) => {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([k, v]) => { if (v) params.set(k, v); });
    const q = params.toString();
    return request(`/audit-logs${q ? `?${q}` : ''}`);
  },
  getSecurityLogs: async () => request('/security-logs'),
  getAccessLogs: async () => request('/access-logs'),
  getActivities: async (filters = {}) => {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([k, v]) => { if (v) params.set(k, v); });
    const q = params.toString();
    return request(`/activities${q ? `?${q}` : ''}`);
  },
};

// Tags
export const tagsApi = {
  list: async () => request('/tags'),
  create: async (name) => request('/tags', { method: 'POST', body: { name } }),
  delete: async (id) => request(`/tags/${id}`, { method: 'DELETE' }),
};
