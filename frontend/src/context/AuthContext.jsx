import { createContext, useContext, useEffect, useState } from "react";
import {
  loginUser,
  registerUser,
  getUsers,
} from "../services/authService";

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [token, setToken] = useState(
    localStorage.getItem("access_token")
  );

  const [user, setUser] = useState(() => {
    const storedUser = localStorage.getItem("user");

    try {
      return storedUser ? JSON.parse(storedUser) : null;
    } catch {
      return null;
    }
  });

  const [loading, setLoading] = useState(true);

  // Restore authentication when the application starts
  useEffect(() => {
    const restoreUser = async () => {
      const storedToken = localStorage.getItem("access_token");

      if (!storedToken) {
        setLoading(false);
        return;
      }

      try {
        const users = await getUsers();

        const storedUser = localStorage.getItem("user");

        if (storedUser) {
          const parsedUser = JSON.parse(storedUser);

          const currentUser = users.find(
            (item) => item.email === parsedUser.email
          );

          if (currentUser) {
            setUser(currentUser);
            localStorage.setItem(
              "user",
              JSON.stringify(currentUser)
            );
          } else {
            logout();
          }
        }
      } catch (error) {
        console.error("Failed to restore authentication:", error);

        localStorage.removeItem("access_token");
        localStorage.removeItem("user");

        setToken(null);
        setUser(null);
      } finally {
        setLoading(false);
      }
    };

    restoreUser();
  }, []);

  // Login
  const login = async (email, password) => {
    const loginResponse = await loginUser(email, password);

    const accessToken = loginResponse.access_token;

    localStorage.setItem("access_token", accessToken);
    setToken(accessToken);

    // Backend login returns only the JWT.
    // Therefore, get the user information separately.
    const users = await getUsers();

    const currentUser = users.find(
      (item) => item.email.toLowerCase() === email.toLowerCase()
    );

    if (!currentUser) {
      localStorage.removeItem("access_token");
      setToken(null);

      throw new Error("User information could not be loaded.");
    }

    localStorage.setItem("user", JSON.stringify(currentUser));
    setUser(currentUser);

    return currentUser;
  };

  // Register
  const register = async (userData) => {
    return await registerUser(userData);
  };

  // Logout
  const logout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("user");

    setToken(null);
    setUser(null);
  };

  const isAuthenticated = Boolean(token && user);

  const role = user?.role || null;

  return (
    <AuthContext.Provider
      value={{
        token,
        user,
        role,
        loading,
        isAuthenticated,
        login,
        register,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

// Custom hook
export const useAuth = () => {
  return useContext(AuthContext);
};