import axiosClient from "../api/axiosClient";

// =========================================================
// GET ALL APPROVALS
// =========================================================

export const getApprovals = async () => {
  const response = await axiosClient.get("/approvals");

  return response.data;
};

// =========================================================
// CREATE / ASSIGN APPROVAL
// =========================================================

export const createApproval = async (approvalData) => {
  const response = await axiosClient.post(
    "/approvals",
    approvalData
  );

  return response.data;
};

// =========================================================
// GET PENDING APPROVALS
// =========================================================

export const getPendingApprovals = async () => {
  const response = await axiosClient.get(
    "/approvals/pending"
  );

  return response.data;
};

// =========================================================
// APPROVE APPROVAL
// =========================================================

export const approveApproval = async (approvalId) => {
  const response = await axiosClient.patch(
    `/approvals/${approvalId}/approve`
  );

  return response.data;
};

// =========================================================
// REJECT APPROVAL
// =========================================================

export const rejectApproval = async (approvalId) => {
  const response = await axiosClient.patch(
    `/approvals/${approvalId}/reject`
  );

  return response.data;
};