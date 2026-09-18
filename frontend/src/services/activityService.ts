import api from "./api";

export interface Activity {
  id: number;
  user_id: number;
  action: string;
  entity_type: string;
  entity_id: number;
  description: string;
  created_at: string;
}

export interface ActivityFilters {
  user_id?: number;
  action?: string;
  entity_type?: string;
  start_date?: string;
  end_date?: string;
}

export async function getActivities(
  filters: ActivityFilters = {},
): Promise<Activity[]> {
  const response = await api.get<Activity[]>("/activities", {
    params: filters,
  });

  return response.data;
}