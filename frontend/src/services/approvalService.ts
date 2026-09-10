import api from "./api";

export type ApprovalStatus =
  | "Pending"
  | "Approved"
  | "Rejected"
  | "Under Review";

export interface Approval {
  id: number;
  decision_id: number;
  reviewer_id: number;
  approval_level: number;
  status: string;
  assigned_at: string;
  completed_at: string | null;
}

export interface ApprovalCreatePayload {
  decision_id: number;
  reviewer_id: number;
  approval_level: number;
  status: string;
}

export interface ApprovalUpdatePayload {
  status?: string;
  completed_at?: string | null;
}

export interface ApprovalFilters {
  decision_id?: number;
  reviewer_id?: number;
  approval_status?: string;
}

export async function getApprovals(
  filters: ApprovalFilters = {},
): Promise<Approval[]> {
  const response = await api.get<Approval[]>("/approvals", {
    params: filters,
  });

  return response.data;
}

export async function getApproval(
  approvalId: number,
): Promise<Approval> {
  const response = await api.get<Approval>(
    `/approvals/${approvalId}`,
  );

  return response.data;
}

export async function createApproval(
  payload: ApprovalCreatePayload,
): Promise<Approval> {
  const response = await api.post<Approval>(
    "/approvals",
    payload,
  );

  return response.data;
}

export async function updateApproval(
  approvalId: number,
  payload: ApprovalUpdatePayload,
): Promise<Approval> {
  const response = await api.patch<Approval>(
    `/approvals/${approvalId}`,
    payload,
  );

  return response.data;
}