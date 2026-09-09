export const ROLES = {
  EMPLOYEE: "Employee",
  REVIEWER: "Reviewer",
  MANAGER: "Manager",
  ADMINISTRATOR: "Administrator",
};

export const ROLE_DASHBOARDS = {
  Employee: "/dashboard",
  Reviewer: "/dashboard",
  Manager: "/dashboard",
  Administrator: "/dashboard",
};

export function hasRole(user, allowedRoles = []) {
  if (!user || !user.role) {
    return false;
  }

  return allowedRoles.includes(user.role);
}