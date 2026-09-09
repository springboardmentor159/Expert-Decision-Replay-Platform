import client from "./client";

// Manager/Administrator assigns a decision to a reviewer.
export async function assignApproval(decisionId, reviewerId, level = 1) {
  const res = await client.post(`/decisions/${decisionId}/approvals`, {
    reviewer_id: reviewerId,
    level,
  });
  return res.data;
}

// Reviewer (or Administrator) approves/rejects.
export async function actOnApproval(approvalId, decisionValue, comments) {
  // decisionValue: "Approved" | "Rejected"
  const res = await client.patch(`/approvals/${approvalId}`, {
    decision: decisionValue,
    comments,
  });
  return res.data;
}

// Current user's pending approvals (their review queue).
export async function getMyPendingApprovals() {
  const res = await client.get(`/approvals/pending`);
  return res.data;
}
