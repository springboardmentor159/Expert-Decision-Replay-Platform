import client from './client';

export const discussionService = {
  // Threads
  async getThreads(decisionId) {
    const response = await client.get(`/decisions/${decisionId}/threads`);
    return response.data;
  },

  async createThread(decisionId, data) {
    const response = await client.post(`/decisions/${decisionId}/threads`, data);
    return response.data;
  },

  async getThreadComments(threadId) {
    const response = await client.get(`/threads/${threadId}/comments`);
    return response.data;
  },

  async addThreadComment(threadId, content) {
    const response = await client.post(`/threads/${threadId}/comments`, { content });
    return response.data;
  },

  // Direct Decision Comments
  async getComments(decisionId) {
    const response = await client.get(`/decisions/${decisionId}/comments`);
    return response.data;
  },

  async addComment(decisionId, content) {
    const response = await client.post(`/decisions/${decisionId}/comments`, { content });
    return response.data;
  },

  // Meeting Notes
  async getMeetingNotes(decisionId) {
    const response = await client.get(`/decisions/${decisionId}/meeting-notes`);
    return response.data;
  },

  async createMeetingNote(decisionId, data) {
    const response = await client.post(`/decisions/${decisionId}/meeting-notes`, data);
    return response.data;
  },
};
