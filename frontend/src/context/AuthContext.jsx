import React, { createContext, useContext, useState, useEffect } from 'react';
import { authApi } from '../api/auth';
import { useNotification } from './NotificationContext';

const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    try {
      const savedUser = localStorage.getItem('user');
      return savedUser ? JSON.parse(savedUser) : null;
    } catch {
      return null;
    }
  });
  const [token, setToken] = useState(() => localStorage.getItem('token'));
  const [loading, setLoading] = useState(true);
  const { success, error, info } = useNotification();

  // Validate session with /auth/me on load
  useEffect(() => {
    async function verifyAuth() {
      if (token) {
        try {
          const userData = await authApi.getCurrentUser();
          setUser(userData);
          localStorage.setItem('user', JSON.stringify(userData));
        } catch {
          // Token expired or invalid
          setUser(null);
          setToken(null);
          localStorage.removeItem('token');
          localStorage.removeItem('user');
        }
      }
      setLoading(false);
    }
    verifyAuth();
  }, [token]);

  // Listen for global auth expired events
  useEffect(() => {
    const handleAuthExpired = () => {
      setUser(null);
      setToken(null);
      info('Your session has expired. Please log in again.');
    };
    window.addEventListener('auth:expired', handleAuthExpired);
    return () => window.removeEventListener('auth:expired', handleAuthExpired);
  }, [info]);

  const login = async (email, password) => {
    try {
      const res = await authApi.login(email, password);
      const accessToken = res.access_token;
      localStorage.setItem('token', accessToken);
      setToken(accessToken);

      // Fetch user profile immediately
      const userData = await authApi.getCurrentUser();
      setUser(userData);
      localStorage.setItem('user', JSON.stringify(userData));
      success(`Welcome back, ${userData.full_name}!`);
      return userData;
    } catch (err) {
      error(err.message || 'Login failed. Please check your credentials.');
      throw err;
    }
  };

  const register = async (userData) => {
    try {
      const res = await authApi.register(userData);
      success('Registration successful! Please log in with your credentials.');
      return res;
    } catch (err) {
      error(err.message || 'Registration failed.');
      throw err;
    }
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    info('You have been logged out.');
  };

  const role = user?.role || null;
  const isEmployee = role === 'Employee';
  const isReviewer = role === 'Reviewer';
  const isManager = role === 'Manager';
  const isAdmin = role === 'Administrator';

  const value = {
    user,
    token,
    loading,
    role,
    isEmployee,
    isReviewer,
    isManager,
    isAdmin,
    login,
    register,
    logout,
    isAuthenticated: !!user && !!token,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
