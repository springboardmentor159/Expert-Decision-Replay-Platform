import api from "../services/api";
import { jwtDecode } from "jwt-decode";

// Register a new user
export const registerUser = async (userData) => {
  const response = await api.post("/users", userData);
  return response.data;
};

// Login user
export const loginUser = async (email, password) => {
  const formData = new URLSearchParams();

  formData.append("username", email);
  formData.append("password", password);

  const response = await api.post("/auth/login", formData, {
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
  });

  return response.data;
};

// Save authentication data
export const saveAuthData = (data) => {
  const token = data.access_token || data.token;

  if (!token) {
    throw new Error("Authentication token was not received.");
  }

  localStorage.setItem("token", token);

  // Decode JWT to get user ID, email and role
  const decodedToken = jwtDecode(token);

  const userFromToken = {
    id: decodedToken.sub,
    email: decodedToken.email,
    role: decodedToken.role,
  };

  localStorage.setItem("user", JSON.stringify(userFromToken));

  return userFromToken;
};

// Get stored token
export const getToken = () => {
  return localStorage.getItem("token");
};

// Get stored user
export const getStoredUser = () => {
  const user = localStorage.getItem("user");

  return user ? JSON.parse(user) : null;
};

// Logout
export const logoutUser = () => {
  localStorage.removeItem("token");
  localStorage.removeItem("user");
};

// Check whether user is logged in
export const isAuthenticated = () => {
  return Boolean(localStorage.getItem("token"));
};