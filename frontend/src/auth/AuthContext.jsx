import { createContext, useContext, useEffect, useState } from "react";
import { jwtDecode } from "jwt-decode";
import apiClient from "../api/apiClient";

const AuthContext = createContext(null);

function getUserFromToken(token) {
  if (!token) {
    return null;
  }

  try {
    const decoded = jwtDecode(token);

    return {
      id: decoded.sub,
      email: decoded.email,
      role: decoded.role,
    };
  } catch {
    return null;
  }
}

function getStoredUser() {
  const savedUser = localStorage.getItem("user");

  if (!savedUser) {
    return null;
  }

  try {
    return JSON.parse(savedUser);
  } catch {
    localStorage.removeItem("user");
    return null;
  }
}

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() =>
    localStorage.getItem("access_token")
  );

  const [user, setUser] = useState(() => {
    const storedUser = getStoredUser();

    if (storedUser) {
      return storedUser;
    }

    const storedToken = localStorage.getItem("access_token");
    return getUserFromToken(storedToken);
  });

  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const storedToken = localStorage.getItem("access_token");

    if (storedToken) {
      const storedUser = getStoredUser();

      if (storedUser) {
        setUser(storedUser);
      } else {
        const decodedUser = getUserFromToken(storedToken);

        if (decodedUser) {
          setUser(decodedUser);
          localStorage.setItem(
            "user",
            JSON.stringify(decodedUser)
          );
        } else {
          localStorage.removeItem("access_token");
          localStorage.removeItem("user");
          setToken(null);
          setUser(null);
        }
      }
    }

    setLoading(false);
  }, []);

  const login = async (email, password) => {
    const formData = new URLSearchParams();

    formData.append("username", email);
    formData.append("password", password);

    const response = await apiClient.post("/login", formData, {
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
    });

    const accessToken = response.data.access_token;

    const decodedUser = getUserFromToken(accessToken);

    if (!decodedUser) {
      throw new Error("Invalid authentication token received.");
    }

    localStorage.setItem("access_token", accessToken);
    localStorage.setItem(
      "user",
      JSON.stringify(decodedUser)
    );

    setToken(accessToken);
    setUser(decodedUser);

    return response.data;
  };

  const logout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("user");

    setToken(null);
    setUser(null);
  };

  const value = {
    token,
    user,
    setUser,
    login,
    logout,
    isAuthenticated: Boolean(token && user),
    loading,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}