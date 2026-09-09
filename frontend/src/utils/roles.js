export const ROLES = {
  EMPLOYEE: "Employee",
  REVIEWER: "Reviewer",
  MANAGER: "Manager",
  ADMINISTRATOR: "Administrator",
};

// Part 3: role-based navigation menus.
export const NAV_BY_ROLE = {
  [ROLES.EMPLOYEE]: [
    { to: "/dashboard", label: "Dashboard" },
    { to: "/decisions", label: "My Decisions" },
    { to: "/decisions/new", label: "Create Decision" },
    { to: "/repository", label: "Knowledge Repository" },
  ],
  [ROLES.REVIEWER]: [
    { to: "/dashboard", label: "Dashboard" },
    { to: "/approvals", label: "Assigned Reviews" },
    { to: "/decisions", label: "Decisions" },
    { to: "/repository", label: "Knowledge Repository" },
  ],
  [ROLES.MANAGER]: [
    { to: "/dashboard", label: "Dashboard" },
    { to: "/decisions", label: "Team Decisions" },
    { to: "/approvals", label: "Pending Approvals" },
    { to: "/reports", label: "Reports" },
    { to: "/repository", label: "Knowledge Repository" },
  ],
  [ROLES.ADMINISTRATOR]: [
    { to: "/dashboard", label: "Admin Dashboard" },
    { to: "/users", label: "User Management" },
    { to: "/audit", label: "Audit Logs" },
    { to: "/reports", label: "Reports" },
    { to: "/repository", label: "Knowledge Repository" },
  ],
};

export function canAssignApprovals(role) {
  return role === ROLES.MANAGER || role === ROLES.ADMINISTRATOR;
}

export function canActOnApprovals(role) {
  return role === ROLES.REVIEWER || role === ROLES.ADMINISTRATOR;
}

export function canDeleteDecision(role) {
  return role === ROLES.ADMINISTRATOR;
}

export function canViewAudit(role) {
  return role === ROLES.ADMINISTRATOR;
}

export function canViewReports(role) {
  return role === ROLES.MANAGER || role === ROLES.ADMINISTRATOR;
}

export function canManageUsers(role) {
  return role === ROLES.ADMINISTRATOR;
}
