import {
  useEffect,
  useState,
  type ReactNode,
} from "react";
import { jwtDecode } from "jwt-decode";
import api from "../services/api";
import {
  AuthContext,
  type User,
} from "./AuthContext";

interface JwtPayload {
  sub: string;
  exp: number;
}

interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({
  children,
}: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null);

  const [token, setToken] = useState<string | null>(
    localStorage.getItem("access_token"),
  );

  const [isLoading, setIsLoading] = useState(true);

  const clearSession = () => {
    localStorage.removeItem("access_token");
    setToken(null);
    setUser(null);
  };

  const loadUserFromToken = async (
    accessToken: string,
  ) => {
    console.log("Loading user from JWT...");

    const decoded = jwtDecode<JwtPayload>(
      accessToken,
    );

    console.log("JWT decoded successfully.");
    console.log("JWT subject:", decoded.sub);

    if (!decoded.sub) {
      throw new Error(
        "Invalid authentication token",
      );
    }

    if (
      decoded.exp &&
      decoded.exp * 1000 < Date.now()
    ) {
      throw new Error(
        "Authentication token has expired",
      );
    }

    const userId = Number(decoded.sub);

    if (!Number.isInteger(userId)) {
      throw new Error(
        "Invalid user ID in authentication token",
      );
    }

    console.log("Requesting user:", userId);

    const response = await api.get<User>(
      `/users/${userId}`,
      {
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      },
    );

    console.log(
      "User loaded successfully:",
      response.data,
    );

    setUser(response.data);
    setToken(accessToken);
  };

  useEffect(() => {
    const restoreSession = async () => {
      const storedToken =
        localStorage.getItem("access_token");

      if (!storedToken) {
        setIsLoading(false);
        return;
      }

      try {
        await loadUserFromToken(storedToken);
      } catch (error) {
        console.error(
          "Unable to restore authentication session:",
          error,
        );

        clearSession();
      } finally {
        setIsLoading(false);
      }
    };

    restoreSession();
  }, []);

  const login = async (
    email: string,
    password: string,
  ) => {
    console.log("Starting login...");

    const formData = new URLSearchParams();

    formData.append("username", email);
    formData.append("password", password);

    const response = await api.post<{
      access_token: string;
      token_type: string;
    }>("/auth/login", formData, {
      headers: {
        "Content-Type":
          "application/x-www-form-urlencoded",
      },
    });

    console.log(
      "Login API response received.",
    );

    console.log(
      "Token received:",
      !!response.data.access_token,
    );

    const accessToken =
      response.data.access_token;

    if (!accessToken) {
      throw new Error(
        "Authentication token was not returned by the server.",
      );
    }

    localStorage.setItem(
      "access_token",
      accessToken,
    );

    setToken(accessToken);

    console.log(
      "Token saved. Loading user...",
    );

    await loadUserFromToken(accessToken);

    console.log(
      "Login completed successfully.",
    );
  };

  const logout = async () => {
    try {
      if (token) {
        await api.post(
          "/auth/logout",
          {},
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          },
        );
      }
    } catch (error) {
      console.error(
        "Logout request failed:",
        error,
      );
    } finally {
      clearSession();
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated:
          !!token && !!user,
        isLoading,
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}