import axiosClient from "../api/axiosClient";

// =========================================================
// DECISION REPORT
// =========================================================

export const getDecisionReport = async (params = {}) => {
  const response = await axiosClient.get(
    "/reports/decisions",
    {
      params,
    }
  );

  return response.data;
};


// =========================================================
// APPROVAL REPORT
// =========================================================

export const getApprovalReport = async (params = {}) => {
  const response = await axiosClient.get(
    "/reports/approvals",
    {
      params,
    }
  );

  return response.data;
};


// =========================================================
// TEAM REPORT
// =========================================================

export const getTeamReport = async (params = {}) => {
  const response = await axiosClient.get(
    "/reports/teams",
    {
      params,
    }
  );

  return response.data;
};


// =========================================================
// AUDIT REPORT
// =========================================================

export const getAuditReport = async (params = {}) => {
  const response = await axiosClient.get(
    "/reports/audit",
    {
      params,
    }
  );

  return response.data;
};


// =========================================================
// DECISION PDF EXPORT
// =========================================================

export const exportDecisionPDF = async (params = {}) => {
  const response = await axiosClient.get(
    "/reports/decisions/export/pdf",
    {
      params,
      responseType: "blob",
    }
  );

  return response.data;
};


// =========================================================
// DECISION EXCEL EXPORT
// =========================================================

export const exportDecisionExcel = async (params = {}) => {
  const response = await axiosClient.get(
    "/reports/decisions/export/excel",
    {
      params,
      responseType: "blob",
    }
  );

  return response.data;
};


// =========================================================
// APPROVAL PDF EXPORT
// =========================================================

export const exportApprovalPDF = async (params = {}) => {
  const response = await axiosClient.get(
    "/reports/approvals/export/pdf",
    {
      params,
      responseType: "blob",
    }
  );

  return response.data;
};


// =========================================================
// APPROVAL EXCEL EXPORT
// =========================================================

export const exportApprovalExcel = async (params = {}) => {
  const response = await axiosClient.get(
    "/reports/approvals/export/excel",
    {
      params,
      responseType: "blob",
    }
  );

  return response.data;
};


// =========================================================
// TEAM PDF EXPORT
// =========================================================

export const exportTeamPDF = async (params = {}) => {
  const response = await axiosClient.get(
    "/reports/teams/export/pdf",
    {
      params,
      responseType: "blob",
    }
  );

  return response.data;
};


// =========================================================
// TEAM EXCEL EXPORT
// =========================================================

export const exportTeamExcel = async (params = {}) => {
  const response = await axiosClient.get(
    "/reports/teams/export/excel",
    {
      params,
      responseType: "blob",
    }
  );

  return response.data;
};


// =========================================================
// AUDIT PDF EXPORT
// =========================================================

export const exportAuditPDF = async (params = {}) => {
  const response = await axiosClient.get(
    "/reports/audit/export/pdf",
    {
      params,
      responseType: "blob",
    }
  );

  return response.data;
};


// =========================================================
// AUDIT EXCEL EXPORT
// =========================================================

export const exportAuditExcel = async (params = {}) => {
  const response = await axiosClient.get(
    "/reports/audit/export/excel",
    {
      params,
      responseType: "blob",
    }
  );

  return response.data;
};