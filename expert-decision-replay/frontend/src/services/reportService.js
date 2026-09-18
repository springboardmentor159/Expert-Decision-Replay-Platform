import api from "./api";

const reportService = {
  // Decision report
  getDecisionReport: async (params = {}) => {
    const response = await api.get("/reports/decisions", {
      params,
    });

    return response.data;
  },

  // Approval report
  getApprovalReport: async (params = {}) => {
    const response = await api.get("/reports/approvals", {
      params,
    });

    return response.data;
  },

  // Team report
  getTeamReport: async (params = {}) => {
    const response = await api.get("/reports/teams", {
      params,
    });

    return response.data;
  },

  // Audit report
  getAuditReport: async (params = {}) => {
    const response = await api.get("/reports/audit", {
      params,
    });

    return response.data;
  },

  // Export decision report as PDF
  exportDecisionPdf: async (params = {}) => {
    const response = await api.get(
      "/reports/decisions/export/pdf",
      {
        params,
        responseType: "blob",
      }
    );

    return response.data;
  },

  // Export decision report as Excel
  exportDecisionExcel: async (params = {}) => {
    const response = await api.get(
      "/reports/decisions/export/excel",
      {
        params,
        responseType: "blob",
      }
    );

    return response.data;
  },

  // Export approval report as PDF
  exportApprovalPdf: async (params = {}) => {
    const response = await api.get(
      "/reports/approvals/export/pdf",
      {
        params,
        responseType: "blob",
      }
    );

    return response.data;
  },

  // Export approval report as Excel
  exportApprovalExcel: async (params = {}) => {
    const response = await api.get(
      "/reports/approvals/export/excel",
      {
        params,
        responseType: "blob",
      }
    );

    return response.data;
  },
};

export default reportService;