import client from "./client";

export async function listActivities({ page = 1, page_size = 20 } = {}) {
  const res = await client.get("/activities", { params: { page, page_size } });
  return res.data; // PaginatedActivities
}
