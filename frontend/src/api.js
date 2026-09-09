const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'

export class ApiError extends Error {
  constructor(status, message) {
    super(message)
    this.status = status
  }
}

function token() {
  return localStorage.getItem('decision_replay_token')
}

export function clearSession() {
  localStorage.removeItem('decision_replay_token')
}

export function decodeToken(value = token()) {
  if (!value) return null
  try {
    const payload = JSON.parse(atob(value.split('.')[1].replace(/-/g, '+').replace(/_/g, '/')))
    return payload.exp * 1000 > Date.now() ? payload : null
  } catch {
    return null
  }
}

export async function request(path, options = {}) {
  const headers = new Headers(options.headers || {})
  if (!(options.body instanceof FormData)) headers.set('Content-Type', 'application/json')
  if (token()) headers.set('Authorization', `Bearer ${token()}`)
  const response = await fetch(`${API_URL}${path}`, { ...options, headers })
  if (response.status === 401) {
    clearSession()
    window.dispatchEvent(new Event('auth-expired'))
  }
  if (!response.ok) {
    let message = 'Something went wrong. Please try again.'
    try {
      const body = await response.json()
      message = Array.isArray(body.detail) ? body.detail.map((item) => item.msg).join(', ') : body.detail || message
    } catch { /* non-JSON error */ }
    throw new ApiError(response.status, message)
  }
  if (response.status === 204) return null
  return response.headers.get('content-type')?.includes('application/json') ? response.json() : response.blob()
}

export const api = {
  login: (body) => request('/auth/login', { method: 'POST', body: JSON.stringify(body) }),
  register: (body) => request('/users', { method: 'POST', body: JSON.stringify(body) }),
  profile: (id) => request(`/users/${id}`),
  users: () => request('/users'),
  dashboard: (role) => request(`/dashboard/${role}`),
  decisions: (params = {}) => request(`/decisions?${new URLSearchParams(params)}`),
  search: (params) => request(`/decisions/search?${new URLSearchParams(params)}`),
  decision: (id) => request(`/decisions/${id}`),
  createDecision: (body) => request('/decisions', { method: 'POST', body: JSON.stringify(body) }),
  updateDecision: (id, body) => request(`/decisions/${id}`, { method: 'PUT', body: JSON.stringify(body) }),
  updateStatus: (id, status) => request(`/decisions/${id}/status`, { method: 'PATCH', body: JSON.stringify({ status }) }),
  timeline: (id) => request(`/decisions/${id}/timeline`),
  versions: (id) => request(`/decisions/${id}/versions`),
  alternatives: (id) => request(`/decisions/${id}/alternatives`),
  compare: (id) => request(`/decisions/${id}/alternatives/compare`),
  createAlternative: (id, body) => request(`/decisions/${id}/alternatives`, { method: 'POST', body: JSON.stringify(body) }),
  updateAlternative: (id, body) => request(`/alternatives/${id}`, { method: 'PUT', body: JSON.stringify(body) }),
  deleteAlternative: (id) => request(`/alternatives/${id}`, { method: 'DELETE' }),
  meetingNotes: (id) => request(`/decisions/${id}/meeting-notes`),
  createMeetingNote: (id, body) => request(`/decisions/${id}/meeting-notes`, { method: 'POST', body: JSON.stringify(body) }),
  updateMeetingNote: (id, body) => request(`/meeting-notes/${id}`, { method: 'PUT', body: JSON.stringify(body) }),
  deleteMeetingNote: (id) => request(`/meeting-notes/${id}`, { method: 'DELETE' }),
  comments: (id) => request(`/decisions/${id}/comments`),
  createComment: (id, body) => request(`/decisions/${id}/comments`, { method: 'POST', body: JSON.stringify(body) }),
  threads: (id) => request(`/decisions/${id}/threads`),
  createThread: (id, body) => request(`/decisions/${id}/threads`, { method: 'POST', body: JSON.stringify(body) }),
  approvals: (params = {}) => request(`/approvals?${new URLSearchParams(params)}`),
  createApproval: (body) => request('/approvals', { method: 'POST', body: JSON.stringify(body) }),
  updateApproval: (id, decision) => request(`/approvals/${id}`, { method: 'PATCH', body: JSON.stringify({ decision }) }),
  activities: (params = {}) => request(`/activities?${new URLSearchParams(params)}`),
  audit: (params = {}) => request(`/audit-logs?${new URLSearchParams(params)}`),
  report: (type, params = {}) => request(`/reports/${type}?${new URLSearchParams(params)}`),
  exportReport: (type, format, params = {}) => request(`/reports/${type}/export/${format}?${new URLSearchParams(params)}`),
}
