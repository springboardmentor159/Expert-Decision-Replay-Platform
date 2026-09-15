import api from "./api";

export interface Approval {
  id: number;
  decision_id: number;
  reviewer_id: number;
  status: string;
  approval_level: number;
  created_at?: string;
  updated_at?: string;
}

export async function getPendingApprovals() {
  const response = await api.get("/approvals/pending");

  return response.data as Approval[];
}

export async function createApproval(
  decisionId: number,
  data: {
    reviewer_id: number;
    approval_level: number;
  },
) {
  const response = await api.post(
    `/approvals/decisions/${decisionId}`,
    data,
  );

  return response.data as Approval;
}

export async function updateApproval(
  approvalId: number,
  status: "Approved" | "Rejected",
) {
  const response = await api.patch(
    `/approvals/${approvalId}`,
    {
      status,
    },
  );

  return response.data as Approval;
}