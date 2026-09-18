import api from "./api";

// =====================================================
// COMMENTS
// =====================================================

// Create comment for a decision
const createComment = async (decisionId, commentData) => {
  const response = await api.post(
    `/decisions/${decisionId}/comments`,
    commentData
  );

  return response.data;
};

// Get all comments of a decision
const getComments = async (decisionId) => {
  const response = await api.get(
    `/decisions/${decisionId}/comments`
  );

  return response.data;
};

// Get one comment
const getCommentById = async (commentId) => {
  const response = await api.get(
    `/comments/${commentId}`
  );

  return response.data;
};

// Update comment
const updateComment = async (commentId, commentData) => {
  const response = await api.put(
    `/comments/${commentId}`,
    commentData
  );

  return response.data;
};

// Delete comment
const deleteComment = async (commentId) => {
  const response = await api.delete(
    `/comments/${commentId}`
  );

  return response.data;
};

// =====================================================
// DISCUSSION THREADS
// =====================================================

// Create discussion thread
const createThread = async (decisionId, threadData) => {
  const response = await api.post(
    `/decisions/${decisionId}/threads`,
    threadData
  );

  return response.data;
};

// Get all discussion threads of a decision
const getThreads = async (decisionId) => {
  const response = await api.get(
    `/decisions/${decisionId}/threads`
  );

  return response.data;
};

// Get one discussion thread
const getThreadById = async (threadId) => {
  const response = await api.get(
    `/threads/${threadId}`
  );

  return response.data;
};

// Update discussion thread
const updateThread = async (threadId, threadData) => {
  const response = await api.put(
    `/threads/${threadId}`,
    threadData
  );

  return response.data;
};

// Delete discussion thread
const deleteThread = async (threadId) => {
  const response = await api.delete(
    `/threads/${threadId}`
  );

  return response.data;
};

// =====================================================
// MEETING NOTES
// =====================================================

// Create meeting note
const createMeetingNote = async (decisionId, noteData) => {
  const response = await api.post(
    `/decisions/${decisionId}/meeting-notes`,
    noteData
  );

  return response.data;
};

// Get meeting notes of a decision
const getMeetingNotes = async (decisionId) => {
  const response = await api.get(
    `/decisions/${decisionId}/meeting-notes`
  );

  return response.data;
};

// Get one meeting note
const getMeetingNoteById = async (noteId) => {
  const response = await api.get(
    `/meeting-notes/${noteId}`
  );

  return response.data;
};

// Update meeting note
const updateMeetingNote = async (noteId, noteData) => {
  const response = await api.put(
    `/meeting-notes/${noteId}`,
    noteData
  );

  return response.data;
};

// Delete meeting note
const deleteMeetingNote = async (noteId) => {
  const response = await api.delete(
    `/meeting-notes/${noteId}`
  );

  return response.data;
};

// =====================================================
// EXPORT SERVICE
// =====================================================

const discussionService = {
  // Comments
  createComment,
  getComments,
  getCommentById,
  updateComment,
  deleteComment,

  // Discussion threads
  createThread,
  getThreads,
  getThreadById,
  updateThread,
  deleteThread,

  // Meeting notes
  createMeetingNote,
  getMeetingNotes,
  getMeetingNoteById,
  updateMeetingNote,
  deleteMeetingNote,
};

export default discussionService;