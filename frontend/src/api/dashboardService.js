import client from './client';

export const dashboardService = {
  // Employee Dashboard
  async getEmployeeDashboard() {
    const response = await client.get('/dashboard/employee');
    return response.data;
  },

  async getEmployeeDecisions() {
    const response = await client.get('/dashboard/employee/decisions');
    return response.data;
  },

  // Reviewer Dashboard
  async getReviewerDashboard() {
    const response = await client.get('/dashboard/reviewer');
    return response.data;
  },

  async getAssignedReviews() {
    const response = await client.get('/dashboard/reviewer/assigned');
    return response.data;
  },

  async getReviewedDecisions() {
    const response = await client.get('/dashboard/reviewer/reviewed');
    return response.data;
  },

  // Manager Dashboard
  async getManagerDashboard() {
    const response = await client.get('/dashboard/manager');
    return response.data;
  },

  async getTeamDecisions() {
    const response = await client.get('/dashboard/manager/team-decisions');
    return response.data;
  },

  async getPendingApprovals() {
    const response = await client.get('/dashboard/manager/pending-approvals');
    return response.data;
  },

  async getManagerStatistics() {
    const response = await client.get('/dashboard/manager/statistics');
    return response.data;
  },

  // Administrator Dashboard
  async getAdminDashboard() {
    const response = await client.get('/dashboard/admin');
    return response.data;
  },

  async getAdminAnalytics() {
    const response = await client.get('/dashboard/admin/analytics');
    return response.data;
  },

  async getAdminActiveUsers() {
    const response = await client.get('/dashboard/admin/active-users');
    return response.data;
  },
};
