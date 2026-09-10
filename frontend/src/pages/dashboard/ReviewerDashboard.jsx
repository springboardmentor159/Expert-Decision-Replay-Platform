import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { dashboardService } from '../../services/dashboardService';
import { StatusBadge } from '../../components/common/StatusBadge';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import { EmptyState } from '../../components/common/EmptyState';
import { useAuth } from '../../context/AuthContext';
import {
  CheckSquare,
  Clock,
  CheckCircle2,
  XCircle,
  FileText,
  ArrowRight,
  ShieldAlert,
} from 'lucide-react';

export const ReviewerDashboard = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState(null);
  const [pendingReviews, setPendingReviews] = useState([]);
  const [recentReviews, setRecentReviews] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchReviewerData = async () => {
      setIsLoading(true);
      setError('');
      try {
        const [statsData, pendingData, recentData] = await Promise.all([
          dashboardService.getReviewerDashboard(),
          dashboardService.getReviewerPendingReviews(),
          dashboardService.getReviewerRecentReviews(),
        ]);
        setStats(statsData);
        setPendingReviews(pendingData);
        setRecentReviews(recentData);
      } catch (err) {
        setError(err.userMessage || 'Failed to load reviewer dashboard');
      } finally {
        setIsLoading(false);
      }
    };

    fetchReviewerData();
  }, []);

  if (isLoading) return <LoadingSpinner message="Loading reviewer dashboard..." />;

  if (error) {
    return (
      <div className="alert alert-error" style={{ margin: '2rem' }}>
        <span>{error}</span>
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      {/* Reviewer Header Banner */}
      <div
        style={{
          background: 'linear-gradient(135deg, #ecfdf5 0%, #f0fdf4 100%)',
          border: '1px solid #a7f3d0',
          borderRadius: 'var(--radius-lg)',
          padding: '2rem',
        }}
      >
        <h2 style={{ fontSize: '1.6rem', color: 'var(--text-primary)', fontWeight: 800 }}>
          Reviewer Governance Hub
        </h2>
        <p className="text-muted" style={{ marginTop: '0.35rem', fontSize: '0.95rem' }}>
          Evaluate peer proposals, review alternatives and risk analysis, and issue approvals or rejections.
        </p>
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
            <FileText size={26} />
          </div>
          <div className="stat-content">
            <span className="stat-value">{stats?.assigned_decisions || 0}</span>
            <span className="stat-label">Assigned Decisions</span>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon-wrapper stat-icon-warning">
            <Clock size={26} />
          </div>
          <div className="stat-content">
            <span className="stat-value">{stats?.pending_reviews || 0}</span>
            <span className="stat-label">Pending Action</span>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon-wrapper stat-icon-success">
            <CheckCircle2 size={26} />
          </div>
          <div className="stat-content">
            <span className="stat-value">{stats?.approved_reviews || 0}</span>
            <span className="stat-label">Approved By Me</span>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon-wrapper stat-icon-danger">
            <XCircle size={26} />
          </div>
          <div className="stat-content">
            <span className="stat-value">{stats?.rejected_reviews || 0}</span>
            <span className="stat-label">Rejected By Me</span>
          </div>
        </div>
      </div>

      {/* Section 1: Pending Reviews (Action Required) */}
      <div className="card">
        <div className="card-header">
          <h3 className="card-title">
            <Clock size={20} color="var(--warning)" />
            Pending Reviews Awaiting Your Decision
          </h3>
          <span className="badge badge-under-review">{pendingReviews.length} Pending</span>
        </div>

        {pendingReviews.length === 0 ? (
          <EmptyState
            icon={CheckCircle2}
            title="All caught up!"
            description="You have no pending decision reviews in your queue."
          />
        ) : (
          <div className="table-container" style={{ border: 'none' }}>
            <table className="table">
              <thead>
                <tr>
                  <th>Decision Title</th>
                  <th>Level</th>
                  <th>Submitted At</th>
                  <th>Requester Remarks</th>
                  <th style={{ textAlign: 'right' }}>Review Action</th>
                </tr>
              </thead>
              <tbody>
                {pendingReviews.map((apprv) => (
                  <tr key={apprv.id}>
                    <td>
                      <div className="table-cell-title">{apprv.decision_title || `Decision #${apprv.decision_id}`}</div>
                    </td>
                    <td>
                      <span className="badge badge-category">Level {apprv.approval_level}</span>
                    </td>
                    <td style={{ fontSize: '0.82rem', color: 'var(--text-dim)' }}>
                      {new Date(apprv.created_at).toLocaleString()}
                    </td>
                    <td style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                      {apprv.comments || 'No submission notes'}
                    </td>
                    <td style={{ textAlign: 'right' }}>
                      <Link to={`/decisions/${apprv.decision_id}`} className="btn btn-primary btn-sm">
                        Review Decision
                        <ArrowRight size={14} />
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Section 2: Recently Completed Reviews */}
      <div className="card">
        <div className="card-header">
          <h3 className="card-title">
            <CheckSquare size={20} color="var(--primary-light)" />
            Recently Completed Reviews
          </h3>
        </div>

        {recentReviews.length === 0 ? (
          <p className="text-muted" style={{ fontSize: '0.88rem', padding: '1rem' }}>
            No past completed reviews found.
          </p>
        ) : (
          <div className="table-container" style={{ border: 'none' }}>
            <table className="table">
              <thead>
                <tr>
                  <th>Decision Title</th>
                  <th>Outcome</th>
                  <th>Completed At</th>
                  <th>Reviewer Comments</th>
                  <th style={{ textAlign: 'right' }}>Details</th>
                </tr>
              </thead>
              <tbody>
                {recentReviews.map((apprv) => (
                  <tr key={apprv.id}>
                    <td>
                      <div className="table-cell-title">{apprv.decision_title || `Decision #${apprv.decision_id}`}</div>
                    </td>
                    <td>
                      <StatusBadge status={apprv.status} />
                    </td>
                    <td style={{ fontSize: '0.82rem', color: 'var(--text-dim)' }}>
                      {apprv.completed_at ? new Date(apprv.completed_at).toLocaleString() : 'N/A'}
                    </td>
                    <td style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                      {apprv.comments || 'No comment provided'}
                    </td>
                    <td style={{ textAlign: 'right' }}>
                      <Link to={`/decisions/${apprv.decision_id}`} className="btn btn-secondary btn-sm">
                        View
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
  );
};
