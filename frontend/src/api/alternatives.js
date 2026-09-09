import client from "./client";

export async function createAlternative(decisionId, payload) {
  // { name, description, pros, cons, estimated_cost, feasibility_score (1-5), risk_level }
  const res = await client.post(`/decisions/${decisionId}/alternatives`, payload);
  return res.data;
}

export async function listAlternatives(decisionId) {
  const res = await client.get(`/decisions/${decisionId}/alternatives`);
  return res.data;
}

export async function getAlternative(alternativeId) {
  const res = await client.get(`/alternatives/${alternativeId}`);
  return res.data;
}

export async function updateAlternative(alternativeId, payload) {
  const res = await client.put(`/alternatives/${alternativeId}`, payload);
  return res.data;
}

export async function compareAlternatives(decisionId) {
  const res = await client.get(`/decisions/${decisionId}/alternatives/compare`);
  return res.data; // { decision_id, alternatives: [...] }
}

export const RISK_LEVELS = ["Low", "Medium", "High", "Critical"];
