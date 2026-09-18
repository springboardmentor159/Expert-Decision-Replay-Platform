// Save logged-in user details
export const saveUser = (user) => {
  localStorage.setItem("user", JSON.stringify(user));
};

// Get logged-in user details
export const getUser = () => {
  const user = localStorage.getItem("user");

  return user ? JSON.parse(user) : null;
};

// Remove user details during logout
export const removeUser = () => {
  localStorage.removeItem("user");
};

// Save JWT token
export const saveToken = (token) => {
  localStorage.setItem("token", token);
};

// Get JWT token
export const getToken = () => {
  return localStorage.getItem("token");
};

// Remove JWT token
export const removeToken = () => {
  localStorage.removeItem("token");
};

// Check whether user is logged in
export const isAuthenticated = () => {
  return Boolean(getToken());
};

// Clear complete login session
export const logout = () => {
  removeUser();
  removeToken();
};