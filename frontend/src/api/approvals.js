import { request } from './client';

export const approvalsApi = {
  create: async (decisionId, reviewerId) => {
    return await request('/approvals', {
      method: 'POST',
      body: {
        decision_id: decisionId,
        reviewer_id: reviewerId,
      },
    });
  },

  getByDecisionId: async (decisionId) => {
    return await request(`/approvals/decision/${decisionId}`);
  },

  getMyApprovals: async () => {
    return await request('/approvals/my');
  },

  getById: async (id) => {
    return await request(`/approvals/${id}`);
  },

  updateStatus: async (approvalId, status) => {
    return await request(`/approvals/${approvalId}/status`, {
      method: 'PATCH',
      body: { status },
    });
  },
};
