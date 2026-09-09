import { createContext, useContext, useEffect, useState } from "react";
import { jwtDecode } from "jwt-decode";
import apiClient from "../api/apiClient";

export const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    const storedUser = localStorage.getItem("user");

    if (!token) {
      setLoading(false);
      return;
    }

    try {
      const decodedToken = jwtDecode(token);

      if (decodedToken.exp) {
        const currentTime = Date.now() / 1000;

        if (decodedToken.exp < currentTime) {
          localStorage.removeItem("access_token");
          localStorage.removeItem("user");
          setUser(null);
          setLoading(false);
          return;
        }
      }

      if (storedUser) {
        try {
          setUser(JSON.parse(storedUser));
        } catch {
          setUser({
            id: decodedToken.sub,
            email: decodedToken.email,
            role: decodedToken.role,
          });
        }
      } else {
        setUser({
          id: decodedToken.sub,
          email: decodedToken.email,
          role: decodedToken.role,
        });
      }
    } catch (error) {
      console.error("Unable to restore authentication session:", error);

      localStorage.removeItem("access_token");
      localStorage.removeItem("user");

      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  const login = async (email, password) => {
    const formData = new URLSearchParams();

    formData.append("username", email);
    formData.append("password", password);

    const response = await apiClient.post(
      "/login",
      formData,
      {
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
      }
    );

    const token = response.data.access_token;

    localStorage.setItem("access_token", token);

    let decodedToken = {};

    try {
      decodedToken = jwtDecode(token);
    } catch (error) {
      console.error("Unable to decode access token:", error);
    }

    const loggedInUser = {
      id:
        response.data.user?.id ??
        decodedToken.sub ??
        null,

      email:
        response.data.user?.email ??
        decodedToken.email ??
        email,

      name:
        response.data.user?.name ??
        response.data.user?.full_name ??
        decodedToken.name ??
        decodedToken.full_name ??
        "",

      role:
        response.data.user?.role ??
        decodedToken.role ??
        "",
    };

    localStorage.setItem(
      "user",
      JSON.stringify(loggedInUser)
    );

    setUser(loggedInUser);

    return response.data;
  };

  const logout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("user");

    setUser(null);
  };

  const value = {
    user,
    setUser,
    loading,
    login,
    logout,
    isAuthenticated: Boolean(user),
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error(
      "useAuth must be used inside an AuthProvider"
    );
  }

  return context;
};