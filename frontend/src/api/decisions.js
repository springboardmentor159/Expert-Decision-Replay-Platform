import client from "./client";

export async function createDecision(payload) {
  // { title, problem_statement, category }
  const res = await client.post("/decisions", payload);
  return res.data;
}

export async function listDecisions({ status, category, tag, page = 1, page_size = 10, sort = "created_at", order = "desc" } = {}) {
  const res = await client.get("/decisions", {
    params: { status, category, tag, page, page_size, sort, order },
  });
  return res.data; // PaginatedDecisions
}

export async function searchDecisions({ q, status, category, tag, page = 1, page_size = 10, sort = "created_at", order = "desc" } = {}) {
  const res = await client.get("/decisions/search", {
    params: { q, status, category, tag, page, page_size, sort, order },
  });
  return res.data;
}

export async function getDecision(decisionId) {
  const res = await client.get(`/decisions/${decisionId}`);
  return res.data;
}

export async function updateDecision(decisionId, payload) {
  const res = await client.put(`/decisions/${decisionId}`, payload);
  return res.data;
}

export async function updateDecisionStatus(decisionId, statusValue) {
  const res = await client.patch(`/decisions/${decisionId}/status`, { status: statusValue });
  return res.data;
}

export async function getDecisionRationale(decisionId) {
  const res = await client.get(`/decisions/${decisionId}/rationale`);
  return res.data;
}

export async function updateDecisionRationale(decisionId, rationale) {
  const res = await client.put(`/decisions/${decisionId}/rationale`, { rationale });
  return res.data;
}

export async function assignTagsToDecision(decisionId, tagIds) {
  const res = await client.post(`/decisions/${decisionId}/tags`, { tag_ids: tagIds });
  return res.data;
}

export async function getDecisionTags(decisionId) {
  const res = await client.get(`/decisions/${decisionId}/tags`);
  return res.data;
}

export async function removeTagFromDecision(decisionId, tagId) {
  const res = await client.delete(`/decisions/${decisionId}/tags/${tagId}`);
  return res.data;
}

export async function getDecisionTimeline(decisionId) {
  const res = await client.get(`/decisions/${decisionId}/timeline`);
  return res.data;
}

export async function getDecisionVersions(decisionId) {
  const res = await client.get(`/decisions/${decisionId}/versions`);
  return res.data;
}

export async function getDecisionVersion(decisionId, versionNumber) {
  const res = await client.get(`/decisions/${decisionId}/versions/${versionNumber}`);
  return res.data;
}

export async function getDecisionHistory(decisionId) {
  const res = await client.get(`/decisions/${decisionId}/history`);
  return res.data;
}
