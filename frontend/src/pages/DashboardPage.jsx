import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  FileText,
  Shield,
  BarChart3,
  Users,
  CheckCircle2,
  Lock,
  PlusCircle,
  Activity,
  History,
  TrendingUp,
  Globe,
} from 'lucide-react';
import { useAuth, UserRole } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import apiClient from '../api/client';
import Badge from '../components/common/Badge';
import Button from '../components/common/Button';
import Alert from '../components/common/Alert';
import LoadingSpinner from '../components/common/LoadingSpinner';
import RoleGate from '../components/auth/RoleGate';

export const DashboardPage = () => {
  const { user, hasRole, isEmployee, isReviewer, isManager, isAdmin } = useAuth();
  const [apiStatus, setApiStatus] = useState('checking');
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    totalDecisions: 0,
    totalUsers: 0,
    draft: 0,
    underReview: 0,
    approved: 0,
    rejected: 0,
    archived: 0,
    recentActivity: [],
  });

  const navigate = useNavigate();
  const toast = useToast();

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        await apiClient.get('/');
        setApiStatus('connected');

        let endpoint = '/dashboard/employee';
        if (isManager) endpoint = '/dashboard/manager/statistics';
        if (isAdmin) endpoint = '/dashboard/admin';

        const res = await apiClient.get(endpoint);
        const data = res.data;

        if (endpoint === '/dashboard/employee') {
          const byStatus = {};
          (data.decisions_by_status || []).forEach((s) => {
            const key = s.status.toLowerCase().replace(/\s+/g, '_');
            byStatus[key] = s.count;
          });
          setStats({
            totalDecisions: data.total_decisions,
            totalUsers: 0,
            draft: byStatus.draft || 0,
            underReview: byStatus.under_review || 0,
            approved: byStatus.approved || 0,
            rejected: byStatus.rejected || 0,
            archived: byStatus.archived || 0,
            recentActivity: data.recent_activity || [],
          });
        } else if (endpoint === '/dashboard/manager/statistics') {
          setStats({
            totalDecisions: data.total || 0,
            totalUsers: 0,
            draft: data.draft || 0,
            underReview: data.under_review || 0,
            approved: data.approved || 0,
            rejected: data.rejected || 0,
            archived: data.archived || 0,
            recentActivity: [],
          });
        } else if (endpoint === '/dashboard/admin') {
          const ds = data.decision_stats || {};
          setStats({
            totalDecisions: data.total_decisions || ds.total || 0,
            totalUsers: data.total_users || 0,
            draft: ds.draft || 0,
            underReview: ds.under_review || 0,
            approved: ds.approved || 0,
            rejected: ds.rejected || 0,
            archived: ds.archived || 0,
            recentActivity: data.recent_activity || [],
          });
        }
      } catch (err) {
        setApiStatus('disconnected');
        if (err.status !== 401) {
          toast.error(err.formattedMessage || 'Failed to load dashboard data');
        }
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [user, isEmployee, isManager, isAdmin, toast]);

  const statCards = [
    { label: 'Total Decisions', value: stats.totalDecisions, icon: FileText, color: '#0066cc', role: 'all' },
    { label: 'Under Review', value: stats.underReview, icon: TrendingUp, color: '#d97706', role: 'all' },
    { label: 'Approved', value: stats.approved, icon: CheckCircle2, color: '#16a34a', role: 'all' },
    { label: 'Rejected', value: stats.rejected, icon: Lock, color: '#dc2626', role: 'all' },
    { label: 'Total Users', value: stats.totalUsers, icon: Users, color: '#7c3aed', role: 'admin' },
    { label: 'Draft', value: stats.draft, icon: Activity, color: '#6b7280', role: 'all' },
    { label: 'Archived', value: stats.archived, icon: History, color: '#9ca3af', role: 'all' },
  ];

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '300px' }}>
        <LoadingSpinner size="large" text="Loading dashboard..." />
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '28px' }}>
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
          <Link to="/decisions">
            <Button variant="primary" size="medium" icon={FileText}>
              View Decisions
            </Button>
          </Link>
        </div>
      </div>

      {apiStatus === 'disconnected' && (
        <Alert type="warning" title="Backend Connection Issue">
          Could not establish connection to the FastAPI backend. Please ensure the backend server is running at{' '}
          <code>http://localhost:8000</code>.
        </Alert>
      )}

      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
          gap: '16px',
        }}
      >
        {statCards.filter((c) => c.role === 'all' || hasRole([UserRole.MANAGER, UserRole.ADMINISTRATOR])).map((card) => (
          <div key={card.label} className="apple-card" style={{ textAlign: 'center', padding: '20px 16px' }}>
            <div
              style={{
                width: '40px',
                height: '40px',
                borderRadius: 'var(--radius-pill)',
                backgroundColor: `${card.color}15`,
                color: card.color,
                display: 'inline-flex',
                alignItems: 'center',
                justifyContent: 'center',
                margin: '0 auto 10px',
              }}
            >
              <card.icon size={20} />
            </div>
            <div style={{ fontSize: '28px', fontWeight: 600, color: 'var(--color-ink)' }}>{card.value}</div>
            <div style={{ fontSize: '12px', color: 'var(--color-ink-muted-48)' }}>{card.label}</div>
          </div>
        ))}
      </div>

      <div className="apple-card">
        <h2 style={{ fontSize: '18px', fontWeight: 600, marginBottom: '16px' }}>
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
            {(isReviewer || isManager || isAdmin) ? (
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
            {(isManager || isAdmin) ? (
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
            <span>Audit trail & Activity log</span>
          </div>
        </div>
      </div>

      {stats.recentActivity.length > 0 && (
        <div className="apple-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
            <h2 style={{ fontSize: '18px', fontWeight: 600 }}>Recent Activity</h2>
            <Link
              to="/activities"
              style={{ fontSize: '13px', fontWeight: 500, color: 'var(--color-primary)' }}
            >
              View all
            </Link>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {stats.recentActivity.slice(0, 10).map((activity) => (
              <div
                key={activity.id}
                style={{
                  padding: '10px 14px',
                  borderRadius: 'var(--radius-sm)',
                  backgroundColor: 'var(--color-surface-pearl)',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '10px',
                  fontSize: '13px',
                }}
              >
                <Activity size={14} color="var(--color-ink-muted-48)" />
                <span style={{ color: 'var(--color-ink-muted-80)' }}>{activity.description || `${activity.action} ${activity.entity_type}`}</span>
                <span style={{ marginLeft: 'auto', fontSize: '11px', color: 'var(--color-ink-muted-48)' }}>
                  {new Date(activity.created_at).toLocaleString()}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      <RoleGate allowedRoles={[UserRole.MANAGER, UserRole.ADMINISTRATOR]}>
        <div className="apple-card" style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', color: '#0369a1' }}>
            <BarChart3 size={22} />
            <h3 style={{ fontSize: '17px', fontWeight: 600 }}>Manager Analytics & Reports</h3>
          </div>
          <p style={{ fontSize: '13px', color: 'var(--color-ink-muted-48)', lineHeight: 1.5 }}>
            Access aggregate organizational decision metrics, department breakdowns, and export PDF/Excel summaries.
          </p>
          <div style={{ marginTop: 'auto', paddingTop: '10px' }}>
            <Link to="/reports" style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', fontSize: '13px', fontWeight: 500 }}>
              <span>Open Analytics</span>
              <TrendingUp size={14} />
            </Link>
          </div>
        </div>

        <div className="apple-card" style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', color: '#6d28d9' }}>
            <Shield size={22} />
            <h3 style={{ fontSize: '17px', fontWeight: 600 }}>Admin & Compliance Hub</h3>
          </div>
          <p style={{ fontSize: '13px', color: 'var(--color-ink-muted-48)', lineHeight: 1.5 }}>
            Manage users, audit immutable system logs, monitor login events, and oversee decision moderation.
          </p>
          <div style={{ marginTop: 'auto', paddingTop: '10px' }}>
            <Link to="/admin/audit" style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', fontSize: '13px', fontWeight: 500 }}>
              <span>Audit Trail</span>
              <History size={14} />
            </Link>
          </div>
        </div>
      </RoleGate>
    </div>
  );
};

export default DashboardPage;
