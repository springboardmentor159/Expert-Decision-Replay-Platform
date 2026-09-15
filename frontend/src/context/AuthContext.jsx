import { createContext, useContext, useEffect, useState } from 'react';
import { authApi } from '../services/api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [initializing, setInitializing] = useState(true);

  useEffect(() => {
    const token = sessionStorage.getItem('edr_token');
    if (!token) {
      setInitializing(false);
      return;
    }
    authApi.getProfile().then(setUser).catch(() => signOut(false)).finally(() => setInitializing(false));
  }, []);

  async function signIn(email, password) {
    const result = await authApi.login(email, password);
    sessionStorage.setItem('edr_token', result.access_token);
    const profile = await authApi.getProfile();
    setUser(profile);
    return profile;
  }

  async function signUp(data) {
    return authApi.register(data);
  }

  function signOut(redirect = true) {
    sessionStorage.removeItem('edr_token');
    sessionStorage.removeItem('edr_user');
    setUser(null);
    if (redirect) window.location.href = '/login';
  }

  const role = user?.role?.toLowerCase() || '';
  return <AuthContext.Provider value={{ user, role, initializing, signIn, signUp, signOut, isAuthenticated: Boolean(user) }}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  return useContext(AuthContext);
}