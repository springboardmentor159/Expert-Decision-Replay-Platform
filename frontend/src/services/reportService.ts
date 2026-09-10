import api from "./api";

export type ReportType = "decisions" | "approvals" | "teams" | "audit";

export interface ReportFilters {
  category?: string;
  status?: string;
  created_by?: number;
  tags?: string;
  approval_status?: string;
  reviewer_id?: number;
  decision_id?: number;
  approval_level?: number;
  team_id?: number;
  user_id?: number;
  action?: string;
  entity_type?: string;
  entity_id?: number;
  date_from?: string;
  date_to?: string;
  page?: number;
  page_size?: number;
  sort_by?: string;
  sort_order?: "asc" | "desc";
}

export interface ReportResponse {
  [key: string]: unknown;
}

export async function getReport(
  type: ReportType,
  filters: ReportFilters = {},
): Promise<ReportResponse> {
  const response = await api.get<ReportResponse>(
    `/reports/${type}`,
    {
      params: filters,
    },
  );

  return response.data;
}

export async function downloadReport(
  type: ReportType,
  format: "pdf" | "excel",
  filters: ReportFilters = {},
): Promise<Blob> {
  const response = await api.get(
    `/reports/${type}/export/${format}`,
    {
      params: filters,
      responseType: "blob",
    },
  );

  return response.data;
}