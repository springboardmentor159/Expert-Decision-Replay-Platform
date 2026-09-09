import client from "./client";

// ---- Discussion threads ----
export async function createThread(decisionId, payload) {
  // { title, description }
  const res = await client.post(`/decisions/${decisionId}/threads`, payload);
  return res.data;
}

export async function listThreads(decisionId) {
  const res = await client.get(`/decisions/${decisionId}/threads`);
  return res.data;
}

export async function getThread(threadId) {
  const res = await client.get(`/threads/${threadId}`);
  return res.data;
}

export async function updateThread(threadId, payload) {
  const res = await client.put(`/threads/${threadId}`, payload);
  return res.data;
}

export async function deleteThread(threadId) {
  const res = await client.delete(`/threads/${threadId}`);
  return res.data;
}

// ---- Comments ----
export async function createDecisionComment(decisionId, content) {
  const res = await client.post(`/decisions/${decisionId}/comments`, { content });
  return res.data;
}

export async function listDecisionComments(decisionId) {
  const res = await client.get(`/decisions/${decisionId}/comments`);
  return res.data;
}

export async function createThreadReply(threadId, content) {
  const res = await client.post(`/threads/${threadId}/comments`, { content });
  return res.data;
}

export async function listThreadReplies(threadId) {
  const res = await client.get(`/threads/${threadId}/comments`);
  return res.data;
}

export async function updateComment(commentId, content) {
  const res = await client.put(`/comments/${commentId}`, { content });
  return res.data;
}

export async function deleteComment(commentId) {
  const res = await client.delete(`/comments/${commentId}`);
  return res.data;
}

// ---- Meeting notes ----
export async function createMeetingNote(decisionId, payload) {
  // { title, content, meeting_date }
  const res = await client.post(`/decisions/${decisionId}/meeting-notes`, payload);
  return res.data;
}

export async function listMeetingNotes(decisionId) {
  const res = await client.get(`/decisions/${decisionId}/meeting-notes`);
  return res.data;
}

export async function updateMeetingNote(noteId, payload) {
  const res = await client.put(`/meeting-notes/${noteId}`, payload);
  return res.data;
}

export async function deleteMeetingNote(noteId) {
  const res = await client.delete(`/meeting-notes/${noteId}`);
  return res.data;
}
