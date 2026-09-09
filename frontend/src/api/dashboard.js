import client from "./client";

// Employee
export async function getEmployeeDashboard() {
  const res = await client.get("/dashboard/employee");
  return res.data;
}
export async function getEmployeeDecisions() {
  const res = await client.get("/dashboard/employee/decisions");
  return res.data;
}
export async function getEmployeePendingReviews() {
  const res = await client.get("/dashboard/employee/pending-reviews");
  return res.data;
}
export async function getEmployeeRecentActivities() {
  const res = await client.get("/dashboard/employee/recent-activities");
  return res.data;
}

// Manager
export async function getManagerDashboard() {
  const res = await client.get("/dashboard/manager");
  return res.data;
}
export async function getManagerTeamDecisions() {
  const res = await client.get("/dashboard/manager/team-decisions");
  return res.data;
}
export async function getManagerPendingApprovals() {
  const res = await client.get("/dashboard/manager/pending-approvals");
  return res.data;
}
export async function getManagerStatistics() {
  const res = await client.get("/dashboard/manager/statistics");
  return res.data;
}

// Admin
export async function getAdminDashboard() {
  const res = await client.get("/dashboard/admin");
  return res.data;
}
export async function getAdminAnalytics() {
  const res = await client.get("/dashboard/admin/analytics");
  return res.data;
}
export async function getAdminDecisionActivity() {
  const res = await client.get("/dashboard/admin/decision-activity");
  return res.data;
}
export async function getAdminApprovalStatistics() {
  const res = await client.get("/dashboard/admin/approval-statistics");
  return res.data;
}
export async function getAdminCompletionRate() {
  const res = await client.get("/dashboard/admin/completion-rate");
  return res.data;
}
export async function getAdminUserActivity() {
  const res = await client.get("/dashboard/admin/user-activity");
  return res.data;
}
