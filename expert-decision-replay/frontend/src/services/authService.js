import api from "./api";

// Login user
const login = async (username, password) => {
  const formData = new URLSearchParams();

  formData.append("username", username);
  formData.append("password", password);

  const response = await api.post("/login", formData, {
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
  });

  const token = response.data.access_token;

  if (token) {
    localStorage.setItem("access_token", token);
  }

  return response.data;
};

// Logout user
const logout = () => {
  localStorage.removeItem("access_token");
  localStorage.removeItem("user");
};

// Get current logged-in user
const getCurrentUser = async () => {
  const response = await api.get("/users/me");

  localStorage.setItem("user", JSON.stringify(response.data));

  return response.data;
};

// Get saved user from localStorage
const getSavedUser = () => {
  const user = localStorage.getItem("user");

  return user ? JSON.parse(user) : null;
};

// Check whether user is logged in
const isAuthenticated = () => {
  return Boolean(localStorage.getItem("access_token"));
};

const authService = {
  login,
  logout,
  getCurrentUser,
  getSavedUser,
  isAuthenticated,
};

export default authService;