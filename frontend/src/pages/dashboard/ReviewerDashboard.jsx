import React, { useState, useEffect } from 'react';
import { dashboardService } from '../../api/dashboardService';
import { Card } from '../../components/common/Card';
import { Button } from '../../components/common/Button';
import { StatusBadge } from '../../components/common/Badge';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import { EmptyState } from '../../components/common/EmptyState';
import { useToast } from '../../context/ToastContext';
import {
  CheckSquare,
  Clock,
  CheckCircle2,
  FileText,
  ArrowRight,
  ShieldCheck,
} from 'lucide-react';

export const ReviewerDashboard = ({ onNavigate }) => {
  const [metrics, setMetrics] = useState(null);
  const [assigned, setAssigned] = useState([]);
  const [reviewed, setReviewed] = useState([]);
  const [loading, setLoading] = useState(true);
  const { error } = useToast();

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [metricData, assignedData, reviewedData] = await Promise.all([
          dashboardService.getReviewerDashboard(),
          dashboardService.getAssignedReviews(),
          dashboardService.getReviewedDecisions(),
        ]);
        setMetrics(metricData);
        setAssigned(assignedData || []);
        setReviewed(reviewedData || []);
      } catch (err) {
        error(err.message || 'Failed to load reviewer dashboard data');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) return <LoadingSpinner message="Loading reviewer dashboard..." />;

  return (
    <div>
      <div style={{ marginBottom: '2rem' }}>
        <h2 style={{ fontSize: '1.75rem', fontWeight: 800, color: '#ffffff' }}>
          Reviewer Dashboard
        </h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem' }}>
          Evaluate assigned technical proposals, compare alternatives, and submit approval verdicts.
        </p>
      </div>

      {/* Metrics Stat Grid */}
      <div className="stat-grid">
        <Card className="stat-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span className="stat-title">Total Assigned</span>
            <FileText size={20} color="#3b82f6" />
          </div>
          <span className="stat-value">{metrics?.total_assigned ?? 0}</span>
          <span className="stat-desc">All proposals routed to you</span>
        </Card>

        <Card className="stat-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span className="stat-title">Pending Reviews</span>
            <Clock size={20} color="#fbbf24" />
          </div>
          <span className="stat-value" style={{ color: '#fbbf24' }}>
            {metrics?.pending_reviews ?? 0}
          </span>
          <span className="stat-desc">Requires your evaluation</span>
        </Card>

        <Card className="stat-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span className="stat-title">Approved by You</span>
            <CheckCircle2 size={20} color="#34d399" />
          </div>
          <span className="stat-value" style={{ color: '#34d399' }}>
            {metrics?.approved_reviews ?? 0}
          </span>
          <span className="stat-desc">Decisions sanctioned</span>
        </Card>

        <Card className="stat-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span className="stat-title">Rejected by You</span>
            <CheckSquare size={20} color="#f43f5e" />
          </div>
          <span className="stat-value" style={{ color: '#f43f5e' }}>
            {metrics?.rejected_reviews ?? 0}
          </span>
          <span className="stat-desc">Returned for revision</span>
        </Card>
      </div>

      {/* Assigned Reviews & History */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '2rem' }}>
        <Card>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
            <div>
              <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#ffffff' }}>
                Pending Review Queue
              </h3>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
                Decisions currently awaiting your review or sign-off
              </p>
            </div>
          </div>

          {assigned.length === 0 ? (
            <EmptyState
              icon={ShieldCheck}
              title="All caught up!"
              description="You have no pending decision reviews in your queue at this moment."
            />
          ) : (
            <div className="table-container">
              <table className="custom-table">
                <thead>
                  <tr>
                    <th>Decision</th>
                    <th>Category</th>
                    <th>Current Status</th>
                    <th>Submitted Date</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {assigned.map((dec) => (
                    <tr key={dec.id}>
                      <td style={{ fontWeight: 600, color: '#ffffff' }}>{dec.title}</td>
                      <td>{dec.category}</td>
                      <td>
                        <StatusBadge status={dec.status} />
                      </td>
                      <td style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>
                        {new Date(dec.created_at).toLocaleDateString()}
                      </td>
                      <td>
                        <Button
                          variant="primary"
                          size="sm"
                          onClick={() => onNavigate('decision-detail', { id: dec.id, activeTab: 'approvals' })}
                        >
                          Review Now
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Card>

        {/* Recently Reviewed */}
        {reviewed.length > 0 && (
          <Card>
            <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#ffffff', marginBottom: '1rem' }}>
              Recently Processed Reviews
            </h3>
            <div className="table-container">
              <table className="custom-table">
                <thead>
                  <tr>
                    <th>Decision Title</th>
                    <th>Status</th>
                    <th>Updated At</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {reviewed.slice(0, 5).map((dec) => (
                    <tr key={dec.id}>
                      <td style={{ fontWeight: 600, color: '#ffffff' }}>{dec.title}</td>
                      <td>
                        <StatusBadge status={dec.status} />
                      </td>
                      <td style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>
                        {new Date(dec.updated_at).toLocaleDateString()}
                      </td>
                      <td>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => onNavigate('decision-detail', { id: dec.id })}
                        >
                          View Details
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        )}
      </div>
    </div>
  );
};
