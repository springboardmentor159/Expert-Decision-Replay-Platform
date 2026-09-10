import React, { createContext, useContext, useState, useEffect } from 'react';
import { authService } from '../api/authService';
import { useToast } from './ToastContext';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(() => {
    try {
      const stored = localStorage.getItem('user');
      return stored ? JSON.parse(stored) : null;
    } catch {
      return null;
    }
  });

  const [token, setToken] = useState(() => localStorage.getItem('token') || null);
  const [loading, setLoading] = useState(true);
  const { success, error } = useToast();

  useEffect(() => {
    // Verify token validity on load if token exists
    const initAuth = async () => {
      if (token) {
        try {
          const profile = await authService.getProfile();
          setUser(profile);
          localStorage.setItem('user', JSON.stringify(profile));
        } catch (err) {
          console.warn('Session verification failed, logging out.', err);
          logout();
        }
      }
      setLoading(false);
    };

    initAuth();
  }, []);

  const login = async (email, password) => {
    try {
      const res = await authService.login(email, password);
      setToken(res.access_token);
      setUser(res.user);
      localStorage.setItem('token', res.access_token);
      localStorage.setItem('user', JSON.stringify(res.user));
      success(`Welcome back, ${res.user.full_name}! (${res.user.role})`);
      return res.user;
    } catch (err) {
      error(err.message || 'Login failed');
      throw err;
    }
  };

  const register = async (userData) => {
    try {
      const newUser = await authService.register(userData);
      success('Registration successful! Please log in with your credentials.');
      return newUser;
    } catch (err) {
      error(err.message || 'Registration failed');
      throw err;
    }
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    success('Logged out successfully.');
  };

  const value = {
    user,
    token,
    role: user?.role || null,
    isAuthenticated: !!token && !!user,
    loading,
    login,
    register,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
