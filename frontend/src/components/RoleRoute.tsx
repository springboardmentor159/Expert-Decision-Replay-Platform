import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "../context/useAuth";
import type { UserRole } from "../context/AuthContext";

interface RoleRouteProps {
  allowedRoles: UserRole[];
}

export default function RoleRoute({
  allowedRoles,
}: RoleRouteProps) {
  const { user } = useAuth();

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  if (!allowedRoles.includes(user.role)) {
    return <Navigate to="/unauthorized" replace />;
  }

  return <Outlet />;
}