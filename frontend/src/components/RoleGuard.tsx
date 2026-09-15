import type { ReactNode } from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

interface RoleGuardProps {
  allowedRoles: string[];
  children: ReactNode;
}

export default function RoleGuard({
  allowedRoles,
  children,
}: RoleGuardProps) {
  const { user, isAuthenticated } = useAuth();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  const role = user?.role;

  if (!role || !allowedRoles.includes(role)) {
    return <Navigate to="/forbidden" replace />;
  }

  return <>{children}</>;
}