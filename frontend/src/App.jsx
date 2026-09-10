import React, { useState } from 'react';
import { ToastProvider } from './context/ToastContext';
import { AuthProvider, useAuth } from './context/AuthContext';
import { AppLayout } from './components/layout/AppLayout';
import { LoadingSpinner } from './components/common/LoadingSpinner';

// Pages
import { LoginPage } from './pages/auth/LoginPage';
import { RegisterPage } from './pages/auth/RegisterPage';
import { DashboardPage } from './pages/dashboard/DashboardPage';
import { DecisionListPage } from './pages/decisions/DecisionListPage';
import { CreateDecisionPage } from './pages/decisions/CreateDecisionPage';
import { DecisionDetailPage } from './pages/decisions/DecisionDetailPage';
import { KnowledgeRepositoryPage } from './pages/repository/KnowledgeRepositoryPage';
import { AuditLogsPage } from './pages/audit/AuditLogsPage';
import { ReportsPage } from './pages/reports/ReportsPage';
import { UserManagementPage } from './pages/users/UserManagementPage';

const AppContent = () => {
  const { isAuthenticated, loading } = useAuth();
  const [authView, setAuthView] = useState('login'); // 'login' or 'register'
  const [currentRoute, setCurrentRoute] = useState('dashboard');
  const [routeParams, setRouteParams] = useState({});

  const handleNavigate = (route, params = {}) => {
    setCurrentRoute(route);
    setRouteParams(params);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  if (loading) {
    return (
      <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <LoadingSpinner message="Initializing Enterprise Decision Replay..." size="lg" />
      </div>
    );
  }

  // Unauthenticated Flow
  if (!isAuthenticated) {
    if (authView === 'register') {
      return <RegisterPage onNavigateToLogin={() => setAuthView('login')} />;
    }
    return <LoginPage onNavigateToRegister={() => setAuthView('register')} />;
  }

  // Page title resolution
  const getPageTitle = () => {
    switch (currentRoute) {
      case 'dashboard':
        return 'System Overview & Dashboard';
      case 'decisions':
      case 'pending-approvals':
        return 'Decision Portfolio';
      case 'create-decision':
        return 'Author Architectural Decision';
      case 'decision-detail':
        return `Decision Details #${routeParams.id || ''}`;
      case 'repository':
        return 'Knowledge Repository & Discovery';
      case 'audit':
        return 'Security, Audit & Compliance';
      case 'reports':
        return 'Centralized Reports & Analytics';
      case 'users':
        return 'Tenant User Management';
      default:
        return 'Expert Decision Replay Platform';
    }
  };

  // Render active view inside AppLayout
  const renderView = () => {
    switch (currentRoute) {
      case 'dashboard':
        return <DashboardPage onNavigate={handleNavigate} />;
      case 'decisions':
      case 'pending-approvals':
        return <DecisionListPage onNavigate={handleNavigate} />;
      case 'create-decision':
        return <CreateDecisionPage onNavigate={handleNavigate} />;
      case 'decision-detail':
        return (
          <DecisionDetailPage
            decisionId={routeParams.id}
            initialTab={routeParams.activeTab || 'overview'}
            initialOpenEdit={routeParams.openEdit || false}
            onNavigate={handleNavigate}
          />
        );
      case 'repository':
        return <KnowledgeRepositoryPage onNavigate={handleNavigate} />;
      case 'audit':
        return <AuditLogsPage onNavigate={handleNavigate} />;
      case 'reports':
        return <ReportsPage onNavigate={handleNavigate} />;
      case 'users':
        return <UserManagementPage onNavigate={handleNavigate} />;
      default:
        return <DashboardPage onNavigate={handleNavigate} />;
    }
  };

  return (
    <AppLayout
      currentRoute={currentRoute}
      onRouteChange={handleNavigate}
      pageTitle={getPageTitle()}
    >
      {renderView()}
    </AppLayout>
  );
};

export default function App() {
  return (
    <ToastProvider>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </ToastProvider>
  );
}
