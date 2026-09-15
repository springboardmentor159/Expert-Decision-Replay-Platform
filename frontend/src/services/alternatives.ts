import api from "./api";

export interface Alternative {
  id: number;
  decision_id: number;
  name: string;
  description?: string;
  estimated_cost?: number;
  feasibility_score?: number;
  risk_level?: string;
  created_at?: string;
  updated_at?: string;
}

export interface AlternativeListResponse {
  items: Alternative[];
  total?: number;
  page?: number;
  page_size?: number;
}

export async function getAlternatives(
  decisionId: number,
) {
  const response = await api.get(
    `/decisions/${decisionId}/alternatives`,
  );

  return response.data as
    | AlternativeListResponse
    | Alternative[];
}

export async function getAlternative(
  alternativeId: number,
) {
  const response = await api.get(
    `/alternatives/${alternativeId}`,
  );

  return response.data as Alternative;
}

export async function createAlternative(
  decisionId: number,
  data: {
    name: string;
    description: string;
    estimated_cost: number;
    feasibility_score: number;
    risk_level: string;
  },
) {
  const response = await api.post(
    `/decisions/${decisionId}/alternatives`,
    data,
  );

  return response.data as Alternative;
}

export async function updateAlternative(
  alternativeId: number,
  data: {
    name?: string;
    description?: string;
    estimated_cost?: number;
    feasibility_score?: number;
    risk_level?: string;
  },
) {
  const response = await api.put(
    `/alternatives/${alternativeId}`,
    data,
  );

  return response.data as Alternative;
}

export async function deleteAlternative(
  alternativeId: number,
) {
  const response = await api.delete(
    `/alternatives/${alternativeId}`,
  );

  return response.data;
}

export async function compareAlternatives(
  decisionId: number,
) {
  const response = await api.get(
    `/decisions/${decisionId}/alternatives/compare`,
  );

  return response.data;
}