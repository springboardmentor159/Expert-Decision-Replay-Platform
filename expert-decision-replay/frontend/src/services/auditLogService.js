import api from "./api";

const auditService = {
  // Get all audit logs
  getAuditLogs: async (params = {}) => {
    const response = await api.get("/activities", {
      params,
    });

    return response.data;
  },

  // Get audit logs for a specific user
  getUserAuditLogs: async (userId) => {
    const response = await api.get(
      `/activities/user/${userId}`
    );

    return response.data;
  },

  // Get audit logs for a specific decision
  getDecisionAuditLogs: async (decisionId) => {
    const response = await api.get(
      `/activities/decision/${decisionId}`
    );

    return response.data;
  },

  // Search audit logs
  searchAuditLogs: async (params = {}) => {
    const response = await api.get("/activities/search", {
      params,
    });

    return response.data;
  },
};

export default auditService;