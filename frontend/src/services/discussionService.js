import axiosClient from "../api/axiosClient";

// =========================================================
// COMMENTS
// =========================================================

// Get comments for a decision
export const getDecisionComments = async (decisionId) => {
  const response = await axiosClient.get(
    `/decisions/${decisionId}/comments`
  );

  return response.data;
};

// Create comment for a decision
export const createDecisionComment = async (
  decisionId,
  content
) => {
  const response = await axiosClient.post(
    `/decisions/${decisionId}/comments`,
    { content }
  );

  return response.data;
};

// Update comment
export const updateComment = async (
  commentId,
  content
) => {
  const response = await axiosClient.put(
    `/comments/${commentId}`,
    { content }
  );

  return response.data;
};

// Delete comment
export const deleteComment = async (commentId) => {
  const response = await axiosClient.delete(
    `/comments/${commentId}`
  );

  return response.data;
};


// =========================================================
// THREADS
// =========================================================

// Get threads for a decision
export const getDecisionThreads = async (decisionId) => {
  const response = await axiosClient.get(
    `/decisions/${decisionId}/threads`
  );

  return response.data;
};

// Create thread
export const createThread = async (
  decisionId,
  threadData
) => {
  const response = await axiosClient.post(
    `/decisions/${decisionId}/threads`,
    threadData
  );

  return response.data;
};

// Get single thread
export const getThread = async (threadId) => {
  const response = await axiosClient.get(
    `/threads/${threadId}`
  );

  return response.data;
};

// Update thread
export const updateThread = async (
  threadId,
  threadData
) => {
  const response = await axiosClient.put(
    `/threads/${threadId}`,
    threadData
  );

  return response.data;
};

// Delete thread
export const deleteThread = async (threadId) => {
  const response = await axiosClient.delete(
    `/threads/${threadId}`
  );

  return response.data;
};

// Create thread reply
export const createThreadReply = async (
  threadId,
  content
) => {
  const response = await axiosClient.post(
    `/threads/${threadId}/comments`,
    { content }
  );

  return response.data;
};


// =========================================================
// MEETING NOTES
// =========================================================

// Get meeting notes
export const getMeetingNotes = async (decisionId) => {
  const response = await axiosClient.get(
    `/decisions/${decisionId}/meeting-notes`
  );

  return response.data;
};

// Create meeting note
export const createMeetingNote = async (
  decisionId,
  noteData
) => {
  const response = await axiosClient.post(
    `/decisions/${decisionId}/meeting-notes`,
    noteData
  );

  return response.data;
};

// Get meeting note
export const getMeetingNote = async (noteId) => {
  const response = await axiosClient.get(
    `/meeting-notes/${noteId}`
  );

  return response.data;
};

// Update meeting note
export const updateMeetingNote = async (
  noteId,
  noteData
) => {
  const response = await axiosClient.put(
    `/meeting-notes/${noteId}`,
    noteData
  );

  return response.data;
};

// Delete meeting note
export const deleteMeetingNote = async (noteId) => {
  const response = await axiosClient.delete(
    `/meeting-notes/${noteId}`
  );

  return response.data;
};


// =========================================================
// RATIONALE
// =========================================================

// Get decision rationale
export const getDecisionRationale = async (
  decisionId
) => {
  const response = await axiosClient.get(
    `/decisions/${decisionId}`
  );

  return response.data;
};

// Update decision rationale
export const updateDecisionRationale = async (
  decisionId,
  rationale
) => {
  const response = await axiosClient.put(
    `/decisions/${decisionId}/rationale`,
    { rationale }
  );

  return response.data;
};