import React from 'react';
import { BrowserRouter, Routes, Route, Navigate, Outlet } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ToastProvider } from './components/common/Toast';
import { Sidebar } from './components/common/Sidebar';
import { Navbar } from './components/common/Navbar';
import { LoadingSpinner } from './components/common/LoadingSpinner';

// Pages
import { LoginPage } from './pages/auth/LoginPage';
import { RegisterPage } from './pages/auth/RegisterPage';
import { DashboardRouter } from './pages/dashboard/DashboardRouter';
import { DecisionListPage } from './pages/decisions/DecisionListPage';
import { CreateDecisionPage } from './pages/decisions/CreateDecisionPage';
import { EditDecisionPage } from './pages/decisions/EditDecisionPage';
import { DecisionDetailPage } from './pages/decisions/DecisionDetailPage';
import { KnowledgeRepositoryPage } from './pages/repository/KnowledgeRepositoryPage';
import { AuditLogsPage } from './pages/audit/AuditLogsPage';
import { ReportsPage } from './pages/reports/ReportsPage';
import { UserManagementPage } from './pages/admin/UserManagementPage';
import { AssignedReviewsPage } from './pages/reviewer/AssignedReviewsPage';
import { PendingApprovalsPage } from './pages/manager/PendingApprovalsPage';
import { ForbiddenPage } from './pages/errors/ForbiddenPage';
import { NotFoundPage } from './pages/errors/NotFoundPage';

// Authenticated Application Shell Layout
const AppLayout = () => {
  return (
    <div className="app-container">
      <Sidebar />
      <div className="app-main">
        <Navbar />
        <main className="header-content-body">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

// Route Guard with Role Verification
const ProtectedRoute = ({ allowedRoles = null }) => {
  const { isAuthenticated, isLoading, user } = useAuth();

  if (isLoading) {
    return (
      <div style={{ height: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <LoadingSpinner message="Checking authentication status..." />
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (allowedRoles && !allowedRoles.includes(user?.role)) {
    return <ForbiddenPage />;
  }

  return <AppLayout />;
};

export function App() {
  return (
    <AuthProvider>
      <ToastProvider>
        <BrowserRouter>
          <Routes>
            {/* Public Auth Routes */}
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />

            {/* Protected Routes (All authenticated users) */}
            <Route element={<ProtectedRoute />}>
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route path="/dashboard" element={<DashboardRouter />} />

              {/* Decisions */}
              <Route path="/decisions" element={<DecisionListPage />} />
              <Route path="/decisions/create" element={<CreateDecisionPage />} />
              <Route path="/decisions/:id" element={<DecisionDetailPage />} />
              <Route path="/decisions/:id/edit" element={<EditDecisionPage />} />

              {/* Knowledge Base */}
              <Route path="/repository" element={<KnowledgeRepositoryPage />} />
            </Route>

            {/* Reviewer / Manager / Admin Review Routes */}
            <Route element={<ProtectedRoute allowedRoles={['Reviewer', 'Manager', 'Administrator']} />}>
              <Route path="/reviewer/reviews" element={<AssignedReviewsPage />} />
            </Route>

            {/* Manager / Admin Routes */}
            <Route element={<ProtectedRoute allowedRoles={['Manager', 'Administrator']} />}>
              <Route path="/manager/approvals" element={<PendingApprovalsPage />} />
              <Route path="/reports" element={<ReportsPage />} />
            </Route>

            {/* Administrator Only Routes */}
            <Route element={<ProtectedRoute allowedRoles={['Administrator']} />}>
              <Route path="/admin/users" element={<UserManagementPage />} />
              <Route path="/audit-logs" element={<AuditLogsPage />} />
            </Route>

            {/* Errors */}
            <Route path="/403" element={<ForbiddenPage />} />
            <Route path="*" element={<NotFoundPage />} />
          </Routes>
        </BrowserRouter>
      </ToastProvider>
    </AuthProvider>
  );
}

export default App;
