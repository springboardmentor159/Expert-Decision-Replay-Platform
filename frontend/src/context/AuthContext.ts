import { createContext } from "react";

export type UserRole =
  | "Employee"
  | "Reviewer"
  | "Manager"
  | "Administrator";

export interface User {
  id: number;
  full_name: string;
  email: string;
  role: UserRole;
  employee_id?: string | null;
  department?: string | null;
  designation?: string | null;
  phone_number?: string | null;
}

export interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
}

export const AuthContext = createContext<
  AuthContextType | undefined
>(undefined);