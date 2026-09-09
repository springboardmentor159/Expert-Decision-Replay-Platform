// Authentication and Session State Manager
import { authApi, setUnauthorizedHandler } from './api.js';

class AuthManager {
  constructor() {
    this.tokenKey = 'edr_token';
    this.userKey = 'edr_user';
    this.currentUser = null;
    this.listeners = [];

    // Attach 401 callback from API
    setUnauthorizedHandler(() => {
      this.logout(true);
    });
  }

  onChange(listener) {
    this.listeners.push(listener);
    return () => {
      this.listeners = this.listeners.filter(l => l !== listener);
    };
  }

  notify() {
    this.listeners.forEach(fn => fn(this.currentUser));
  }

  getToken() {
    return sessionStorage.getItem(this.tokenKey);
  }

  isAuthenticated() {
    return !!this.getToken() && !!this.currentUser;
  }

  getRole() {
    return (this.currentUser?.role || '').toLowerCase();
  }

  isEmployee() {
    return this.getRole() === 'employee';
  }

  isReviewer() {
    return this.getRole() === 'reviewer';
  }

  isManager() {
    return this.getRole() === 'manager';
  }

  isAdmin() {
    const r = this.getRole();
    return r === 'administrator' || r === 'admin';
  }

  canApprove() {
    const r = this.getRole();
    return ['manager', 'admin', 'administrator', 'reviewer'].includes(r);
  }

  canManageTeam() {
    const r = this.getRole();
    return ['manager', 'admin', 'administrator'].includes(r);
  }

  decodeToken(token) {
    try {
      const base64Url = token.split('.')[1];
      const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
      const jsonPayload = decodeURIComponent(
        atob(base64)
          .split('')
          .map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
          .join('')
      );
      return JSON.parse(jsonPayload);
    } catch {
      return {};
    }
  }

  async initAuth() {
    const token = this.getToken();
    if (!token) {
      this.currentUser = null;
      this.notify();
      return null;
    }

    try {
      // First try /users/me
      let user = await authApi.getProfile();
      if (!user) {
        // Fallback to /users and find by email from sub
        const payload = this.decodeToken(token);
        const email = payload.sub;
        if (email) {
          const users = await authApi.listUsers();
          user = users.find(u => u.email.toLowerCase() === email.toLowerCase()) || null;
        }
      }

      if (user) {
        this.currentUser = user;
        sessionStorage.setItem(this.userKey, JSON.stringify(user));
        this.notify();
        return user;
      } else {
        this.logout(false);
        return null;
      }
    } catch {
      this.logout(false);
      return null;
    }
  }

  async login(email, password) {
    const res = await authApi.login(email, password);
    sessionStorage.setItem(this.tokenKey, res.access_token);
    await this.initAuth();
    return this.currentUser;
  }

  async register(userData) {
    return authApi.register(userData);
  }

  logout(showNotice = true) {
    sessionStorage.removeItem(this.tokenKey);
    sessionStorage.removeItem(this.userKey);
    this.currentUser = null;
    this.notify();
    if (showNotice) {
      window.dispatchEvent(new CustomEvent('edr:toast', {
        detail: { message: 'Signed out successfully.', type: 'info' }
      }));
    }
    window.location.hash = '#login';
  }
}

export const auth = new AuthManager();
