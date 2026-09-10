import api from "./api";

export type RiskLevel = "Low" | "Medium" | "High" | "Critical";

export interface Alternative {
  id: number;
  decision_id: number;
  name: string;
  description: string;
  pros: string;
  cons: string;
  estimated_cost: number;
  feasibility_score: number;
  risk_level: RiskLevel;
  created_at: string;
  updated_at: string;
}

export interface AlternativePayload {
  name: string;
  description: string;
  pros: string;
  cons: string;
  estimated_cost: number;
  feasibility_score: number;
  risk_level: RiskLevel;
}

export interface AlternativeComparisonItem {
  name: string;
  estimated_cost: number;
  feasibility_score: number;
  risk_level: RiskLevel;
}

export interface AlternativeComparison {
  decision_id: number;
  alternatives: AlternativeComparisonItem[];
}

export async function getAlternatives(
  decisionId: number,
): Promise<Alternative[]> {
  const response = await api.get<Alternative[]>(
    `/decisions/${decisionId}/alternatives`,
  );

  return response.data;
}

export async function createAlternative(
  decisionId: number,
  payload: AlternativePayload,
): Promise<Alternative> {
  const response = await api.post<Alternative>(
    `/decisions/${decisionId}/alternatives`,
    payload,
  );

  return response.data;
}

export async function updateAlternative(
  alternativeId: number,
  payload: AlternativePayload,
): Promise<Alternative> {
  const response = await api.put<Alternative>(
    `/alternatives/${alternativeId}`,
    payload,
  );

  return response.data;
}

export async function compareAlternatives(
  decisionId: number,
): Promise<AlternativeComparison> {
  const response = await api.get<AlternativeComparison>(
    `/decisions/${decisionId}/alternatives/compare`,
  );

  return response.data;
}