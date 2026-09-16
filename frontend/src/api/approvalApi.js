import apiClient from "./apiClient";

/*
 * Approval API
 *
 * Backend base path:
 * /approvals
 *
 * Available backend endpoints:
 * POST   /approvals
 * GET    /approvals/{approval_id}
 * GET    /approvals/decision/{decision_id}
 * POST   /approvals/{approval_id}/approve
 * POST   /approvals/{approval_id}/reject
 */

/**
 * Assign an approval to a Reviewer / Manager / Administrator.
 *
 * Expected payload:
 * {
 *   decision_id: number,
 *   assigned_to: number,
 *   assigned_role: "Reviewer" | "Manager" | "Administrator" | "Employee"
 * }
 */
export const createApproval = async (approvalData) => {
  const response = await apiClient.post(
    "/approvals",
    approvalData
  );

  return response.data;
};

/**
 * Get a single approval by ID.
 */
export const getApproval = async (approvalId) => {
  const response = await apiClient.get(
    `/approvals/${approvalId}`
  );

  return response.data;
};

/**
 * Get all approvals associated with a decision.
 */
export const getDecisionApprovals = async (decisionId) => {
  const response = await apiClient.get(
    `/approvals/decision/${decisionId}`
  );

  return response.data;
};

/**
 * Convert the comments argument into the string
 * expected by the FastAPI ApprovalReview schema.
 *
 * Supports both:
 *
 * approveApproval(8, "Approved after review")
 *
 * and:
 *
 * approveApproval(8, {
 *   comments: "Approved after review"
 * })
 */
function normalizeComments(comments) {
  if (
    comments &&
    typeof comments === "object"
  ) {
    return comments.comments || null;
  }

  if (
    typeof comments === "string" &&
    comments.trim()
  ) {
    return comments.trim();
  }

  return null;
}

/**
 * Approve an approval request.
 *
 * Backend expects:
 * {
 *   comments: string | null
 * }
 */
export const approveApproval = async (
  approvalId,
  comments = ""
) => {
  const payload = {
    comments: normalizeComments(comments),
  };

  try {
    const response = await apiClient.post(
      `/approvals/${approvalId}/approve`,
      payload
    );

    return response.data;
  } catch (error) {
    console.error(
      "Failed to approve approval:",
      error
    );

    throw error;
  }
};

/**
 * Reject an approval request.
 *
 * Backend expects:
 * {
 *   comments: string | null
 * }
 */
export const rejectApproval = async (
  approvalId,
  comments = ""
) => {
  const payload = {
    comments: normalizeComments(comments),
  };

  try {
    const response = await apiClient.post(
      `/approvals/${approvalId}/reject`,
      payload
    );

    return response.data;
  } catch (error) {
    console.error(
      "Failed to reject approval:",
      error
    );

    throw error;
  }
};

/**
 * Convert backend errors into a user-friendly message.
 */
export const getApprovalErrorMessage = (error) => {
  const status = error?.response?.status;
  const detail = error?.response?.data?.detail;

  if (status === 400) {
    return (
      detail ||
      "This approval request cannot be processed."
    );
  }

  if (status === 401) {
    return "Your session has expired. Please log in again.";
  }

  if (status === 403) {
    return (
      detail ||
      "You do not have permission to perform this approval action."
    );
  }

  if (status === 404) {
    return (
      detail ||
      "Approval or decision not found."
    );
  }

  if (status === 422) {
    if (Array.isArray(detail)) {
      return detail
        .map((item) => item.msg)
        .join(" ");
    }

    return (
      detail ||
      "The approval information is invalid."
    );
  }

  if (status >= 500) {
    return "A server error occurred. Please try again later.";
  }

  if (error?.message) {
    return error.message;
  }

  return "Something went wrong while processing the approval.";
};