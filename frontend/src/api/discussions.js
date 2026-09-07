import { request } from './client';

export const discussionsApi = {
  getThreads: async (decisionId) => {
    return await request(`/decisions/${decisionId}/threads`);
  },

  createThread: async (decisionId, data) => {
    return await request(`/decisions/${decisionId}/threads`, {
      method: 'POST',
      body: data,
    });
  },

  getThreadComments: async (threadId) => {
    return await request(`/threads/${threadId}/comments`);
  },

  addThreadComment: async (threadId, content) => {
    return await request(`/threads/${threadId}/comments`, {
      method: 'POST',
      body: { content },
    });
  },

  getComments: async (decisionId) => {
    return await request(`/decisions/${decisionId}/comments`);
  },

  createComment: async (decisionId, content) => {
    return await request(`/decisions/${decisionId}/comments`, {
      method: 'POST',
      body: { content },
    });
  },

  getMeetingNotes: async (decisionId) => {
    return await request(`/decisions/${decisionId}/meeting-notes`);
  },

  createMeetingNote: async (decisionId, data) => {
    return await request(`/decisions/${decisionId}/meeting-notes`, {
      method: 'POST',
      body: data,
    });
  },
};
