import api from "./api";

export interface DecisionVersion {
  id: number;
  decision_id: number;
  version_number: number;
  title?: string;
  problem_statement?: string;
  description?: string;
  category?: string;
  status?: string;
  created_by?: number;
  created_at?: string;
}

export interface DecisionHistoryItem {
  id?: number;
  action?: string;
  entity_type?: string;
  entity_id?: number;
  description?: string;
  user_id?: number;
  created_at?: string;
  old_value?: string | null;
  new_value?: string | null;
}

function normalizeList<T>(
  data: T[] | { items?: T[] },
): T[] {
  if (Array.isArray(data)) {
    return data;
  }

  if (Array.isArray(data.items)) {
    return data.items;
  }

  return [];
}

/**
 * Get all versions of a decision
 */
export async function getDecisionVersions(
  decisionId: number,
) {
  const response = await api.get(
    `/decisions/${decisionId}/versions`,
  );

  return normalizeList<DecisionVersion>(
    response.data,
  );
}

/**
 * Get one specific version
 */
export async function getDecisionVersion(
  decisionId: number,
  versionNumber: number,
) {
  const response = await api.get(
    `/decisions/${decisionId}/versions/${versionNumber}`,
  );

  return response.data as DecisionVersion;
}

/**
 * Get complete decision history
 */
export async function getDecisionHistory(
  decisionId: number,
) {
  const response = await api.get(
    `/decisions/${decisionId}/history`,
  );

  return normalizeList<DecisionHistoryItem>(
    response.data,
  );
}