import api from "./api";

export async function getEmployeeDashboard() {
  const response = await api.get("/dashboard/employee");
  return response.data;
}

export async function getManagerDashboard() {
  const response = await api.get("/dashboard/manager");
  return response.data;
}

export async function getAdminDashboard() {
  const response = await api.get("/dashboard/admin");
  return response.data;
}