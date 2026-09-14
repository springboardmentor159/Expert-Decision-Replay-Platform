import axiosClient from "../api/axiosClient";

// Login user
export const loginUser = async (email, password) => {
  const response = await axiosClient.post("/users/login", {
    email,
    password,
  });

  return response.data;
};

// Register user
export const registerUser = async (userData) => {
  const response = await axiosClient.post("/users", userData);

  return response.data;
};

// Get all users
export const getUsers = async () => {
  const response = await axiosClient.get("/users");

  return response.data;
};

// Get a specific user
export const getUser = async (userId) => {
  const response = await axiosClient.get(`/users/${userId}`);

  return response.data;
};

// Update user
export const updateUser = async (userId, userData) => {
  const response = await axiosClient.put(`/users/${userId}`, userData);

  return response.data;
};