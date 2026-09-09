import apiClient from "./apiClient";

export async function getEmployeeDashboard() {
  const response = await apiClient.get("/dashboard/employee");

  return response.data;
}

export async function getEmployeeDecisions(page = 1, pageSize = 20) {
  const response = await apiClient.get(
    "/dashboard/employee/decisions",
    {
      params: {
        page,
        page_size: pageSize,
      },
    }
  );

  return response.data;
}

export async function getEmployeeRecentActivities(limit = 20) {
  const response = await apiClient.get(
    "/dashboard/employee/recent-activities",
    {
      params: {
        limit,
      },
    }
  );

  return response.data;
}

export async function getManagerDashboard() {
  const response = await apiClient.get("/dashboard/manager");

  return response.data;
}

export async function getManagerTeamDecisions(
  page = 1,
  pageSize = 20
) {
  const response = await apiClient.get(
    "/dashboard/manager/team-decisions",
    {
      params: {
        page,
        page_size: pageSize,
      },
    }
  );

  return response.data;
}

export async function getManagerStatistics() {
  const response = await apiClient.get(
    "/dashboard/manager/statistics"
  );

  return response.data;
}

export async function getManagerPendingApprovals() {
  const response = await apiClient.get(
    "/dashboard/manager/pending-approvals"
  );

  return response.data;
}

export async function getAdminDashboard() {
  const response = await apiClient.get("/dashboard/admin");

  return response.data;
}

export async function getAdminAnalytics(
  startDate = null,
  endDate = null
) {
  const params = {};

  if (startDate) {
    params.start_date = startDate;
  }

  if (endDate) {
    params.end_date = endDate;
  }

  const response = await apiClient.get(
    "/dashboard/admin/analytics",
    {
      params,
    }
  );

  return response.data;
}

export async function getAdminDecisionActivity(
  startDate = null,
  endDate = null
) {
  const params = {};

  if (startDate) {
    params.start_date = startDate;
  }

  if (endDate) {
    params.end_date = endDate;
  }

  const response = await apiClient.get(
    "/dashboard/admin/decision-activity",
    {
      params,
    }
  );

  return response.data;
}

export async function getAdminApprovalStatistics() {
  const response = await apiClient.get(
    "/dashboard/admin/approval-statistics"
  );

  return response.data;
}

export async function getAdminUserActivity(days = 30) {
  const response = await apiClient.get(
    "/dashboard/admin/user-activity",
    {
      params: {
        days,
      },
    }
  );

  return response.data;
}

export async function getActivities(filters = {}) {
  const response = await apiClient.get(
    "/dashboard/activities",
    {
      params: filters,
    }
  );

  return response.data;
}