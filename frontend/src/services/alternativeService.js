import axiosClient from "../api/axiosClient";

// Get all alternatives for a decision
export const getAlternatives = async (decisionId) => {
  const response = await axiosClient.get(
    `/decisions/${decisionId}/alternatives`
  );

  return response.data;
};

// Create an alternative
export const createAlternative = async (
  decisionId,
  alternativeData
) => {
  const response = await axiosClient.post(
    `/decisions/${decisionId}/alternatives`,
    alternativeData
  );

  return response.data;
};

// Get a single alternative
export const getAlternative = async (alternativeId) => {
  const response = await axiosClient.get(
    `/alternatives/${alternativeId}`
  );

  return response.data;
};

// Update an alternative
export const updateAlternative = async (
  alternativeId,
  alternativeData
) => {
  const response = await axiosClient.put(
    `/alternatives/${alternativeId}`,
    alternativeData
  );

  return response.data;
};

// Compare alternatives
export const compareAlternatives = async (decisionId) => {
  const response = await axiosClient.get(
    `/decisions/${decisionId}/alternatives/compare`
  );

  return response.data;
};