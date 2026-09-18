import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

import api from "../services/api";

export type UserRole =
  | "employee"
  | "reviewer"
  | "manager"
  | "administrator";

export interface AuthUser {
  id: number;
  full_name: string;
  email: string;
  role: UserRole;
  employee_id: string;
  department: string;
  designation: string;
  phone_number?: string | null;
}

interface LoginResponse {
  access_token: string;
  token_type: string;
}

interface AuthContextValue {
  user: AuthUser | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  hasRole: (...roles: UserRole[]) => boolean;
}

const AuthContext = createContext<AuthContextValue | undefined>(
  undefined,
);

const ACCESS_TOKEN_KEY = "access_token";
const CURRENT_USER_KEY = "current_user";

function normalizeRole(role: unknown): UserRole | null {
  const normalizedRole = String(role ?? "")
    .trim()
    .toLowerCase();

  if (
    normalizedRole === "employee" ||
    normalizedRole === "reviewer" ||
    normalizedRole === "manager" ||
    normalizedRole === "administrator"
  ) {
    return normalizedRole;
  }

  return null;
}

function normalizeUser(value: unknown): AuthUser | null {
  if (!value || typeof value !== "object") {
    return null;
  }

  const candidate = value as Record<string, unknown>;
  const role = normalizeRole(candidate.role);

  if (
    typeof candidate.id !== "number" ||
    typeof candidate.full_name !== "string" ||
    typeof candidate.email !== "string" ||
    !role ||
    typeof candidate.employee_id !== "string" ||
    typeof candidate.department !== "string" ||
    typeof candidate.designation !== "string"
  ) {
    return null;
  }

  return {
    id: candidate.id,
    full_name: candidate.full_name,
    email: candidate.email,
    role,
    employee_id: candidate.employee_id,
    department: candidate.department,
    designation: candidate.designation,
    phone_number:
      typeof candidate.phone_number === "string" ||
      candidate.phone_number === null
        ? candidate.phone_number
        : undefined,
  };
}

function getStoredUser(): AuthUser | null {
  const storedUser = localStorage.getItem(
    CURRENT_USER_KEY,
  );

  if (!storedUser) {
    return null;
  }

  try {
    const parsedUser = JSON.parse(storedUser);
    const normalizedUser = normalizeUser(parsedUser);

    if (!normalizedUser) {
      localStorage.removeItem(CURRENT_USER_KEY);
      return null;
    }

    localStorage.setItem(
      CURRENT_USER_KEY,
      JSON.stringify(normalizedUser),
    );

    return normalizedUser;
  } catch {
    localStorage.removeItem(CURRENT_USER_KEY);
    return null;
  }
}

function decodeJwtPayload(token: string): { sub?: string } {
  const parts = token.split(".");

  if (parts.length !== 3) {
    throw new Error("Invalid access token.");
  }

  const base64Url = parts[1];

  const base64 = base64Url
    .replace(/-/g, "+")
    .replace(/_/g, "/")
    .padEnd(
      base64Url.length +
        ((4 - (base64Url.length % 4)) % 4),
      "=",
    );

  try {
    return JSON.parse(atob(base64)) as {
      sub?: string;
    };
  } catch {
    throw new Error("Unable to decode access token.");
  }
}

export function AuthProvider({
  children,
}: {
  children: ReactNode;
}) {
  const [token, setToken] = useState<string | null>(() =>
    localStorage.getItem(ACCESS_TOKEN_KEY),
  );

  const [user, setUser] = useState<AuthUser | null>(() =>
    getStoredUser(),
  );

  const [isLoading, setIsLoading] = useState(true);

  const logout = useCallback(() => {
    localStorage.removeItem(ACCESS_TOKEN_KEY);
    localStorage.removeItem(CURRENT_USER_KEY);

    setToken(null);
    setUser(null);
  }, []);

  const login = useCallback(
    async (email: string, password: string) => {
      const normalizedEmail = email.trim();

      if (!normalizedEmail) {
        throw new Error("Email is required.");
      }

      if (!password) {
        throw new Error("Password is required.");
      }

      const formData = new URLSearchParams();

      formData.append("username", normalizedEmail);
      formData.append("password", password);

      const response = await api.post<LoginResponse>(
        "/auth/login",
        formData,
        {
          headers: {
            "Content-Type":
              "application/x-www-form-urlencoded",
          },
        },
      );

      const newToken = response.data.access_token;

      if (!newToken) {
        throw new Error(
          "Login response did not contain an access token.",
        );
      }

      localStorage.setItem(
        ACCESS_TOKEN_KEY,
        newToken,
      );

      setToken(newToken);

      try {
        const payload = decodeJwtPayload(newToken);
        const userId = Number(payload.sub);

        if (!Number.isInteger(userId) || userId <= 0) {
          throw new Error(
            "Invalid user identifier in access token.",
          );
        }

        const userResponse = await api.get<AuthUser>(
          `/users/${userId}`,
        );

        const currentUser = normalizeUser(
          userResponse.data,
        );

        if (!currentUser) {
          throw new Error(
            "The server returned an invalid user profile.",
          );
        }

        localStorage.setItem(
          CURRENT_USER_KEY,
          JSON.stringify(currentUser),
        );

        setUser(currentUser);
      } catch (error) {
        localStorage.removeItem(ACCESS_TOKEN_KEY);
        localStorage.removeItem(CURRENT_USER_KEY);

        setToken(null);
        setUser(null);

        throw error;
      }
    },
    [],
  );

  const hasRole = useCallback(
    (...roles: UserRole[]) => {
      if (!user) {
        return false;
      }

      return roles.includes(user.role);
    },
    [user],
  );

  useEffect(() => {
    const handleSessionExpired = () => {
      logout();
    };

    window.addEventListener(
      "auth:session-expired",
      handleSessionExpired,
    );

    return () => {
      window.removeEventListener(
        "auth:session-expired",
        handleSessionExpired,
      );
    };
  }, [logout]);

  useEffect(() => {
    const storedToken =
      localStorage.getItem(ACCESS_TOKEN_KEY);

    const storedUser = getStoredUser();

    if (!storedToken || !storedUser) {
      logout();
    }

    setIsLoading(false);
  }, [logout]);

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      token,
      isAuthenticated: Boolean(token && user),
      isLoading,
      login,
      logout,
      hasRole,
    }),
    [
      user,
      token,
      isLoading,
      login,
      logout,
      hasRole,
    ],
  );

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error(
      "useAuth must be used within an AuthProvider.",
    );
  }

  return context;
}