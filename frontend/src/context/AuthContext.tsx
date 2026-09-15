import {
  createContext,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";

export interface User {
  id?: number;
  full_name?: string;
  email?: string;
  role?: string;
  employee_id?: string | null;
  department?: string | null;
  designation?: string | null;
  phone_number?: string | null;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (token: string, user?: User) => void;
  logout: () => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(
  undefined,
);

export function AuthProvider({
  children,
}: {
  children: ReactNode;
}) {
  const [token, setToken] = useState<string | null>(
    localStorage.getItem("access_token"),
  );

  const [user, setUser] = useState<User | null>(() => {
    const storedUser = localStorage.getItem("user");

    if (!storedUser) {
      return null;
    }

    try {
      return JSON.parse(storedUser) as User;
    } catch {
      return null;
    }
  });

  useEffect(() => {
    if (token) {
      localStorage.setItem("access_token", token);
    } else {
      localStorage.removeItem("access_token");
    }
  }, [token]);

  useEffect(() => {
    if (user) {
      localStorage.setItem("user", JSON.stringify(user));
    } else {
      localStorage.removeItem("user");
    }
  }, [user]);

  const login = (newToken: string, newUser?: User) => {
    setToken(newToken);

    if (newUser) {
      setUser(newUser);
    }
  };

  const logout = () => {
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        login,
        logout,
        isAuthenticated: Boolean(token),
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error(
      "useAuth must be used inside AuthProvider",
    );
  }

  return context;
}