import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { dashboardService } from '../../services/dashboardService';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import {
  Users,
  FileText,
  CheckSquare,
  ShieldCheck,
  Activity,
  BarChart3,
  Layers,
  ArrowUpRight,
  TrendingUp,
} from 'lucide-react';

export const AdminDashboard = () => {
  const [dashboard, setDashboard] = useState(null);
  const [approvalStats, setApprovalStats] = useState(null);
  const [userStats, setUserStats] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchAdminData = async () => {
      setIsLoading(true);
      setError('');
      try {
        const [dashData, apprvData, uData] = await Promise.all([
          dashboardService.getAdminDashboard(),
          dashboardService.getAdminApprovalStatistics(),
          dashboardService.getAdminUserActivity(),
        ]);
        setDashboard(dashData);
        setApprovalStats(apprvData);
        setUserStats(uData);
      } catch (err) {
        setError(err.userMessage || 'Failed to load administrator dashboard');
      } finally {
        setIsLoading(false);
      }
    };

    fetchAdminData();
  }, []);

  if (isLoading) return <LoadingSpinner message="Loading administrator dashboard..." />;

  if (error) {
    return (
      <div className="alert alert-error" style={{ margin: '2rem' }}>
        <span>{error}</span>
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      {/* Admin Header Banner */}
      <div
        style={{
          background: 'linear-gradient(135deg, #ecfdf5 0%, #f0fdf4 100%)',
          border: '1px solid #a7f3d0',
          borderRadius: 'var(--radius-lg)',
          padding: '2rem',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '1rem',
        }}
      >
        <div>
          <h2 style={{ fontSize: '1.6rem', color: 'var(--text-primary)', fontWeight: 800 }}>
            System Administration & Governance
          </h2>
          <p className="text-muted" style={{ marginTop: '0.35rem', fontSize: '0.95rem' }}>
            Enterprise compliance monitoring, user lifecycle management, and organization-wide decision intelligence.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '0.75rem' }}>
          <Link to="/admin/users" className="btn btn-secondary">
            <Users size={16} />
            <span>Manage Users</span>
          </Link>
          <Link to="/audit-logs" className="btn btn-primary">
            <ShieldCheck size={16} />
            <span>Audit Trail</span>
          </Link>
        </div>
      </div>

      {/* Metrics Row */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: '1.25rem',
        }}
      >
        <div className="stat-card">
          <div className="stat-icon-wrapper stat-icon-cyan">
            <Users size={26} />
          </div>
          <div className="stat-content">
            <span className="stat-value">{dashboard?.total_users || 0}</span>
            <span className="stat-label">Total Users</span>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon-wrapper stat-icon-primary">
            <FileText size={26} />
          </div>
          <div className="stat-content">
            <span className="stat-value">{dashboard?.total_decisions || 0}</span>
            <span className="stat-label">Total Decisions</span>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon-wrapper stat-icon-warning">
            <CheckSquare size={26} />
          </div>
          <div className="stat-content">
            <span className="stat-value">{dashboard?.pending_approvals || 0}</span>
            <span className="stat-label">Pending Approvals</span>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon-wrapper stat-icon-success">
            <TrendingUp size={26} />
          </div>
          <div className="stat-content">
            <span className="stat-value">{approvalStats?.completion_rate || 0}%</span>
            <span className="stat-label">Completion Rate</span>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon-wrapper stat-icon-primary">
            <Activity size={26} />
          </div>
          <div className="stat-content">
            <span className="stat-value">{userStats?.active_users_count || 0}</span>
            <span className="stat-label">Active Users</span>
          </div>
        </div>
      </div>

      {/* Decision Pipeline Distribution */}
      <div className="card">
        <div className="card-header">
          <h3 className="card-title">
            <BarChart3 size={20} color="var(--primary-light)" />
            Enterprise Decision Lifecycle Breakdown
          </h3>
        </div>

        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))',
            gap: '1rem',
          }}
        >
          <div style={{ background: 'var(--bg-elevated)', padding: '1rem', borderRadius: 'var(--radius-sm)' }}>
            <span className="text-dim" style={{ fontSize: '0.8rem' }}>Draft Decisions</span>
            <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#475569', marginTop: '4px' }}>
              {dashboard?.draft_decisions || 0}
            </div>
          </div>

          <div style={{ background: 'var(--bg-elevated)', padding: '1rem', borderRadius: 'var(--radius-sm)' }}>
            <span className="text-dim" style={{ fontSize: '0.8rem' }}>Under Review</span>
            <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#b45309', marginTop: '4px' }}>
              {dashboard?.under_review || 0}
            </div>
          </div>

          <div style={{ background: 'var(--bg-elevated)', padding: '1rem', borderRadius: 'var(--radius-sm)' }}>
            <span className="text-dim" style={{ fontSize: '0.8rem' }}>Approved</span>
            <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#047857', marginTop: '4px' }}>
              {dashboard?.approved_decisions || 0}
            </div>
          </div>

          <div style={{ background: 'var(--bg-elevated)', padding: '1rem', borderRadius: 'var(--radius-sm)' }}>
            <span className="text-dim" style={{ fontSize: '0.8rem' }}>Rejected</span>
            <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#b91c1c', marginTop: '4px' }}>
              {dashboard?.rejected_decisions || 0}
            </div>
          </div>

          <div style={{ background: 'var(--bg-elevated)', padding: '1rem', borderRadius: 'var(--radius-sm)' }}>
            <span className="text-dim" style={{ fontSize: '0.8rem' }}>Avg Turnaround</span>
            <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#4338ca', marginTop: '4px' }}>
              {approvalStats?.average_approval_time_hours ? `${approvalStats.average_approval_time_hours} hrs` : 'N/A'}
            </div>
          </div>
        </div>
      </div>

      {/* Grid: Active Users & Recent System Audit Activities */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
        {/* Active Users */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">
              <Users size={20} color="var(--accent-cyan)" />
              Recent Active Personnel
            </h3>
            <Link to="/admin/users" className="btn btn-secondary btn-sm">
              View All
            </Link>
          </div>

          <div className="table-container" style={{ border: 'none' }}>
            <table className="table">
              <thead>
                <tr>
                  <th>User</th>
                  <th>Role</th>
                  <th>Actions</th>
                  <th>Last Active</th>
                </tr>
              </thead>
              <tbody>
                {(userStats?.active_users || []).slice(0, 5).map((u) => (
                  <tr key={u.id}>
                    <td>
                      <div className="table-cell-title">{u.full_name}</div>
                      <span className="text-dim" style={{ fontSize: '0.78rem' }}>{u.email}</span>
                    </td>
                    <td>
                      <span className="badge badge-category">{u.role}</span>
                    </td>
                    <td style={{ fontWeight: 600, color: '#4338ca' }}>{u.action_count}</td>
                    <td style={{ fontSize: '0.8rem', color: 'var(--text-dim)' }}>
                      {u.last_active ? new Date(u.last_active).toLocaleDateString() : 'Never'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* System Activity Stream */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">
              <Activity size={20} color="var(--primary-light)" />
              System Audit Stream
            </h3>
            <Link to="/audit-logs" className="btn btn-secondary btn-sm">
              Full Logs
            </Link>
          </div>

          <div className="timeline">
            {(dashboard?.recent_activities || []).slice(0, 6).map((act) => (
              <div key={act.id} className="timeline-item">
                <div className="timeline-dot">
                  <div className="timeline-dot-inner"></div>
                </div>
                <div className="timeline-content">
                  <div className="timeline-meta">
                    <span className="timeline-title">
                      {act.user_name || 'System'} • {act.action?.replace('_', ' ').toUpperCase()}
                    </span>
                    <span className="timeline-time">
                      {new Date(act.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </span>
                  </div>
                  <p className="timeline-desc">{act.description}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
