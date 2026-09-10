import api from './api';

export const approvalService = {
  // Submit a decision for review / approval
  submitDecision: async (decisionId, submissionData) => {
    const response = await api.post(`/decisions/${decisionId}/submit`, submissionData);
    return response.data;
  },

  // List approvals with optional filters (reviewer_id, decision_id, status)
  getApprovals: async (params = {}) => {
    const response = await api.get('/approvals', { params });
    return response.data;
  },

  // Get approvals for a specific decision
  getDecisionApprovals: async (decisionId) => {
    const response = await api.get(`/decisions/${decisionId}/approvals`);
    return response.data;
  },

  // Approve or Reject an approval request
  processAction: async (approvalId, actionData) => {
    // actionData: { status: 'Approved' | 'Rejected', comments: string }
    const response = await api.post(`/approvals/${approvalId}/action`, actionData);
    return response.data;
  },
};
