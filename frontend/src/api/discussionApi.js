import apiClient from "./apiClient";

// =====================================================
// DISCUSSION THREADS
// =====================================================

// Get all discussion threads for a decision
export async function getThreads(decisionId) {
  const response = await apiClient.get(
    `/decisions/${decisionId}/threads`
  );

  return response.data;
}

// Get a single discussion thread
export async function getThread(threadId) {
  const response = await apiClient.get(
    `/threads/${threadId}`
  );

  return response.data;
}

// Create a discussion thread
export async function createThread(
  decisionId,
  threadData
) {
  const response = await apiClient.post(
    `/decisions/${decisionId}/threads`,
    threadData
  );

  return response.data;
}

// Update a discussion thread
export async function updateThread(
  threadId,
  threadData
) {
  const response = await apiClient.put(
    `/threads/${threadId}`,
    threadData
  );

  return response.data;
}

// Delete a discussion thread
export async function deleteThread(
  threadId
) {
  const response = await apiClient.delete(
    `/threads/${threadId}`
  );

  return response.data;
}


// =====================================================
// DECISION COMMENTS
// =====================================================

// Get all comments for a decision
export async function getDecisionComments(
  decisionId
) {
  const response = await apiClient.get(
    `/decisions/${decisionId}/comments`
  );

  return response.data;
}

// Create a comment for a decision
export async function createDecisionComment(
  decisionId,
  commentData
) {
  const response = await apiClient.post(
    `/decisions/${decisionId}/comments`,
    commentData
  );

  return response.data;
}


// =====================================================
// SINGLE COMMENTS
// =====================================================

// Get a single comment
export async function getComment(commentId) {
  const response = await apiClient.get(
    `/comments/${commentId}`
  );

  return response.data;
}

// Update a comment
export async function updateComment(
  commentId,
  commentData
) {
  const response = await apiClient.put(
    `/comments/${commentId}`,
    commentData
  );

  return response.data;
}

// Delete a comment
export async function deleteComment(
  commentId
) {
  const response = await apiClient.delete(
    `/comments/${commentId}`
  );

  return response.data;
}


// =====================================================
// THREAD REPLIES
// =====================================================

// Get replies for a thread
export async function getThreadReplies(
  threadId
) {
  const response = await apiClient.get(
    `/threads/${threadId}/comments`
  );

  return response.data;
}

// Create a reply to a thread
export async function createThreadReply(
  threadId,
  commentData
) {
  const response = await apiClient.post(
    `/threads/${threadId}/comments`,
    commentData
  );

  return response.data;
}