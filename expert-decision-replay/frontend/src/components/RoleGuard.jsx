import { Navigate, Outlet } from "react-router-dom";

const RoleGuard = ({ allowedRoles = [], children }) => {
  const userData = localStorage.getItem("user");

  let user = null;

  try {
    user = userData ? JSON.parse(userData) : null;
  } catch (error) {
    user = null;
  }

  const userRole = user?.role;

  if (!userRole) {
    return <Navigate to="/login" replace />;
  }

  if (
    allowedRoles.length > 0 &&
    !allowedRoles.includes(userRole.toLowerCase())
  ) {
    return <Navigate to="/dashboard" replace />;
  }

  if (children) {
    return children;
  }

  return <Outlet />;
};

export default RoleGuard;