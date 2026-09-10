import React, { useState, useEffect } from 'react';
import { dashboardService } from '../../api/dashboardService';
import { Card } from '../../components/common/Card';
import { Button } from '../../components/common/Button';
import { StatusBadge } from '../../components/common/Badge';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import { EmptyState } from '../../components/common/EmptyState';
import { useToast } from '../../context/ToastContext';
import {
  FileText,
  Clock,
  CheckCircle,
  AlertCircle,
  PlusCircle,
  Activity,
  ArrowRight,
} from 'lucide-react';

export const EmployeeDashboard = ({ onNavigate }) => {
  const [metrics, setMetrics] = useState(null);
  const [recentDecisions, setRecentDecisions] = useState([]);
  const [loading, setLoading] = useState(true);
  const { error } = useToast();

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [dashData, decisionsData] = await Promise.all([
          dashboardService.getEmployeeDashboard(),
          dashboardService.getEmployeeDecisions(),
        ]);
        setMetrics(dashData);
        setRecentDecisions(decisionsData || []);
      } catch (err) {
        error(err.message || 'Failed to load employee dashboard data');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) return <LoadingSpinner message="Loading your dashboard..." />;

  return (
    <div>
      {/* Welcome Banner */}
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
            Employee Workspace
          </h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem' }}>
            Track your proposals, active drafts, and recent decision workflows.
          </p>
        </div>
        <Button
          variant="primary"
          icon={PlusCircle}
          onClick={() => onNavigate('create-decision')}
        >
          Create New Decision
        </Button>
      </div>

      {/* Metrics Stat Grid */}
      <div className="stat-grid">
        <Card className="stat-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span className="stat-title">Total Decisions</span>
            <FileText size={20} color="#3b82f6" />
          </div>
          <span className="stat-value">{metrics?.total_decisions ?? 0}</span>
          <span className="stat-desc">Proposals initiated by you</span>
        </Card>

        <Card className="stat-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span className="stat-title">Drafts</span>
            <Clock size={20} color="#9ca3af" />
          </div>
          <span className="stat-value">{metrics?.draft_decisions ?? 0}</span>
          <span className="stat-desc">Awaiting submission for review</span>
        </Card>

        <Card className="stat-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span className="stat-title">Under Review</span>
            <Clock size={20} color="#fbbf24" />
          </div>
          <span className="stat-value">{metrics?.under_review ?? 0}</span>
          <span className="stat-desc">Currently in evaluation pipeline</span>
        </Card>

        <Card className="stat-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span className="stat-title">Approved</span>
            <CheckCircle size={20} color="#34d399" />
          </div>
          <span className="stat-value" style={{ color: '#34d399' }}>
            {metrics?.approved_decisions ?? 0}
          </span>
          <span className="stat-desc">Fully ratified decisions</span>
        </Card>
      </div>

      {/* Main Content Sections: Recent Decisions & Activity */}
      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '1.5rem' }}>
        {/* Recent Decisions Table */}
        <Card>
          <div
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              marginBottom: '1.25rem',
            }}
          >
            <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#ffffff' }}>
              My Decisions
            </h3>
            <Button
              variant="outline"
              size="sm"
              onClick={() => onNavigate('decisions')}
            >
              View All <ArrowRight size={14} style={{ marginLeft: '4px' }} />
            </Button>
          </div>

          {recentDecisions.length === 0 ? (
            <EmptyState
              title="No decisions yet"
              description="You haven't drafted any decision records yet. Start by creating one."
              actionLabel="Create Decision"
              onAction={() => onNavigate('create-decision')}
            />
          ) : (
            <div className="table-container">
              <table className="custom-table">
                <thead>
                  <tr>
                    <th>Title</th>
                    <th>Category</th>
                    <th>Status</th>
                    <th>Date</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {recentDecisions.slice(0, 5).map((dec) => (
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
                          variant="outline"
                          size="sm"
                          onClick={() => onNavigate('decision-detail', { id: dec.id })}
                        >
                          View
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Card>

        {/* Recent Activities Panel */}
        <Card>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.25rem' }}>
            <Activity size={18} color="#3b82f6" />
            <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#ffffff' }}>
              Recent Activity
            </h3>
          </div>

          {!metrics?.recent_activities || metrics.recent_activities.length === 0 ? (
            <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>
              No recent activities recorded yet.
            </p>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
              {metrics.recent_activities.slice(0, 6).map((act) => (
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
                    <span style={{ fontWeight: 600, fontSize: '0.85rem', color: '#60a5fa' }}>
                      {act.action}
                    </span>
                    <span style={{ fontSize: '0.725rem', color: 'var(--text-muted)' }}>
                      {new Date(act.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </span>
                  </div>
                  <p style={{ fontSize: '0.825rem', color: 'var(--text-secondary)' }}>
                    {act.details?.description || `${act.action} on ${act.entity_type}`}
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
