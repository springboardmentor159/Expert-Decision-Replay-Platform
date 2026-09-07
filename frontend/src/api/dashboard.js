import { request } from './client';

export const dashboardApi = {
  getEmployeeDashboard: async () => {
    return await request('/dashboard/employee');
  },

  getEmployeeDecisions: async (page = 1, pageSize = 10) => {
    return await request(`/dashboard/employee/decisions?page=${page}&page_size=${pageSize}`);
  },

  getEmployeePendingReviews: async () => {
    return await request('/dashboard/employee/pending-reviews');
  },

  getEmployeeRecentActivities: async () => {
    return await request('/dashboard/employee/recent-activities');
  },

  getManagerDashboard: async () => {
    return await request('/dashboard/manager');
  },

  getManagerTeamDecisions: async (page = 1, pageSize = 10) => {
    return await request(`/dashboard/manager/team-decisions?page=${page}&page_size=${pageSize}`);
  },

  getManagerPendingApprovals: async (page = 1, pageSize = 10) => {
    return await request(`/dashboard/manager/pending-approvals?page=${page}&page_size=${pageSize}`);
  },

  getManagerStatistics: async () => {
    return await request('/dashboard/manager/statistics');
  },

  getAdminDashboard: async () => {
    return await request('/dashboard/admin');
  },

  getAdminUsers: async (page = 1, pageSize = 10) => {
    return await request(`/dashboard/admin/users?page=${page}&page_size=${pageSize}`);
  },

  getAdminAnalytics: async () => {
    return await request('/dashboard/admin/analytics');
  },

  getAdminUserActivity: async () => {
    return await request('/dashboard/admin/user-activity');
  },

  getAdminCategoryAnalytics: async () => {
    return await request('/dashboard/admin/analytics/categories');
  },

  getAdminStatusAnalytics: async () => {
    return await request('/dashboard/admin/analytics/status');
  },

  getAdminUserAnalytics: async () => {
    return await request('/dashboard/admin/analytics/users');
  },

  getAnalytics: async () => {
    return await request('/dashboard/analytics');
  },
};
