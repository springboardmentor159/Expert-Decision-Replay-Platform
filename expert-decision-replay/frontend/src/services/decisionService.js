import api from "./api";

// Create a new decision
const createDecision = async (decisionData) => {
  const response = await api.post("/decisions", decisionData);
  return response.data;
};

// Get all decisions
// Supports search, status, category, tag, pagination and sorting
const getDecisions = async (params = {}) => {
  const response = await api.get("/decisions", {
    params,
  });

  return response.data;
};

// Get one decision by ID
const getDecisionById = async (decisionId) => {
  const response = await api.get(`/decisions/${decisionId}`);
  return response.data;
};

// Update decision details
const updateDecision = async (decisionId, decisionData) => {
  const response = await api.put(
    `/decisions/${decisionId}`,
    decisionData
  );

  return response.data;
};

// Update decision status
const updateDecisionStatus = async (decisionId, status) => {
  const response = await api.put(
    `/decisions/${decisionId}/status`,
    {
      status,
    }
  );

  return response.data;
};

// Update decision rationale
const updateDecisionRationale = async (decisionId, rationale) => {
  const response = await api.put(
    `/decisions/${decisionId}/rationale`,
    {
      rationale,
    }
  );

  return response.data;
};

// Get decision rationale
const getDecisionRationale = async (decisionId) => {
  const response = await api.get(
    `/decisions/${decisionId}/rationale`
  );

  return response.data;
};

// Search decisions
const searchDecisions = async (params = {}) => {
  const response = await api.get("/decisions/search", {
    params,
  });

  return response.data;
};

// Compare alternatives of a decision
const compareAlternatives = async (decisionId) => {
  const response = await api.get(
    `/decisions/${decisionId}/alternatives/compare`
  );

  return response.data;
};

// Assign tags to a decision
const assignTagsToDecision = async (decisionId, tagIds) => {
  const response = await api.post(
    `/decisions/${decisionId}/tags`,
    {
      tag_ids: tagIds,
    }
  );

  return response.data;
};

// Get tags of a decision
const getDecisionTags = async (decisionId) => {
  const response = await api.get(
    `/decisions/${decisionId}/tags`
  );

  return response.data;
};

// Remove tag from a decision
const removeTagFromDecision = async (decisionId, tagId) => {
  const response = await api.delete(
    `/decisions/${decisionId}/tags/${tagId}`
  );

  return response.data;
};

// Get decision timeline
const getDecisionTimeline = async (decisionId) => {
  const response = await api.get(
    `/decisions/${decisionId}/timeline`
  );

  return response.data;
};

// Get all versions of a decision
const getDecisionVersions = async (decisionId) => {
  const response = await api.get(
    `/decisions/${decisionId}/versions`
  );

  return response.data;
};

// Get a specific decision version
const getSpecificDecisionVersion = async (
  decisionId,
  versionNumber
) => {
  const response = await api.get(
    `/decisions/${decisionId}/versions/${versionNumber}`
  );

  return response.data;
};

// Get decision change history
const getDecisionHistory = async (decisionId) => {
  const response = await api.get(
    `/decisions/${decisionId}/history`
  );

  return response.data;
};

// Delete decision
// Backend lo admin-only permission undi
const deleteDecision = async (decisionId) => {
  const response = await api.delete(
    `/decisions/${decisionId}`
  );

  return response.data;
};

const decisionService = {
  createDecision,
  getDecisions,
  getDecisionById,
  updateDecision,
  updateDecisionStatus,
  updateDecisionRationale,
  getDecisionRationale,
  searchDecisions,
  compareAlternatives,
  assignTagsToDecision,
  getDecisionTags,
  removeTagFromDecision,
  getDecisionTimeline,
  getDecisionVersions,
  getSpecificDecisionVersion,
  getDecisionHistory,
  deleteDecision,
};

export default decisionService;