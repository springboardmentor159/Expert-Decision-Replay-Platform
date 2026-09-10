import api from './api';

export const discussionService = {
  // --- Discussion Threads & Replies ---
  getThreads: async (decisionId) => {
    const response = await api.get(`/decisions/${decisionId}/threads`);
    return response.data;
  },

  createThread: async (decisionId, threadData) => {
    const response = await api.post(`/decisions/${decisionId}/threads`, threadData);
    return response.data;
  },

  getThreadComments: async (threadId) => {
    const response = await api.get(`/threads/${threadId}/comments`);
    return response.data;
  },

  addThreadComment: async (threadId, commentData) => {
    const response = await api.post(`/threads/${threadId}/comments`, commentData);
    return response.data;
  },

  // --- Decision Comments ---
  getComments: async (decisionId) => {
    const response = await api.get(`/decisions/${decisionId}/comments`);
    return response.data;
  },

  addComment: async (decisionId, commentData) => {
    const response = await api.post(`/decisions/${decisionId}/comments`, commentData);
    return response.data;
  },

  // --- Meeting Notes ---
  getMeetingNotes: async (decisionId) => {
    const response = await api.get(`/decisions/${decisionId}/meeting-notes`);
    return response.data;
  },

  createMeetingNote: async (decisionId, noteData) => {
    const response = await api.post(`/decisions/${decisionId}/meeting-notes`, noteData);
    return response.data;
  },

  deleteMeetingNote: async (noteId) => {
    const response = await api.delete(`/meeting-notes/${noteId}`);
    return response.data;
  },
};
