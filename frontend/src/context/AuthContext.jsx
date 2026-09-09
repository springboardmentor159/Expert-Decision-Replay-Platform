import { createContext, useContext, useEffect, useState, useCallback } from "react";
import { loginUser, decodeUserIdFromToken, fetchUser } from "../api/auth";
import { getToken, setToken, clearToken, registerUnauthorizedHandler } from "../api/client";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null); // full UserResponse from backend
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadUserFromToken = useCallback(async (token) => {
    const userId = decodeUserIdFromToken(token);
    if (!userId) {
      clearToken();
      setUser(null);
      return;
    }
    try {
      const profile = await fetchUser(userId);
      setUser(profile);
    } catch {
      clearToken();
      setUser(null);
    }
  }, []);

  useEffect(() => {
    const token = getToken();
    if (token) {
      loadUserFromToken(token).finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, [loadUserFromToken]);

  // If any API call ever returns 401, force the user back to a logged-out state.
  useEffect(() => {
    registerUnauthorizedHandler(() => {
      setUser(null);
    });
  }, []);

  async function login(email, password) {
    setError(null);
    const { access_token } = await loginUser(email, password);
    setToken(access_token);
    await loadUserFromToken(access_token);
  }

  function logout() {
    clearToken();
    setUser(null);
  }

  const value = {
    user,
    isAuthenticated: !!user,
    loading,
    error,
    login,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
