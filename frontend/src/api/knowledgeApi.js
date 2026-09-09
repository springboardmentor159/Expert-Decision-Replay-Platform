import apiClient from "./apiClient";

export const searchKnowledgeRepository = async ({
  q = "",
  category = "",
  decision_status = "",
  tag = "",
  page = 1,
  page_size = 10,
  sort_by = "created_at",
  order = "desc",
} = {}) => {
  const params = {
    page,
    page_size,
    sort_by,
    order,
  };

  if (q?.trim()) {
    params.q = q.trim();
  }

  if (category) {
    params.category = category;
  }

  if (decision_status) {
    params.decision_status = decision_status;
  }

  if (tag?.trim()) {
    params.tag = tag.trim();
  }

  const response = await apiClient.get(
    "/decisions/search",
    { params }
  );

  return response.data;
};

export const getKnowledgeRepositoryErrorMessage = (error) => {
  const status = error?.response?.status;
  const detail = error?.response?.data?.detail;

  if (status === 400) {
    return (
      detail ||
      "The search request is invalid."
    );
  }

  if (status === 401) {
    return "Your session has expired. Please log in again.";
  }

  if (status === 403) {
    return (
      detail ||
      "You do not have permission to access the Knowledge Repository."
    );
  }

  if (status === 404) {
    return (
      detail ||
      "The requested repository information was not found."
    );
  }

  if (status === 422) {
    return (
      detail ||
      "One or more search or filter values are invalid."
    );
  }

  if (status === 500) {
    return "A server error occurred while loading the Knowledge Repository. Please try again later.";
  }

  if (error?.message) {
    return error.message;
  }

  return "Unable to load the Knowledge Repository.";
};