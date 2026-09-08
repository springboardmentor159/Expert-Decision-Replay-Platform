import React from 'react';
import { useAuth } from '../../context/AuthContext';

/**
 * RoleGate conditionally renders its children based on the current user's role.
 *
 * @param {string|string[]} allowedRoles - Role or array of roles permitted to view children.
 * @param {React.ReactNode} [fallback=null] - Optional fallback component to render if unauthorized.
 * @param {React.ReactNode} children - Content rendered when authorized.
 */
export const RoleGate = ({ allowedRoles, fallback = null, children }) => {
  const { hasRole } = useAuth();

  if (!hasRole(allowedRoles)) {
    return fallback;
  }

  return <>{children}</>;
};

export default RoleGate;
