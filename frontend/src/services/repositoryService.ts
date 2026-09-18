import api from "./api";

export interface RepositoryDecision {
  id: number;
  title: string;
  category: string;
  status: string;
  tags: string | null;
  created_at: string;
  updated_at: string;
}

export interface RepositoryResponse {
  items: RepositoryDecision[];
  page: number;
  page_size: number;
  total: number;
}

export interface RepositoryFilters {
  q?: string;
  category?: string;
  status?: string;
  tag?: string;
  page?: number;
  page_size?: number;
  sort?: "created_at" | "updated_at" | "title";
  order?: "asc" | "desc";
}

export async function searchRepository(
  filters: RepositoryFilters = {},
): Promise<RepositoryResponse> {
  const response = await api.get<RepositoryResponse>(
    "/decisions/search",
    {
      params: filters,
    },
  );

  return response.data;
}