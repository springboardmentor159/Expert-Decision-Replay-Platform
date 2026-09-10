import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { dashboardService } from '../../services/dashboardService';
import { StatusBadge } from '../../components/common/StatusBadge';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import { EmptyState } from '../../components/common/EmptyState';
import { useAuth } from '../../context/AuthContext';
import {
  Users,
  CheckSquare,
  FileText,
  Clock,
  CheckCircle2,
  XCircle,
  ArrowRight,
  BarChart2,
} from 'lucide-react';

export const ManagerDashboard = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState(null);
  const [teamDecisions, setTeamDecisions] = useState([]);
  const [pendingApprovals, setPendingApprovals] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchManagerData = async () => {
      setIsLoading(true);
      setError('');
      try {
        const [statsData, decisionsData, pendingData] = await Promise.all([
          dashboardService.getManagerDashboard(),
          dashboardService.getManagerTeamDecisions(),
          dashboardService.getManagerPendingApprovals(),
        ]);
        setStats(statsData);
        setTeamDecisions(decisionsData);
        setPendingApprovals(pendingData);
      } catch (err) {
        setError(err.userMessage || 'Failed to load manager dashboard');
      } finally {
        setIsLoading(false);
      }
    };

    fetchManagerData();
  }, []);

  if (isLoading) return <LoadingSpinner message="Loading manager dashboard..." />;

  if (error) {
    return (
      <div className="alert alert-error" style={{ margin: '2rem' }}>
        <span>{error}</span>
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      {/* Manager Header Banner */}
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
            Manager Oversight Dashboard
          </h2>
          <p className="text-muted" style={{ marginTop: '0.35rem', fontSize: '0.95rem' }}>
            Department: <strong style={{ color: 'var(--text-primary)' }}>{user?.department || 'Core Platform'}</strong> •{' '}
            {stats?.team_members_count || 1} team members tracked
          </p>
        </div>
        <Link to="/reports" className="btn btn-secondary">
          <BarChart2 size={18} />
          <span>View Team Analytics</span>
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
            <span className="stat-value">{stats?.team_decisions || 0}</span>
            <span className="stat-label">Team Decisions</span>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon-wrapper stat-icon-warning">
            <Clock size={26} />
          </div>
          <div className="stat-content">
            <span className="stat-value">{stats?.pending_approvals || 0}</span>
            <span className="stat-label">Pending Approvals</span>
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

        <div className="stat-card">
          <div className="stat-icon-wrapper stat-icon-cyan">
            <Users size={26} />
          </div>
          <div className="stat-content">
            <span className="stat-value">{stats?.team_members_count || 1}</span>
            <span className="stat-label">Team Members</span>
          </div>
        </div>
      </div>

      {/* Grid: Pending Team Approvals & Team Decisions */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '1.75rem' }}>
        {/* Pending Approvals */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">
              <CheckSquare size={20} color="var(--warning)" />
              Pending Team Approvals
            </h3>
            <span className="badge badge-under-review">{pendingApprovals.length} Pending</span>
          </div>

          {pendingApprovals.length === 0 ? (
            <EmptyState
              icon={CheckCircle2}
              title="No pending approvals"
              description="Your team has no proposals waiting for review or approval."
            />
          ) : (
            <div className="table-container" style={{ border: 'none' }}>
              <table className="table">
                <thead>
                  <tr>
                    <th>Decision Title</th>
                    <th>Level</th>
                    <th>Assigned Reviewer</th>
                    <th>Submitted Date</th>
                    <th style={{ textAlign: 'right' }}>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {pendingApprovals.map((apprv) => (
                    <tr key={apprv.id}>
                      <td>
                        <div className="table-cell-title">{apprv.decision_title || `Decision #${apprv.decision_id}`}</div>
                      </td>
                      <td>
                        <span className="badge badge-category">Level {apprv.approval_level}</span>
                      </td>
                      <td>{apprv.reviewer_name || `Reviewer #${apprv.reviewer_id}`}</td>
                      <td style={{ fontSize: '0.82rem', color: 'var(--text-dim)' }}>
                        {new Date(apprv.created_at).toLocaleDateString()}
                      </td>
                      <td style={{ textAlign: 'right' }}>
                        <Link to={`/decisions/${apprv.decision_id}`} className="btn btn-primary btn-sm">
                          Review & Act
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Team Decisions */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">
              <FileText size={20} color="var(--primary-light)" />
              Team Decisions Overview
            </h3>
            <Link to="/decisions" className="btn btn-secondary btn-sm">
              View All
            </Link>
          </div>

          {teamDecisions.length === 0 ? (
            <EmptyState title="No decisions logged" description="No decisions have been logged by this team yet." />
          ) : (
            <div className="table-container" style={{ border: 'none' }}>
              <table className="table">
                <thead>
                  <tr>
                    <th>Decision</th>
                    <th>Category</th>
                    <th>Status</th>
                    <th>Created</th>
                    <th style={{ textAlign: 'right' }}>Details</th>
                  </tr>
                </thead>
                <tbody>
                  {teamDecisions.slice(0, 8).map((dec) => (
                    <tr key={dec.id}>
                      <td>
                        <div className="table-cell-title">{dec.title}</div>
                      </td>
                      <td>
                        <span className="badge badge-category">{dec.category}</span>
                      </td>
                      <td>
                        <StatusBadge status={dec.status} />
                      </td>
                      <td style={{ fontSize: '0.82rem', color: 'var(--text-dim)' }}>
                        {new Date(dec.created_at).toLocaleDateString()}
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
      </div>
    </div>
  );
};
