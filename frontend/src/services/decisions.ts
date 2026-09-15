import api from "./api";

export interface Decision {
  id: number;
  title: string;
  problem_statement?: string;
  category?: string;
  rationale?: string;
  status?: string;
  created_by?: number;
  created_at?: string;
  updated_at?: string;
}

export interface DecisionListResponse {
  items: Decision[];
  total?: number;
  page?: number;
  page_size?: number;
}

export async function getDecisions(params?: {
  search?: string;
  status?: string;
  category?: string;
  page?: number;
  page_size?: number;
}) {
  const response = await api.get("/decisions", {
    params,
  });

  return response.data as DecisionListResponse | Decision[];
}

export async function getDecision(decisionId: number) {
  const response = await api.get(`/decisions/${decisionId}`);

  return response.data as Decision;
}

export async function createDecision(data: {
  title: string;
  problem_statement: string;
  category: string;
  rationale?: string;
}) {
  const response = await api.post("/decisions", data);

  return response.data as Decision;
}

export async function updateDecision(
  decisionId: number,
  data: {
    title?: string;
    problem_statement?: string;
    category?: string;
    rationale?: string;
  },
) {
  const response = await api.put(
    `/decisions/${decisionId}`,
    data,
  );

  return response.data as Decision;
}

export async function updateDecisionStatus(
  decisionId: number,
  status: string,
) {
  const response = await api.patch(
    `/decisions/${decisionId}/status`,
    {
      status,
    },
  );

  return response.data as Decision;
}

export async function deleteDecision(decisionId: number) {
  const response = await api.delete(
    `/decisions/${decisionId}`,
  );

  return response.data;
}