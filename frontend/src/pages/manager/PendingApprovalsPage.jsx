import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { dashboardService } from '../../services/dashboardService';
import { StatusBadge } from '../../components/common/StatusBadge';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import { EmptyState } from '../../components/common/EmptyState';
import { CheckSquare, Clock, ArrowRight, CheckCircle2 } from 'lucide-react';

export const PendingApprovalsPage = () => {
  const [approvals, setApprovals] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchApprovals = async () => {
      setIsLoading(true);
      try {
        const data = await dashboardService.getManagerPendingApprovals();
        setApprovals(data);
      } catch (err) {
        setError(err.userMessage || 'Failed to load team pending approvals');
      } finally {
        setIsLoading(false);
      }
    };
    fetchApprovals();
  }, []);

  if (isLoading) return <LoadingSpinner message="Loading pending approvals..." />;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      <div>
        <h1 className="page-title">
          <CheckSquare size={28} />
          Team Pending Approvals
        </h1>
        <p className="page-description">
          Review proposals submitted by your team members and manage governance sign-offs.
        </p>
      </div>

      {error && (
        <div className="alert alert-error">
          <span>{error}</span>
        </div>
      )}

      <div className="card">
        <div className="card-header">
          <h3 className="card-title">
            <Clock size={20} color="var(--warning)" />
            Pending Action Queue ({approvals.length})
          </h3>
        </div>

        {approvals.length === 0 ? (
          <EmptyState
            icon={CheckCircle2}
            title="Queue is empty"
            description="There are currently no proposals awaiting approval for your team."
          />
        ) : (
          <div className="table-container" style={{ border: 'none' }}>
            <table className="table">
              <thead>
                <tr>
                  <th>Decision Title</th>
                  <th>Level</th>
                  <th>Assigned Reviewer</th>
                  <th>Date Submitted</th>
                  <th>Requester Notes</th>
                  <th style={{ textAlign: 'right' }}>Action</th>
                </tr>
              </thead>
              <tbody>
                {approvals.map((apprv) => (
                  <tr key={apprv.id}>
                    <td>
                      <div className="table-cell-title">{apprv.decision_title || `Decision #${apprv.decision_id}`}</div>
                    </td>
                    <td>
                      <span className="badge badge-category">Level {apprv.approval_level}</span>
                    </td>
                    <td>{apprv.reviewer_name || `Reviewer #${apprv.reviewer_id}`}</td>
                    <td style={{ fontSize: '0.82rem', color: 'var(--text-dim)' }}>
                      {new Date(apprv.created_at).toLocaleString()}
                    </td>
                    <td style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                      {apprv.comments || '—'}
                    </td>
                    <td style={{ textAlign: 'right' }}>
                      <Link to={`/decisions/${apprv.decision_id}`} className="btn btn-primary btn-sm">
                        Review & Act <ArrowRight size={14} />
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
