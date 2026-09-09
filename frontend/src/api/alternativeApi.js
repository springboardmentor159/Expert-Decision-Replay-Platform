import apiClient from "./apiClient";

// =====================================================
// GET ALL ALTERNATIVES FOR A DECISION
// =====================================================

export async function getAlternatives(decisionId) {
  const response = await apiClient.get(
    `/alternatives/decision/${decisionId}`
  );

  return response.data;
}

// =====================================================
// GET SINGLE ALTERNATIVE
// =====================================================

export async function getAlternative(alternativeId) {
  const response = await apiClient.get(
    `/alternatives/${alternativeId}`
  );

  return response.data;
}

// =====================================================
// CREATE ALTERNATIVE
// =====================================================

export async function createAlternative(
  decisionId,
  alternativeData
) {
  const response = await apiClient.post(
    `/alternatives/decision/${decisionId}`,
    alternativeData
  );

  return response.data;
}

// =====================================================
// UPDATE ALTERNATIVE
// =====================================================

export async function updateAlternative(
  alternativeId,
  alternativeData
) {
  const response = await apiClient.put(
    `/alternatives/${alternativeId}`,
    alternativeData
  );

  return response.data;
}

// =====================================================
// DELETE ALTERNATIVE
// =====================================================

export async function deleteAlternative(
  alternativeId
) {
  const response = await apiClient.delete(
    `/alternatives/${alternativeId}`
  );

  return response.data;
}

// =====================================================
// COMPARE ALTERNATIVES
// =====================================================

export async function compareDecisionAlternatives(
  decisionId
) {
  const response = await apiClient.get(
    `/decisions/${decisionId}/alternatives/compare`
  );

  return response.data;
}