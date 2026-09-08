import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, UserRole } from './context/AuthContext';
import { ToastProvider } from './context/ToastContext';
import ProtectedRoute from './components/auth/ProtectedRoute';
import AppLayout from './components/layout/AppLayout';

import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import DecisionsPage from './pages/DecisionsPage';
import ComponentShowcasePage from './pages/ComponentShowcasePage';
import UnauthorizedPage from './pages/UnauthorizedPage';
import NotFoundPage from './pages/NotFoundPage';

export const App = () => {
  return (
    <BrowserRouter>
      <AuthProvider>
        <ToastProvider>
          <Routes>
            {/* Public Auth Route */}
            <Route path="/login" element={<LoginPage />} />

            {/* Protected Routes inside AppLayout */}
            <Route
              path="/"
              element={
                <ProtectedRoute>
                  <AppLayout />
                </ProtectedRoute>
              }
            >
              <Route index element={<Navigate to="/dashboard" replace />} />
              <Route path="dashboard" element={<DashboardPage />} />
              <Route path="decisions" element={<DecisionsPage />} />
              <Route path="component-library" element={<ComponentShowcasePage />} />

              {/* Manager & Admin Only Areas */}
              <Route
                path="manager/stats"
                element={
                  <ProtectedRoute allowedRoles={[UserRole.MANAGER, UserRole.ADMINISTRATOR]}>
                    <DashboardPage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="reports"
                element={
                  <ProtectedRoute allowedRoles={[UserRole.MANAGER, UserRole.ADMINISTRATOR]}>
                    <DashboardPage />
                  </ProtectedRoute>
                }
              />

              {/* Admin Only Areas */}
              <Route
                path="admin/users"
                element={
                  <ProtectedRoute allowedRoles={[UserRole.ADMINISTRATOR]}>
                    <DashboardPage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="admin/audit"
                element={
                  <ProtectedRoute allowedRoles={[UserRole.ADMINISTRATOR]}>
                    <DashboardPage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="admin/security-logs"
                element={
                  <ProtectedRoute allowedRoles={[UserRole.ADMINISTRATOR]}>
                    <DashboardPage />
                  </ProtectedRoute>
                }
              />

              {/* Error Pages */}
              <Route path="unauthorized" element={<UnauthorizedPage />} />
              <Route path="*" element={<NotFoundPage />} />
            </Route>

            {/* Fallback */}
            <Route path="*" element={<NotFoundPage />} />
          </Routes>
        </ToastProvider>
      </AuthProvider>
    </BrowserRouter>
  );
};

export default App;
