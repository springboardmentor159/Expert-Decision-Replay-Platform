import axiosClient from "../api/axiosClient";

// =========================================================
// AUDIT LOGS
// =========================================================

export const getAuditLogs = async (params = {}) => {
  const response = await axiosClient.get("/audit-logs", {
    params,
  });

  return response.data;
};


// =========================================================
// SECURITY LOGS
// =========================================================

export const getSecurityLogs = async (params = {}) => {
  const response = await axiosClient.get("/security-logs", {
    params,
  });

  return response.data;
};


// =========================================================
// ACCESS LOGS
// =========================================================

export const getAccessLogs = async (params = {}) => {
  const response = await axiosClient.get("/access-logs", {
    params,
  });

  return response.data;
};


// =========================================================
// DECISION HISTORY
// =========================================================

export const getDecisionHistory = async (decisionId) => {
  const response = await axiosClient.get(
    `/decisions/${decisionId}/history`
  );

  return response.data;
};


// =========================================================
// DECISION VERSIONS
// =========================================================

export const getDecisionVersions = async (decisionId) => {
  const response = await axiosClient.get(
    `/decisions/${decisionId}/versions`
  );

  return response.data;
};


// =========================================================
// SPECIFIC VERSION
// =========================================================

export const getDecisionVersion = async (
  decisionId,
  versionNumber
) => {
  const response = await axiosClient.get(
    `/decisions/${decisionId}/versions/${versionNumber}`
  );

  return response.data;
};


// =========================================================
// DECISION TIMELINE
// =========================================================

export const getDecisionTimeline = async (decisionId) => {
  const response = await axiosClient.get(
    `/decisions/${decisionId}/timeline`
  );

  return response.data;
};