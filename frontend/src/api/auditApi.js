import apiClient from "./apiClient";

/**
 * Get audit/activity records.
 *
 * Backend:
 * GET /dashboard/activities
 *
 * Supported filters:
 * - user_id
 * - action
 * - entity_type
 * - start_date
 * - end_date
 * - page
 * - page_size
 */
export const getAuditActivities = async ({
  user_id = "",
  action = "",
  entity_type = "",
  start_date = "",
  end_date = "",
  page = 1,
  page_size = 20,
} = {}) => {
  const params = {
    page,
    page_size,
  };

  if (user_id !== "" && user_id !== null && user_id !== undefined) {
    params.user_id = user_id;
  }

  if (action?.trim()) {
    params.action = action.trim();
  }

  if (entity_type?.trim()) {
    params.entity_type = entity_type.trim();
  }

  if (start_date) {
    params.start_date = start_date;
  }

  if (end_date) {
    params.end_date = end_date;
  }

  const response = await apiClient.get(
    "/dashboard/activities",
    {
      params,
    }
  );

  return response.data;
};


/**
 * Convert backend/API errors into user-friendly messages.
 */
export const getAuditErrorMessage = (error) => {
  const status = error?.response?.status;
  const detail = error?.response?.data?.detail;

  if (status === 400) {
    return (
      detail ||
      "The audit log request is invalid."
    );
  }

  if (status === 401) {
    return (
      "Your session has expired. Please log in again."
    );
  }

  if (status === 403) {
    return (
      detail ||
      "You are not authorized to view these audit logs."
    );
  }

  if (status === 404) {
    return (
      detail ||
      "The requested audit information was not found."
    );
  }

  if (status === 422) {
    return (
      detail ||
      "One or more audit filter values are invalid."
    );
  }

  if (status >= 500) {
    return (
      "A server error occurred while loading audit logs. Please try again later."
    );
  }

  return (
    detail ||
    error?.message ||
    "Unable to load audit logs."
  );
};