import client from "./client";

export async function listUsers() {
  const res = await client.get("/users/");
  return res.data;
}

export async function getUser(userId) {
  const res = await client.get(`/users/${userId}`);
  return res.data;
}

export async function updateUser(userId, payload) {
  const res = await client.put(`/users/${userId}`, payload);
  return res.data;
}

export async function deleteUser(userId) {
  const res = await client.delete(`/users/${userId}`);
  return res.data;
}
