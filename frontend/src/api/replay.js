import { request } from './client';

export const replayApi = {
  getDecisionReplay: async (decisionId) => {
    return await request(`/decisions/${decisionId}/replay`);
  },
};