import api from "./api";

export interface Decision {
  id: number;
  title: string;
  problem_statement: string;
  category: string;
  status: string;
  tags: string | null;
  created_by: number;
  created_at: string;
  updated_at: string;
}

export interface DecisionCreatePayload {
  title: string;
  problem_statement: string;
  category: string;
  tags?: string | null;
}

export interface DecisionUpdatePayload {
  title: string;
  problem_statement: string;
  category: string;
  tags?: string | null;
}

export interface DecisionStatusUpdatePayload {
  status: string;
}

export interface DecisionVersion {
  id: number;
  decision_id: number;
  version_number: number;
  title: string;
  problem_statement: string;
  category: string;
  status: string;
  changed_by: number;
  change_summary: string;
  created_at: string;
}

export interface DecisionVersionComparison {
  decision_id: number;
  version_a: number;
  version_b: number;
  differences: Record<
    string,
    {
      version_a: string;
      version_b: string;
    }
  >;
}

export interface DecisionFilters {
  status?: string;
  category?: string;
  search?: string;
}

export async function getDecisions(
  filters: DecisionFilters = {},
): Promise<Decision[]> {
  const response = await api.get<Decision[]>("/decisions", {
    params: filters,
  });

  return response.data;
}

export async function getDecision(
  decisionId: number,
): Promise<Decision> {
  const response = await api.get<Decision>(
    `/decisions/${decisionId}`,
  );

  return response.data;
}

export async function createDecision(
  payload: DecisionCreatePayload,
): Promise<Decision> {
  const response = await api.post<Decision>(
    "/decisions",
    payload,
  );

  return response.data;
}

export async function updateDecision(
  decisionId: number,
  payload: DecisionUpdatePayload,
): Promise<Decision> {
  const response = await api.put<Decision>(
    `/decisions/${decisionId}`,
    payload,
  );

  return response.data;
}

export async function updateDecisionStatus(
  decisionId: number,
  payload: DecisionStatusUpdatePayload,
): Promise<Decision> {
  const response = await api.patch<Decision>(
    `/decisions/${decisionId}/status`,
    payload,
  );

  return response.data;
}

export async function getDecisionHistory(
  decisionId: number,
): Promise<DecisionVersion[]> {
  const response = await api.get<DecisionVersion[]>(
    `/decisions/${decisionId}/history`,
  );

  return response.data;
}

export async function compareDecisionVersions(
  decisionId: number,
  versionA: number,
  versionB: number,
): Promise<DecisionVersionComparison> {
  const response =
    await api.get<DecisionVersionComparison>(
      `/decisions/${decisionId}/versions/compare`,
      {
        params: {
          version_a: versionA,
          version_b: versionB,
        },
      },
    );

  return response.data;
}

export async function getDecisionVersion(
  decisionId: number,
  versionNumber: number,
): Promise<DecisionVersion> {
  const response = await api.get<DecisionVersion>(
    `/decisions/${decisionId}/versions/${versionNumber}`,
  );

  return response.data;
}