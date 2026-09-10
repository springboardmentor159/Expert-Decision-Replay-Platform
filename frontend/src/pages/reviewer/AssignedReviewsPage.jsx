import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { dashboardService } from '../../services/dashboardService';
import { StatusBadge } from '../../components/common/StatusBadge';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import { EmptyState } from '../../components/common/EmptyState';
import { CheckSquare, Clock, ArrowRight, CheckCircle2 } from 'lucide-react';

export const AssignedReviewsPage = () => {
  const [pendingReviews, setPendingReviews] = useState([]);
  const [recentReviews, setRecentReviews] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const loadReviews = async () => {
      setIsLoading(true);
      setError('');
      try {
        const [pending, recent] = await Promise.all([
          dashboardService.getReviewerPendingReviews(),
          dashboardService.getReviewerRecentReviews(),
        ]);
        setPendingReviews(pending);
        setRecentReviews(recent);
      } catch (err) {
        setError(err.userMessage || 'Failed to load assigned reviews');
      } finally {
        setIsLoading(false);
      }
    };
    loadReviews();
  }, []);

  if (isLoading) return <LoadingSpinner message="Loading assigned reviews..." />;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      <div>
        <h1 className="page-title">
          <CheckSquare size={28} />
          Assigned Reviews & Tasks
        </h1>
        <p className="page-description">
          Review, analyze alternatives, and issue governance verdicts for pending proposals assigned to you.
        </p>
      </div>

      {error && (
        <div className="alert alert-error">
          <span>{error}</span>
        </div>
      )}

      {/* Pending Reviews Queue */}
      <div className="card">
        <div className="card-header">
          <h3 className="card-title">
            <Clock size={20} color="var(--warning)" />
            Pending Reviews Awaiting Action ({pendingReviews.length})
          </h3>
        </div>

        {pendingReviews.length === 0 ? (
          <EmptyState
            icon={CheckCircle2}
            title="No reviews pending"
            description="You do not have any decision proposals waiting for review."
          />
        ) : (
          <div className="table-container" style={{ border: 'none' }}>
            <table className="table">
              <thead>
                <tr>
                  <th>Decision Title</th>
                  <th>Level</th>
                  <th>Submitted At</th>
                  <th>Requester Notes</th>
                  <th style={{ textAlign: 'right' }}>Action</th>
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
                      {apprv.comments || 'No comment provided'}
                    </td>
                    <td style={{ textAlign: 'right' }}>
                      <Link to={`/decisions/${apprv.decision_id}`} className="btn btn-primary btn-sm">
                        Review Now <ArrowRight size={14} />
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Completed Reviews Log */}
      <div className="card">
        <div className="card-header">
          <h3 className="card-title">
            <CheckCircle2 size={20} color="var(--success)" />
            Previously Completed Reviews ({recentReviews.length})
          </h3>
        </div>

        {recentReviews.length === 0 ? (
          <p className="text-muted" style={{ padding: '1rem' }}>No past reviews found.</p>
        ) : (
          <div className="table-container" style={{ border: 'none' }}>
            <table className="table">
              <thead>
                <tr>
                  <th>Decision Title</th>
                  <th>Verdict</th>
                  <th>Completed Date</th>
                  <th>Reviewer Remarks</th>
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
                      {apprv.completed_at ? new Date(apprv.completed_at).toLocaleString() : '—'}
                    </td>
                    <td style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                      {apprv.comments || '—'}
                    </td>
                    <td style={{ textAlign: 'right' }}>
                      <Link to={`/decisions/${apprv.decision_id}`} className="btn btn-secondary btn-sm">
                        View Decision
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
