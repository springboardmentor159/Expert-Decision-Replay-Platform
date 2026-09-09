import client from "./client";

export async function createTag(name) {
  const res = await client.post("/tags", { name });
  return res.data;
}

export async function listTags() {
  const res = await client.get("/tags");
  return res.data;
}

export async function getTag(tagId) {
  const res = await client.get(`/tags/${tagId}`);
  return res.data;
}

export async function deleteTag(tagId) {
  const res = await client.delete(`/tags/${tagId}`);
  return res.data;
}
