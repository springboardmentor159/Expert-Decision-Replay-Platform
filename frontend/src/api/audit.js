import client from "./client";

export async function getAuditLogs(params = {}) {
  const res = await client.get("/audit-logs", { params });
  return res.data;
}

export async function getSecurityLogs(params = {}) {
  const res = await client.get("/security-logs", { params });
  return res.data;
}

export async function getAccessLogs(params = {}) {
  const res = await client.get("/access-logs", { params });
  return res.data;
}
