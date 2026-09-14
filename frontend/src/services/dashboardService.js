import axiosClient from "../api/axiosClient";

// ===============================
// EMPLOYEE DASHBOARD
// ===============================

export const getEmployeeDashboard = async () => {
  const response = await axiosClient.get("/dashboard/employee");
  return response.data;
};

export const getEmployeeDecisions = async () => {
  const response = await axiosClient.get(
    "/dashboard/employee/decisions"
  );
  return response.data;
};

export const getEmployeePendingReviews = async () => {
  const response = await axiosClient.get(
    "/dashboard/employee/pending-reviews"
  );
  return response.data;
};

export const getEmployeeRecentActivities = async () => {
  const response = await axiosClient.get(
    "/dashboard/employee/recent-activities"
  );
  return response.data;
};

// ===============================
// REVIEWER DASHBOARD
// ===============================

export const getReviewerDashboard = async () => {
  const response = await axiosClient.get("/dashboard/reviewer");
  return response.data;
};

export const getReviewerDecisions = async () => {
  const response = await axiosClient.get(
    "/dashboard/reviewer/decisions"
  );
  return response.data;
};

export const getReviewerPendingReviews = async () => {
  const response = await axiosClient.get(
    "/dashboard/reviewer/pending-reviews"
  );
  return response.data;
};

export const getReviewerRecentActivities = async () => {
  const response = await axiosClient.get(
    "/dashboard/reviewer/recent-activities"
  );
  return response.data;
};
// ===============================
// MANAGER DASHBOARD
// ===============================

export const getManagerDashboard = async () => {
  const response = await axiosClient.get("/dashboard/manager");
  return response.data;
};

export const getManagerTeamDecisions = async () => {
  const response = await axiosClient.get(
    "/dashboard/manager/team-decisions"
  );
  return response.data;
};

export const getManagerPendingApprovals = async () => {
  const response = await axiosClient.get(
    "/dashboard/manager/pending-approvals"
  );
  return response.data;
};

export const getManagerStatistics = async () => {
  const response = await axiosClient.get(
    "/dashboard/manager/statistics"
  );
  return response.data;
};


// ===============================
// ADMIN DASHBOARD
// ===============================

export const getAdminDashboard = async () => {
  const response = await axiosClient.get("/dashboard/admin");
  return response.data;
};

export const getAdminAnalytics = async (params = {}) => {
  const response = await axiosClient.get(
    "/dashboard/admin/analytics",
    { params }
  );
  return response.data;
};

export const getAdminDecisionActivity = async () => {
  const response = await axiosClient.get(
    "/dashboard/admin/decision-activity"
  );
  return response.data;
};

export const getAdminApprovalStatistics = async () => {
  const response = await axiosClient.get(
    "/dashboard/admin/approval-statistics"
  );
  return response.data;
};

export const getAdminUserActivity = async () => {
  const response = await axiosClient.get(
    "/dashboard/admin/user-activity"
  );
  return response.data;
};