import axiosClient from "../api/axiosClient";

// Get decisions
export const getDecisions = async (params = {}) => {
  const response = await axiosClient.get("/decisions", {
    params,
  });

  return response.data;
};

// Get single decision
export const getDecision = async (decisionId) => {
  const response = await axiosClient.get(`/decisions/${decisionId}`);

  return response.data;
};

// Create decision
export const createDecision = async (decisionData) => {
  const response = await axiosClient.post("/decisions", decisionData);

  return response.data;
};

// Update decision
export const updateDecision = async (decisionId, decisionData) => {
  const response = await axiosClient.put(
    `/decisions/${decisionId}`,
    decisionData
  );

  return response.data;
};

// Update decision status
export const updateDecisionStatus = async (decisionId, status) => {
  const response = await axiosClient.patch(
    `/decisions/${decisionId}/status`,
    { status }
  );

  return response.data;
};

// Update rationale
export const updateDecisionRationale = async (decisionId, rationale) => {
  const response = await axiosClient.put(
    `/decisions/${decisionId}/rationale`,
    { rationale }
  );

  return response.data;
};

// Get decision timeline
export const getDecisionTimeline = async (decisionId) => {
  const response = await axiosClient.get(
    `/decisions/${decisionId}/timeline`
  );

  return response.data;
};

// Get decision history
export const getDecisionHistory = async (decisionId) => {
  const response = await axiosClient.get(
    `/decisions/${decisionId}/history`
  );

  return response.data;
};

// Get decision versions
export const getDecisionVersions = async (decisionId) => {
  const response = await axiosClient.get(
    `/decisions/${decisionId}/versions`
  );

  return response.data;
};

// Get specific decision version
export const getDecisionVersion = async (decisionId, versionNumber) => {
  const response = await axiosClient.get(
    `/decisions/${decisionId}/versions/${versionNumber}`
  );

  return response.data;
};