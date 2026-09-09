import apiClient from "./apiClient";


// GET ALL USERS
export async function getUsers() {
  const response = await apiClient.get("/users");
  return response.data;
}


// GET SINGLE USER
export async function getUser(userId) {
  const response = await apiClient.get(
    `/users/${userId}`
  );

  return response.data;
}


// CREATE USER
export async function createUser(userData) {
  const response = await apiClient.post(
    "/users",
    userData
  );

  return response.data;
}


// UPDATE USER
export async function updateUser(
  userId,
  userData
) {
  const response = await apiClient.put(
    `/users/${userId}`,
    userData
  );

  return response.data;
}


// DELETE USER
export async function deleteUser(userId) {
  const response = await apiClient.delete(
    `/users/${userId}`
  );

  return response.data;
}