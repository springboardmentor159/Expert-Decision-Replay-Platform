import React, { useState, useEffect } from 'react';
import { dashboardService } from '../../api/dashboardService';
import { Card } from '../../components/common/Card';
import { Button } from '../../components/common/Button';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import { useToast } from '../../context/ToastContext';
import {
  Users,
  FileText,
  ShieldCheck,
  Activity,
  UserCheck,
  BarChart3,
  Lock,
  ArrowRight,
} from 'lucide-react';

export const AdminDashboard = ({ onNavigate }) => {
  const [metrics, setMetrics] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const [activeUsers, setActiveUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const { error } = useToast();

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [adminData, analyticsData, usersData] = await Promise.all([
          dashboardService.getAdminDashboard(),
          dashboardService.getAdminAnalytics(),
          dashboardService.getAdminActiveUsers(),
        ]);
        setMetrics(adminData);
        setAnalytics(analyticsData);
        setActiveUsers(usersData || []);
      } catch (err) {
        error(err.message || 'Failed to load administrator telemetry');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) return <LoadingSpinner message="Aggregating platform telemetry..." />;

  return (
    <div>
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '2rem',
          flexWrap: 'wrap',
          gap: '1rem',
        }}
      >
        <div>
          <h2 style={{ fontSize: '1.75rem', fontWeight: 800, color: '#ffffff' }}>
            System Administration & Telemetry
          </h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem' }}>
            System health, compliance auditing, user governance, and organizational decision metrics.
          </p>
        </div>
        <div style={{ display: 'flex', gap: '0.75rem' }}>
          <Button
            variant="outline"
            icon={Lock}
            onClick={() => onNavigate('audit')}
          >
            Audit Logs
          </Button>
          <Button
            variant="primary"
            icon={Users}
            onClick={() => onNavigate('users')}
          >
            Manage Users
          </Button>
        </div>
      </div>

      {/* Primary KPI Grid */}
      <div className="stat-grid">
        <Card className="stat-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span className="stat-title">Total Users</span>
            <Users size={20} color="#3b82f6" />
          </div>
          <span className="stat-value">{metrics?.users?.total_users ?? 0}</span>
          <span className="stat-desc">Provisioned tenant accounts</span>
        </Card>

        <Card className="stat-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span className="stat-title">Total Decisions</span>
            <FileText size={20} color="#8b5cf6" />
          </div>
          <span className="stat-value">{metrics?.decisions?.total_decisions ?? 0}</span>
          <span className="stat-desc">Recorded decisions to date</span>
        </Card>

        <Card className="stat-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span className="stat-title">Active Approvals</span>
            <ShieldCheck size={20} color="#f59e0b" />
          </div>
          <span className="stat-value" style={{ color: '#fbbf24' }}>
            {metrics?.approvals?.pending_approvals ?? 0}
          </span>
          <span className="stat-desc">Pending across departments</span>
        </Card>

        <Card className="stat-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span className="stat-title">Active Users (30d)</span>
            <UserCheck size={20} color="#10b981" />
          </div>
          <span className="stat-value" style={{ color: '#34d399' }}>
            {activeUsers.length}
          </span>
          <span className="stat-desc">Participating contributors</span>
        </Card>
      </div>

      {/* Dual Section: Active Users & Telemetry Activity */}
      <div style={{ display: 'grid', gridTemplateColumns: '1.4fr 1fr', gap: '1.5rem' }}>
        {/* Active Users Table */}
        <Card>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
            <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#ffffff' }}>
              Most Active Contributors
            </h3>
            <Button variant="outline" size="sm" onClick={() => onNavigate('users')}>
              All Users <ArrowRight size={14} style={{ marginLeft: '4px' }} />
            </Button>
          </div>

          <div className="table-container">
            <table className="custom-table">
              <thead>
                <tr>
                  <th>User</th>
                  <th>Role</th>
                  <th>Department</th>
                  <th>Decisions Created</th>
                </tr>
              </thead>
              <tbody>
                {activeUsers.slice(0, 6).map((u) => (
                  <tr key={u.user_id}>
                    <td style={{ fontWeight: 600, color: '#ffffff' }}>
                      {u.user_name || `User #${u.user_id}`}
                    </td>
                    <td>
                      <span className="badge badge-role">{u.role || 'User'}</span>
                    </td>
                    <td>{u.department || 'General'}</td>
                    <td style={{ fontWeight: 700, color: '#60a5fa' }}>
                      {u.decision_count ?? 0}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>

        {/* Recent System Activity */}
        <Card>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.25rem' }}>
            <Activity size={18} color="#06b6d4" />
            <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#ffffff' }}>
              System Event Stream
            </h3>
          </div>

          {!metrics?.recent_activities || metrics.recent_activities.length === 0 ? (
            <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>
              No system activity events recorded yet.
            </p>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
              {metrics.recent_activities.slice(0, 7).map((act) => (
                <div
                  key={act.id}
                  style={{
                    padding: '0.75rem',
                    background: 'rgba(255, 255, 255, 0.02)',
                    borderRadius: 'var(--radius-md)',
                    border: '1px solid var(--border-subtle)',
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.25rem' }}>
                    <span style={{ fontWeight: 600, fontSize: '0.85rem', color: '#38bdf8' }}>
                      {act.action}
                    </span>
                    <span style={{ fontSize: '0.725rem', color: 'var(--text-muted)' }}>
                      {new Date(act.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </span>
                  </div>
                  <p style={{ fontSize: '0.825rem', color: 'var(--text-secondary)' }}>
                    {act.details?.description || `Event on ${act.entity_type}`}
                  </p>
                </div>
              ))}
            </div>
          )}
        </Card>
      </div>
    </div>
  );
};
