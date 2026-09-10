import api from "./api";

export interface Comment {
  id: number;
  decision_id: number;
  user_id: number;
  content: string;
  created_at: string;
  updated_at: string;
}

export interface CommentPayload {
  content: string;
}

export async function getComments(
  decisionId: number,
): Promise<Comment[]> {
  const response = await api.get<Comment[]>(
    `/decisions/${decisionId}/comments`,
  );

  return response.data;
}

export async function createComment(
  decisionId: number,
  payload: CommentPayload,
): Promise<Comment> {
  const response = await api.post<Comment>(
    `/decisions/${decisionId}/comments`,
    payload,
  );

  return response.data;
}

export async function updateComment(
  commentId: number,
  payload: CommentPayload,
): Promise<Comment> {
  const response = await api.put<Comment>(
    `/decisions/${commentId}`,
    payload,
  );

  return response.data;
}

export async function deleteComment(
  commentId: number,
): Promise<{ message: string }> {
  const response = await api.delete<{ message: string }>(
    `/decisions/${commentId}`,
  );

  return response.data;
}