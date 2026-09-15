import api from "./api";

export interface AuditLog {
  id: number;
  user_id?: number | null;
  action: string;
  entity_type: string;
  entity_id?: number | null;
  description?: string | null;
  ip_address?: string | null;
  created_at: string;
  old_value?: string | null;
  new_value?: string | null;
  request_method?: string | null;
  endpoint?: string | null;
}

export interface AuditLogResponse {
  items: AuditLog[];
  page: number;
  page_size: number;
  total: number;
}

export interface AuditFilters {
  user_id?: number;
  action?: string;
  entity_type?: string;
  entity_id?: number;
  start_date?: string;
  end_date?: string;
  page?: number;
  page_size?: number;
}

export async function getAuditLogs(
  filters?: AuditFilters,
) {
  const response = await api.get("/audit-logs", {
    params: filters,
  });

  return response.data as AuditLogResponse;
}