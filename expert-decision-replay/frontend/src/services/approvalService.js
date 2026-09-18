import api from "./api";

const approvalService = {
  // Get all approvals
  getAllApprovals: async () => {
    const response = await api.get("/approvals");
    return response.data;
  },

  // Get approval by ID
  getApprovalById: async (approvalId) => {
    const response = await api.get(`/approvals/${approvalId}`);
    return response.data;
  },

  // Create approval
  createApproval: async (approvalData) => {
    const response = await api.post("/approvals", approvalData);
    return response.data;
  },

  // Update approval
  updateApproval: async (approvalId, approvalData) => {
    const response = await api.put(
      `/approvals/${approvalId}`,
      approvalData
    );
    return response.data;
  },

  // Delete approval
  deleteApproval: async (approvalId) => {
    const response = await api.delete(`/approvals/${approvalId}`);
    return response.data;
  },
};

export default approvalService;