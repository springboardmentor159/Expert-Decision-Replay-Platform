import React, { createContext, useContext, useState, useEffect, useCallback, useMemo } from 'react';
import apiClient from '../api/client';

export const UserRole = {
  EMPLOYEE: 'Employee',
  REVIEWER: 'Reviewer',
  MANAGER: 'Manager',
  ADMINISTRATOR: 'Administrator',
};

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [token, setToken] = useState(() => localStorage.getItem('token') || null);
  const [user, setUser] = useState(() => {
    try {
      const savedUser = localStorage.getItem('user');
      return savedUser ? JSON.parse(savedUser) : null;
    } catch {
      return null;
    }
  });
  const [isLoading, setIsLoading] = useState(() => Boolean(localStorage.getItem('token')));

  const clearSession = useCallback(() => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setToken(null);
    setUser(null);
  }, []);

  useEffect(() => {
    if (!token) {
      setIsLoading(false);
      return undefined;
    }

    let active = true;
    const storedUser = JSON.parse(localStorage.getItem('user') || 'null');
    const profilePath = storedUser?.id ? `/users/${storedUser.id}` : '/users/me';
    apiClient.get(profilePath)
      .then((response) => {
        if (active) {
          const userData = response.data;
          localStorage.setItem('user', JSON.stringify(userData));
          setUser(userData);
        }
      })
      .catch(() => {
        if (active) clearSession();
      })
      .finally(() => {
        if (active) setIsLoading(false);
      });

    return () => {
      active = false;
    };
  }, [token, clearSession]);

  // Synchronize 401 unauthorized events across windows/interceptors
  useEffect(() => {
    const handleUnauthorized = () => {
      clearSession();
    };

    window.addEventListener('auth:unauthorized', handleUnauthorized);
    return () => window.removeEventListener('auth:unauthorized', handleUnauthorized);
  }, [clearSession]);

  const login = useCallback(async (email, password) => {
    setIsLoading(true);
    try {
      const response = await apiClient.post('/login', { email, password });
      const { access_token, user: userData } = response.data;

      localStorage.setItem('token', access_token);
      localStorage.setItem('user', JSON.stringify(userData));

      setToken(access_token);
      setUser(userData);

      return { success: true, user: userData };
    } catch (error) {
      return {
        success: false,
        error: error.formattedMessage || 'Login failed. Please check your credentials.',
      };
    } finally {
      setIsLoading(false);
    }
  }, []);

  const logout = useCallback(async () => {
    setIsLoading(true);
    try {
      if (token) {
        await apiClient.post('/login/logout');
      }
    } catch {
      // Ignore errors on logout
    } finally {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      setToken(null);
      setUser(null);
      setIsLoading(false);
    }
  }, [token]);

  const hasRole = useCallback((allowedRoles) => {
    if (!user || !user.role) return false;
    if (Array.isArray(allowedRoles)) {
      return allowedRoles.includes(user.role);
    }
    return user.role === allowedRoles;
  }, [user]);

  const hasPermission = useCallback((permission) => {
    const permissions = {
      view_decisions: [UserRole.EMPLOYEE, UserRole.REVIEWER, UserRole.MANAGER, UserRole.ADMINISTRATOR],
      create_decision: [UserRole.EMPLOYEE, UserRole.REVIEWER, UserRole.MANAGER, UserRole.ADMINISTRATOR],
      review_decision: [UserRole.REVIEWER, UserRole.MANAGER, UserRole.ADMINISTRATOR],
      manager_dashboard: [UserRole.MANAGER, UserRole.ADMINISTRATOR],
      admin_dashboard: [UserRole.ADMINISTRATOR],
      security_logs: [UserRole.MANAGER, UserRole.ADMINISTRATOR],
      reports: [UserRole.EMPLOYEE, UserRole.REVIEWER, UserRole.MANAGER, UserRole.ADMINISTRATOR],
    };
    return hasRole(permissions[permission] || []);
  }, [hasRole]);

  const value = useMemo(() => ({
    token,
    user,
    isAuthenticated: !!token && !!user,
    isLoading,
    login,
    logout,
    hasRole,
    hasPermission,
    isEmployee: user?.role === UserRole.EMPLOYEE,
    isReviewer: user?.role === UserRole.REVIEWER,
    isManager: user?.role === UserRole.MANAGER,
    isAdmin: user?.role === UserRole.ADMINISTRATOR,
  }), [token, user, isLoading, login, logout, hasRole]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
