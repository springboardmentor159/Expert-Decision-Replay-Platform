import api from './api';

export const dashboardService = {
  // --- Employee Dashboard ---
  getEmployeeDashboard: async () => {
    const response = await api.get('/dashboard/employee');
    return response.data;
  },

  getEmployeeDecisions: async () => {
    const response = await api.get('/dashboard/employee/decisions');
    return response.data;
  },

  getEmployeePendingReviews: async () => {
    const response = await api.get('/dashboard/employee/pending-reviews');
    return response.data;
  },

  getEmployeeActivities: async (limit = 15) => {
    const response = await api.get('/dashboard/employee/recent-activities', { params: { limit } });
    return response.data;
  },

  // --- Reviewer Dashboard ---
  getReviewerDashboard: async () => {
    const response = await api.get('/dashboard/reviewer');
    return response.data;
  },

  getReviewerPendingReviews: async () => {
    const response = await api.get('/dashboard/reviewer/pending-reviews');
    return response.data;
  },

  getReviewerRecentReviews: async () => {
    const response = await api.get('/dashboard/reviewer/recent-reviews');
    return response.data;
  },

  // --- Manager Dashboard ---
  getManagerDashboard: async () => {
    const response = await api.get('/dashboard/manager');
    return response.data;
  },

  getManagerTeamDecisions: async () => {
    const response = await api.get('/dashboard/manager/team-decisions');
    return response.data;
  },

  getManagerPendingApprovals: async () => {
    const response = await api.get('/dashboard/manager/pending-approvals');
    return response.data;
  },

  getManagerStatistics: async () => {
    const response = await api.get('/dashboard/manager/statistics');
    return response.data;
  },

  // --- Admin Dashboard & Analytics ---
  getAdminDashboard: async () => {
    const response = await api.get('/dashboard/admin');
    return response.data;
  },

  getAdminAnalytics: async (params = {}) => {
    const response = await api.get('/dashboard/admin/analytics', { params });
    return response.data;
  },

  getAdminDecisionActivity: async (params = {}) => {
    const response = await api.get('/dashboard/admin/decision-activity', { params });
    return response.data;
  },

  getAdminApprovalStatistics: async (params = {}) => {
    const response = await api.get('/dashboard/admin/approval-statistics', { params });
    return response.data;
  },

  getAdminUserActivity: async (params = {}) => {
    const response = await api.get('/dashboard/admin/user-activity', { params });
    return response.data;
  },
};
