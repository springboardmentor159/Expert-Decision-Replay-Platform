import { getUser } from "./auth";

// Get current user's role
export const getUserRole = () => {
  const user = getUser();

  return user?.role?.toLowerCase() || "";
};

// Check whether the user has one of the given roles
export const hasRole = (allowedRoles = []) => {
  const userRole = getUserRole();

  return allowedRoles.some(
    (role) => role.toLowerCase() === userRole
  );
};

// Check whether the user is an Employee
export const isEmployee = () => {
  return hasRole(["employee"]);
};

// Check whether the user is a Manager
export const isManager = () => {
  return hasRole(["manager"]);
};

// Check whether the user is an Admin
export const isAdmin = () => {
  return hasRole(["admin"]);
};

// Check whether the user is a Reviewer
export const isReviewer = () => {
  return hasRole(["reviewer"]);
};

// Check whether the user can manage users
export const canManageUsers = () => {
  return hasRole(["admin"]);
};

// Check whether the user can create decisions
export const canCreateDecision = () => {
  return hasRole(["employee", "manager", "admin"]);
};

// Check whether the user can edit decisions
export const canEditDecision = () => {
  return hasRole(["employee", "manager", "admin"]);
};

// Check whether the user can approve decisions
export const canApproveDecision = () => {
  return hasRole(["reviewer", "manager", "admin"]);
};

// Check whether the user can view audit logs
export const canViewAuditLogs = () => {
  return hasRole(["admin", "manager", "reviewer"]);
};

// Check whether the user can manage teams
export const canManageTeams = () => {
  return hasRole(["admin", "manager"]);
};

// Check whether the user can view reports
export const canViewReports = () => {
  return hasRole(["admin", "manager", "reviewer"]);
};