import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, UserRole } from './context/AuthContext';
import { ToastProvider } from './context/ToastContext';
import ProtectedRoute from './components/auth/ProtectedRoute';
import AppLayout from './components/layout/AppLayout';

import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import DecisionsPage from './pages/DecisionsPage';
import DecisionDetailPage from './pages/DecisionDetailPage';
import ReportsPage from './pages/ReportsPage';
import ManagerStatsPage from './pages/ManagerStatsPage';
import AdminUsersPage from './pages/AdminUsersPage';
import AdminAuditPage from './pages/AdminAuditPage';
import AdminSecurityLogsPage from './pages/AdminSecurityLogsPage';
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
              <Route path="decisions/:decisionId" element={<DecisionDetailPage />} />

              {/* Manager & Admin Only Areas */}
              <Route
                path="manager/stats"
                element={
                  <ProtectedRoute allowedRoles={[UserRole.MANAGER, UserRole.ADMINISTRATOR]}>
                    <ManagerStatsPage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="reports"
                element={
                  <ProtectedRoute allowedRoles={[UserRole.MANAGER, UserRole.ADMINISTRATOR]}>
                    <ReportsPage />
                  </ProtectedRoute>
                }
              />

              {/* Admin Only Areas */}
              <Route
                path="admin/users"
                element={
                  <ProtectedRoute allowedRoles={[UserRole.ADMINISTRATOR]}>
                    <AdminUsersPage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="admin/audit"
                element={
                  <ProtectedRoute allowedRoles={[UserRole.ADMINISTRATOR]}>
                    <AdminAuditPage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="admin/security-logs"
                element={
                  <ProtectedRoute allowedRoles={[UserRole.ADMINISTRATOR]}>
                    <AdminSecurityLogsPage />
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
