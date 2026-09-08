import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  FileText,
  Shield,
  BarChart3,
  Users,
  CheckCircle2,
  AlertTriangle,
  ArrowRight,
  PlusCircle,
  Component,
  Activity,
  History,
  Lock,
} from 'lucide-react';
import { useAuth, UserRole } from '../context/AuthContext';
import apiClient from '../api/client';
import Badge from '../components/common/Badge';
import Button from '../components/common/Button';
import Alert from '../components/common/Alert';
import RoleGate from '../components/auth/RoleGate';

export const DashboardPage = () => {
  const { user, hasRole, isEmployee, isReviewer, isManager, isAdmin } = useAuth();
  const [apiStatus, setApiStatus] = useState('checking');
  const [stats, setStats] = useState({
    totalDecisions: 0,
    underReview: 0,
    approved: 0,
    rejected: 0,
  });

  useEffect(() => {
    // Check backend connectivity
    apiClient
      .get('/')
      .then(() => setApiStatus('connected'))
      .catch(() => setApiStatus('disconnected'));

    // Fetch dashboard stats if available
    const endpoint = isEmployee
      ? '/dashboard/employee'
      : isManager
      ? '/dashboard/manager/statistics'
      : isAdmin
      ? '/dashboard/admin'
      : '/decisions';

    apiClient
      .get(endpoint)
      .then((res) => {
        if (res.data) {
          setStats({
            totalDecisions: res.data.total_decisions || res.data.length || 0,
            underReview: res.data.status_counts?.['Under Review'] || 0,
            approved: res.data.status_counts?.['Approved'] || 0,
            rejected: res.data.status_counts?.['Rejected'] || 0,
          });
        }
      })
      .catch(() => {
        // Fallback gracefully
      });
  }, [user, isEmployee, isManager, isAdmin]);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '28px' }}>
      {/* Welcome Banner */}
      <div
        className="apple-card"
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '20px',
          background: 'linear-gradient(135deg, var(--color-canvas) 0%, var(--color-surface-pearl) 100%)',
        }}
      >
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
            <h1 style={{ fontSize: '24px', fontWeight: 600 }}>
              Welcome back, {user?.full_name || user?.email}
            </h1>
            <Badge variant="role" size="medium">
              {user?.role}
            </Badge>
          </div>
          <p style={{ fontSize: '14px', color: 'var(--color-ink-muted-48)' }}>
            Signed in as <strong>{user?.email}</strong> · Department:{' '}
            <strong>{user?.department || 'Engineering'}</strong>
          </p>
        </div>

        <div style={{ display: 'flex', gap: '10px' }}>
          <Link to="/component-library">
            <Button variant="pearl" size="medium" icon={Component}>
              UI Components
            </Button>
          </Link>
          <Link to="/decisions">
            <Button variant="primary" size="medium" icon={FileText}>
              View Decisions
            </Button>
          </Link>
        </div>
      </div>

      {/* Backend API Connection Alert */}
      {apiStatus === 'disconnected' && (
        <Alert type="warning" title="Backend Connection Issue">
          Could not establish connection to the FastAPI backend at <code>http://localhost:8000</code>. Please ensure the backend server is running.
        </Alert>
      )}

      {/* Role-Based Quick Access Cards */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
          gap: '20px',
        }}
      >
        {/* Workspace Card (All roles) */}
        <div className="apple-card" style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', color: 'var(--color-primary)' }}>
            <FileText size={22} />
            <h3 style={{ fontSize: '17px', fontWeight: 600, color: 'var(--color-ink)' }}>Decisions Center</h3>
          </div>
          <p style={{ fontSize: '13px', color: 'var(--color-ink-muted-48)', lineHeight: 1.5 }}>
            Create and browse decision proposals, evaluate weighted alternatives, participate in discussion threads.
          </p>
          <div style={{ marginTop: 'auto', paddingTop: '10px' }}>
            <Link to="/decisions" style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', fontSize: '13px', fontWeight: 500 }}>
              <span>Go to Decisions</span>
              <ArrowRight size={14} />
            </Link>
          </div>
        </div>

        {/* Manager & Admin Reports */}
        <RoleGate allowedRoles={[UserRole.MANAGER, UserRole.ADMINISTRATOR]}>
          <div className="apple-card" style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', color: '#0369a1' }}>
              <BarChart3 size={22} />
              <h3 style={{ fontSize: '17px', fontWeight: 600, color: 'var(--color-ink)' }}>Manager Analytics & Reports</h3>
            </div>
            <p style={{ fontSize: '13px', color: 'var(--color-ink-muted-48)', lineHeight: 1.5 }}>
              Access aggregate organizational decision metrics, department breakdowns, and export PDF/Excel summaries.
            </p>
            <div style={{ marginTop: 'auto', paddingTop: '10px' }}>
              <Link to="/reports" style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', fontSize: '13px', fontWeight: 500 }}>
                <span>Open Analytics</span>
                <ArrowRight size={14} />
              </Link>
            </div>
          </div>
        </RoleGate>

        {/* Administrator Security Hub */}
        <RoleGate allowedRoles={[UserRole.ADMINISTRATOR]}>
          <div className="apple-card" style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', color: '#6d28d9' }}>
              <Shield size={22} />
              <h3 style={{ fontSize: '17px', fontWeight: 600, color: 'var(--color-ink)' }}>Admin & Compliance Hub</h3>
            </div>
            <p style={{ fontSize: '13px', color: 'var(--color-ink-muted-48)', lineHeight: 1.5 }}>
              Manage users, audit immutable system logs, monitor login events, and oversee decision moderation.
            </p>
            <div style={{ marginTop: 'auto', paddingTop: '10px' }}>
              <Link to="/admin/audit" style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', fontSize: '13px', fontWeight: 500 }}>
                <span>Audit Trail</span>
                <ArrowRight size={14} />
              </Link>
            </div>
          </div>
        </RoleGate>
      </div>

      {/* Permissions Matrix Breakdown */}
      <div className="apple-card">
        <h2 style={{ fontSize: '18px', fontWeight: 600, marginBottom: '6px' }}>
          Role Capabilities: {user?.role}
        </h2>
        <p style={{ fontSize: '13px', color: 'var(--color-ink-muted-48)', marginBottom: '16px' }}>
          Your account is subject to role-based access control (RBAC) enforced on both the frontend UI and backend API.
        </p>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '12px' }}>
          <div
            style={{
              padding: '12px 14px',
              borderRadius: 'var(--radius-sm)',
              backgroundColor: 'var(--color-surface-pearl)',
              display: 'flex',
              alignItems: 'center',
              gap: '10px',
              fontSize: '13px',
            }}
          >
            <CheckCircle2 size={16} color="#059669" />
            <span>Create & edit own decisions</span>
          </div>

          <div
            style={{
              padding: '12px 14px',
              borderRadius: 'var(--radius-sm)',
              backgroundColor: 'var(--color-surface-pearl)',
              display: 'flex',
              alignItems: 'center',
              gap: '10px',
              fontSize: '13px',
            }}
          >
            <CheckCircle2 size={16} color="#059669" />
            <span>Discussions & alternatives comparison</span>
          </div>

          <div
            style={{
              padding: '12px 14px',
              borderRadius: 'var(--radius-sm)',
              backgroundColor: 'var(--color-surface-pearl)',
              display: 'flex',
              alignItems: 'center',
              gap: '10px',
              fontSize: '13px',
            }}
          >
            {isReviewer || isManager || isAdmin ? (
              <CheckCircle2 size={16} color="#059669" />
            ) : (
              <Lock size={16} color="#9ca3af" />
            )}
            <span style={{ color: isReviewer || isManager || isAdmin ? 'inherit' : 'var(--color-ink-muted-48)' }}>
              Decision review & approval
            </span>
          </div>

          <div
            style={{
              padding: '12px 14px',
              borderRadius: 'var(--radius-sm)',
              backgroundColor: 'var(--color-surface-pearl)',
              display: 'flex',
              alignItems: 'center',
              gap: '10px',
              fontSize: '13px',
            }}
          >
            {isManager || isAdmin ? (
              <CheckCircle2 size={16} color="#059669" />
            ) : (
              <Lock size={16} color="#9ca3af" />
            )}
            <span style={{ color: isManager || isAdmin ? 'inherit' : 'var(--color-ink-muted-48)' }}>
              Manager statistics & Reports
            </span>
          </div>

          <div
            style={{
              padding: '12px 14px',
              borderRadius: 'var(--radius-sm)',
              backgroundColor: 'var(--color-surface-pearl)',
              display: 'flex',
              alignItems: 'center',
              gap: '10px',
              fontSize: '13px',
            }}
          >
            {isAdmin ? (
              <CheckCircle2 size={16} color="#059669" />
            ) : (
              <Lock size={16} color="#9ca3af" />
            )}
            <span style={{ color: isAdmin ? 'inherit' : 'var(--color-ink-muted-48)' }}>
              User management & Admin Audit
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
