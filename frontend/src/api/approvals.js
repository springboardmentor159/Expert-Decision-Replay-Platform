import { request } from './client';

export const approvalsApi = {
  create: async (decisionId, reviewerId, sequenceOrder = 1, dueDate = null) => {
    return await request('/approvals', {
      method: 'POST',
      body: {
        decision_id: decisionId,
        reviewer_id: reviewerId,
        sequence_order: sequenceOrder,
        due_date: dueDate,
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

  escalate: async (approvalId, reason = null, escalatedToId = null) => {
    return await request(`/approvals/${approvalId}/escalate`, {
      method: 'POST',
      body: {
        reason,
        escalated_to_id: escalatedToId,
      },
    });
  },
};
