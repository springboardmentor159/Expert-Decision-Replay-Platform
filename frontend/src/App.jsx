import React, { useState } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ThemeProvider } from './context/ThemeContext';
import { NotificationProvider } from './context/NotificationContext';

import { AppLayout } from './components/layout/AppLayout';
import { LoginPage } from './pages/auth/LoginPage';
import { RegisterPage } from './pages/auth/RegisterPage';
import { DashboardPage } from './pages/dashboard/DashboardPage';
import { DecisionsListPage } from './pages/decisions/DecisionsListPage';
import { CreateDecisionPage } from './pages/decisions/CreateDecisionPage';
import { DecisionDetailPage } from './pages/decisions/DecisionDetailPage';
import { KnowledgeRepositoryPage } from './pages/repository/KnowledgeRepositoryPage';
import { AuditLogsPage } from './pages/audit/AuditLogsPage';
import { ReportsPage } from './pages/reports/ReportsPage';
import { UserManagementPage } from './pages/admin/UserManagementPage';
import { ProfilePage } from './pages/profile/ProfilePage';
import { LoadingSpinner } from './components/common/LoadingSpinner';

function MainApp() {
  const { isAuthenticated, loading, role, isEmployee, isReviewer, isManager, isAdmin } = useAuth();
  const [authView, setAuthView] = useState('login'); // 'login' | 'register'
  const [currentView, setCurrentView] = useState('dashboard');
  const [selectedDecisionId, setSelectedDecisionId] = useState(null);
  const [previousView, setPreviousView] = useState('dashboard');

  if (loading) {
    return (
      <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <LoadingSpinner message="Initializing Expert Decision Replay Platform..." size="large" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return authView === 'login' ? (
      <LoginPage onNavigateRegister={() => setAuthView('register')} />
    ) : (
      <RegisterPage onNavigateLogin={() => setAuthView('login')} />
    );
  }

  const navigateToDecisionDetail = (id) => {
    setPreviousView(currentView);
    setSelectedDecisionId(id);
    setCurrentView('decision-detail');
  };

  const handleBackFromDetail = () => {
    setSelectedDecisionId(null);
    setCurrentView(previousView || 'dashboard');
  };

  const handleDecisionCreated = (newId) => {
    setSelectedDecisionId(newId);
    setCurrentView('decision-detail');
  };

  return (
    <AppLayout currentView={currentView} setCurrentView={setCurrentView}>
      {currentView === 'dashboard' && (
        <DashboardPage
          onSelectDecision={navigateToDecisionDetail}
          onNavigateCreate={() => setCurrentView('create-decision')}
          onNavigateReviews={() => setCurrentView('assigned-reviews')}
        />
      )}

      {currentView === 'create-decision' && (
        <CreateDecisionPage
          onCancel={() => setCurrentView(previousView || 'dashboard')}
          onDecisionCreated={handleDecisionCreated}
        />
      )}

      {currentView === 'decision-detail' && selectedDecisionId && (
        <DecisionDetailPage
          decisionId={selectedDecisionId}
          onBack={handleBackFromDetail}
        />
      )}

      {currentView === 'my-decisions' && (
        <DecisionsListPage
          title="My Decisions"
          subtitle="Decisions authored by you"
          onlyMine={true}
          onSelectDecision={navigateToDecisionDetail}
          onNavigateCreate={() => setCurrentView('create-decision')}
        />
      )}

      {(currentView === 'team-decisions' || currentView === 'all-decisions') && (
        <DecisionsListPage
          title={currentView === 'team-decisions' ? "Team Decisions" : "Decision Management"}
          subtitle={currentView === 'team-decisions' ? "Decisions created across your team and organization" : "Browse and manage organizational decisions"}
          onlyMine={false}
          onSelectDecision={navigateToDecisionDetail}
          onNavigateCreate={() => setCurrentView('create-decision')}
        />
      )}

      {currentView === 'assigned-reviews' && (
        <DecisionsListPage
          onSelectDecision={navigateToDecisionDetail}
          onNavigateCreate={() => setCurrentView('create-decision')}
          initialFilter={{ status: 'Under Review' }}
        />
      )}

      {currentView === 'repository' && (
        <KnowledgeRepositoryPage onSelectDecision={navigateToDecisionDetail} />
      )}

      {currentView === 'audit-logs' && <AuditLogsPage />}

      {currentView === 'reports' && <ReportsPage />}

      {currentView === 'user-management' && <UserManagementPage />}

      {currentView === 'profile' && (
        <ProfilePage
          onNavigateCreate={() => setCurrentView('create-decision')}
          onNavigateMyDecisions={() => setCurrentView('my-decisions')}
        />
      )}
    </AppLayout>
  );
}

export default function App() {
  return (
    <ThemeProvider>
      <NotificationProvider>
        <AuthProvider>
          <MainApp />
        </AuthProvider>
      </NotificationProvider>
    </ThemeProvider>
  );
}
