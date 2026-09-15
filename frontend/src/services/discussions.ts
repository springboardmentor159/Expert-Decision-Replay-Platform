import api from "./api";

export interface DiscussionThread {
  id: number;
  decision_id: number;
  title: string;
  description?: string;
  status?: string;
  created_by?: number;
  created_at?: string;
  updated_at?: string;
}

export interface Comment {
  id: number;
  decision_id?: number;
  thread_id?: number;
  user_id?: number;
  content: string;
  created_at?: string;
  updated_at?: string;
}

function normalizeList<T>(
  data: T[] | { items?: T[] },
): T[] {
  if (Array.isArray(data)) {
    return data;
  }

  if (Array.isArray(data.items)) {
    return data.items;
  }

  return [];
}

/* =========================
   DISCUSSION THREADS
========================= */

export async function getThreads(
  decisionId: number,
) {
  const response = await api.get(
    `/decisions/${decisionId}/threads`,
  );

  return normalizeList<DiscussionThread>(
    response.data,
  );
}

export async function getThread(
  threadId: number,
) {
  const response = await api.get(
    `/threads/${threadId}`,
  );

  return response.data as DiscussionThread;
}

export async function createThread(
  decisionId: number,
  data: {
    title: string;
    description: string;
  },
) {
  const response = await api.post(
    `/decisions/${decisionId}/threads`,
    data,
  );

  return response.data as DiscussionThread;
}

export async function updateThread(
  threadId: number,
  data: {
    title?: string;
    description?: string;
    status?: string;
  },
) {
  const response = await api.put(
    `/threads/${threadId}`,
    data,
  );

  return response.data as DiscussionThread;
}

export async function deleteThread(
  threadId: number,
) {
  const response = await api.delete(
    `/threads/${threadId}`,
  );

  return response.data;
}

/* =========================
   DECISION COMMENTS
========================= */

export async function getDecisionComments(
  decisionId: number,
) {
  const response = await api.get(
    `/decisions/${decisionId}/comments`,
  );

  return normalizeList<Comment>(
    response.data,
  );
}

export async function createDecisionComment(
  decisionId: number,
  content: string,
) {
  const response = await api.post(
    `/decisions/${decisionId}/comments`,
    {
      content,
    },
  );

  return response.data as Comment;
}

/* =========================
   THREAD COMMENTS
========================= */

export async function getThreadComments(
  threadId: number,
) {
  const response = await api.get(
    `/threads/${threadId}/comments`,
  );

  return normalizeList<Comment>(
    response.data,
  );
}

export async function createThreadComment(
  threadId: number,
  content: string,
) {
  const response = await api.post(
    `/threads/${threadId}/comments`,
    {
      content,
    },
  );

  return response.data as Comment;
}

/* =========================
   COMMENT MANAGEMENT
========================= */

export async function getComment(
  commentId: number,
) {
  const response = await api.get(
    `/comments/${commentId}`,
  );

  return response.data as Comment;
}

export async function updateComment(
  commentId: number,
  content: string,
) {
  const response = await api.put(
    `/comments/${commentId}`,
    {
      content,
    },
  );

  return response.data as Comment;
}

export async function deleteComment(
  commentId: number,
) {
  const response = await api.delete(
    `/comments/${commentId}`,
  );

  return response.data;
}