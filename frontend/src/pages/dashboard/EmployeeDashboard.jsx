import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { dashboardService } from '../../services/dashboardService';
import { StatusBadge } from '../../components/common/StatusBadge';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import { EmptyState } from '../../components/common/EmptyState';
import { useAuth } from '../../context/AuthContext';
import {
  FileText,
  Clock,
  CheckCircle2,
  XCircle,
  PlusCircle,
  ArrowRight,
  Activity,
  FileQuestion,
  Layers,
} from 'lucide-react';

export const EmployeeDashboard = () => {
  const { user } = useAuth();
  const navigate = useNavigate();

  const [stats, setStats] = useState(null);
  const [decisions, setDecisions] = useState([]);
  const [activities, setActivities] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchDashboardData = async () => {
      setIsLoading(true);
      setError('');
      try {
        const [statsData, decisionsData, actsData] = await Promise.all([
          dashboardService.getEmployeeDashboard(),
          dashboardService.getEmployeeDecisions(),
          dashboardService.getEmployeeActivities(10),
        ]);
        setStats(statsData);
        setDecisions(decisionsData);
        setActivities(actsData);
      } catch (err) {
        setError(err.userMessage || 'Failed to load dashboard data');
      } finally {
        setIsLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  if (isLoading) return <LoadingSpinner message="Loading your dashboard..." />;

  if (error) {
    return (
      <div className="alert alert-error" style={{ margin: '2rem' }}>
        <span>{error}</span>
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      {/* Welcome Banner */}
      <div
        style={{
          background: 'linear-gradient(135deg, #ecfdf5 0%, #f0fdf4 100%)',
          border: '1px solid #a7f3d0',
          borderRadius: 'var(--radius-lg)',
          padding: '2rem',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '1.5rem',
        }}
      >
        <div>
          <h2 style={{ fontSize: '1.6rem', color: 'var(--text-primary)', fontWeight: 800 }}>
            Hello, {user?.full_name || 'Colleague'}! 👋
          </h2>
          <p className="text-muted" style={{ marginTop: '0.35rem', fontSize: '0.95rem' }}>
            Welcome to your decision workspace. Propose architecture choices, evaluate alternatives, and track review approvals.
          </p>
        </div>
        <Link to="/decisions/create" className="btn btn-primary btn-lg">
          <PlusCircle size={20} />
          <span>Create Decision</span>
        </Link>
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
          <div className="stat-icon-wrapper stat-icon-primary">
            <FileText size={26} />
          </div>
          <div className="stat-content">
            <span className="stat-value">{stats?.total_decisions || 0}</span>
            <span className="stat-label">My Decisions</span>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon-wrapper stat-icon-cyan">
            <FileQuestion size={26} />
          </div>
          <div className="stat-content">
            <span className="stat-value">{stats?.draft_decisions || 0}</span>
            <span className="stat-label">Drafts</span>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon-wrapper stat-icon-warning">
            <Clock size={26} />
          </div>
          <div className="stat-content">
            <span className="stat-value">{stats?.under_review || 0}</span>
            <span className="stat-label">Under Review</span>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon-wrapper stat-icon-success">
            <CheckCircle2 size={26} />
          </div>
          <div className="stat-content">
            <span className="stat-value">{stats?.approved_decisions || 0}</span>
            <span className="stat-label">Approved</span>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon-wrapper stat-icon-danger">
            <XCircle size={26} />
          </div>
          <div className="stat-content">
            <span className="stat-value">{stats?.rejected_decisions || 0}</span>
            <span className="stat-label">Rejected</span>
          </div>
        </div>
      </div>

      {/* Content Grid: Recent Decisions & Activity Feed */}
      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '1.5rem' }}>
        {/* Decisions Table */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">
              <Layers size={20} color="var(--primary-light)" />
              Recently Created Decisions
            </h3>
            <Link to="/decisions" className="btn btn-secondary btn-sm">
              View All
            </Link>
          </div>

          {decisions.length === 0 ? (
            <EmptyState
              title="No decisions created yet"
              description="Start by creating your first architectural or operational decision."
              actionText="Create Decision"
              onAction={() => navigate('/decisions/create')}
            />
          ) : (
            <div className="table-container" style={{ border: 'none' }}>
              <table className="table">
                <thead>
                  <tr>
                    <th>Title & Category</th>
                    <th>Status</th>
                    <th>Updated</th>
                    <th style={{ textAlign: 'right' }}>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {decisions.slice(0, 5).map((dec) => (
                    <tr key={dec.id}>
                      <td>
                        <div className="table-cell-title">{dec.title}</div>
                        <span className="badge badge-category">{dec.category}</span>
                      </td>
                      <td>
                        <StatusBadge status={dec.status} />
                      </td>
                      <td style={{ fontSize: '0.8rem', color: 'var(--text-dim)' }}>
                        {new Date(dec.updated_at || dec.created_at).toLocaleDateString()}
                      </td>
                      <td style={{ textAlign: 'right' }}>
                        <Link to={`/decisions/${dec.id}`} className="btn btn-outline btn-sm">
                          View Details
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Activity Feed */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">
              <Activity size={20} color="var(--accent-cyan)" />
              Recent Activities
            </h3>
          </div>

          {activities.length === 0 ? (
            <p className="text-muted" style={{ fontSize: '0.88rem', padding: '1rem' }}>
              No recent activity recorded.
            </p>
          ) : (
            <div className="timeline">
              {activities.slice(0, 5).map((act) => (
                <div key={act.id} className="timeline-item">
                  <div className="timeline-dot">
                    <div className="timeline-dot-inner"></div>
                  </div>
                  <div className="timeline-content">
                    <div className="timeline-meta">
                      <span className="timeline-title">{act.action?.replace('_', ' ').toUpperCase()}</span>
                      <span className="timeline-time">
                        {new Date(act.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </span>
                    </div>
                    <p className="timeline-desc">{act.description}</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
