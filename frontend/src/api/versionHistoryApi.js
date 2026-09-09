import apiClient from "./apiClient";

/*
 * Get all versions of a decision.
 *
 * Backend:
 * GET /decisions/{decision_id}/versions
 */
export const getDecisionVersions = async (decisionId) => {
  const response = await apiClient.get(
    `/decisions/${decisionId}/versions`
  );

  return response.data;
};


/*
 * Get a specific version of a decision.
 *
 * Backend:
 * GET /decisions/{decision_id}/versions/{version_number}
 */
export const getDecisionVersion = async (
  decisionId,
  versionNumber
) => {
  const response = await apiClient.get(
    `/decisions/${decisionId}/versions/${versionNumber}`
  );

  return response.data;
};


/*
 * Get decision history.
 *
 * Backend:
 * GET /decisions/{decision_id}/history
 */
export const getDecisionHistory = async (decisionId) => {
  const response = await apiClient.get(
    `/decisions/${decisionId}/history`
  );

  return response.data;
};


/*
 * Get decision timeline.
 *
 * Backend:
 * GET /decisions/{decision_id}/timeline
 */
export const getDecisionTimeline = async (decisionId) => {
  const response = await apiClient.get(
    `/decisions/${decisionId}/timeline`
  );

  return response.data;
};


/*
 * Convert backend errors into user-friendly messages.
 */
export const getVersionHistoryErrorMessage = (error) => {
  const status = error?.response?.status;
  const detail = error?.response?.data?.detail;

  if (status === 400) {
    return (
      detail ||
      "The requested version or history information is invalid."
    );
  }

  if (status === 401) {
    return "Your session has expired. Please log in again.";
  }

  if (status === 403) {
    return (
      detail ||
      "You do not have permission to view this decision history."
    );
  }

  if (status === 404) {
    return (
      detail ||
      "The decision or requested history was not found."
    );
  }

  if (status === 422) {
    return (
      detail ||
      "The decision history request contains invalid information."
    );
  }

  if (status >= 500) {
    return (
      "A server error occurred while loading the decision history. Please try again later."
    );
  }

  if (error?.message) {
    return error.message;
  }

  return (
    "Unable to load the decision version history."
  );
};
