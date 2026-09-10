import React, { useState, useEffect } from 'react';
import { dashboardService } from '../../api/dashboardService';
import { Card } from '../../components/common/Card';
import { Button } from '../../components/common/Button';
import { StatusBadge } from '../../components/common/Badge';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import { EmptyState } from '../../components/common/EmptyState';
import { useToast } from '../../context/ToastContext';
import {
  Users,
  Clock,
  CheckCircle,
  XCircle,
  BarChart2,
  FileSpreadsheet,
  ArrowRight,
} from 'lucide-react';

export const ManagerDashboard = ({ onNavigate }) => {
  const [metrics, setMetrics] = useState(null);
  const [teamDecisions, setTeamDecisions] = useState([]);
  const [pendingApprovals, setPendingApprovals] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const { error } = useToast();

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [dashData, teamData, pendingData, statsData] = await Promise.all([
          dashboardService.getManagerDashboard(),
          dashboardService.getTeamDecisions(),
          dashboardService.getPendingApprovals(),
          dashboardService.getManagerStatistics(),
        ]);
        setMetrics(dashData);
        setTeamDecisions(teamData || []);
        setPendingApprovals(pendingData || []);
        setStats(statsData);
      } catch (err) {
        error(err.message || 'Failed to load manager dashboard data');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) return <LoadingSpinner message="Loading team decision metrics..." />;

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
            Managerial Oversight & Analytics
          </h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem' }}>
            Monitor team velocity, authorize pending decisions, and review department statistics.
          </p>
        </div>
        <div style={{ display: 'flex', gap: '0.75rem' }}>
          <Button
            variant="outline"
            icon={FileSpreadsheet}
            onClick={() => onNavigate('reports')}
          >
            Team Reports
          </Button>
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="stat-grid">
        <Card className="stat-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span className="stat-title">Team Decisions</span>
            <Users size={20} color="#3b82f6" />
          </div>
          <span className="stat-value">{metrics?.total_team_decisions ?? 0}</span>
          <span className="stat-desc">Originated within department</span>
        </Card>

        <Card className="stat-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span className="stat-title">Pending Approvals</span>
            <Clock size={20} color="#fbbf24" />
          </div>
          <span className="stat-value" style={{ color: '#fbbf24' }}>
            {metrics?.pending_approvals ?? 0}
          </span>
          <span className="stat-desc">Awaiting manager authorization</span>
        </Card>

        <Card className="stat-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span className="stat-title">Approved Decisions</span>
            <CheckCircle size={20} color="#34d399" />
          </div>
          <span className="stat-value" style={{ color: '#34d399' }}>
            {metrics?.approved_decisions ?? 0}
          </span>
          <span className="stat-desc">Completed and ratified</span>
        </Card>

        <Card className="stat-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span className="stat-title">Rejected Decisions</span>
            <XCircle size={20} color="#f43f5e" />
          </div>
          <span className="stat-value" style={{ color: '#f43f5e' }}>
            {metrics?.rejected_decisions ?? 0}
          </span>
          <span className="stat-desc">Declined proposals</span>
        </Card>
      </div>

      {/* Pending Approvals Section */}
      <Card style={{ marginBottom: '2rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
          <div>
            <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#ffffff' }}>
              High-Priority Pending Approvals
            </h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
              Authorizations awaiting managerial review or escalation
            </p>
          </div>
        </div>

        {pendingApprovals.length === 0 ? (
          <EmptyState
            title="No pending approvals"
            description="All team proposals have been reviewed or are in active drafting."
          />
        ) : (
          <div className="table-container">
            <table className="custom-table">
              <thead>
                <tr>
                  <th>Decision ID</th>
                  <th>Approval Level</th>
                  <th>Status</th>
                  <th>Created Date</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {pendingApprovals.map((appr) => (
                  <tr key={appr.id}>
                    <td style={{ fontWeight: 600, color: '#ffffff' }}>
                      Decision #{appr.decision_id}
                    </td>
                    <td>Level {appr.approval_level}</td>
                    <td>
                      <StatusBadge status={appr.status} />
                    </td>
                    <td style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>
                      {new Date(appr.created_at).toLocaleDateString()}
                    </td>
                    <td>
                      <Button
                        variant="primary"
                        size="sm"
                        onClick={() => onNavigate('decision-detail', { id: appr.decision_id, activeTab: 'approvals' })}
                      >
                        Review & Authorize
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>

      {/* Team Decisions Table */}
      <Card>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
          <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#ffffff' }}>
            Team Decision Portfolio
          </h3>
          <Button variant="outline" size="sm" onClick={() => onNavigate('decisions')}>
            View All <ArrowRight size={14} style={{ marginLeft: '4px' }} />
          </Button>
        </div>

        <div className="table-container">
          <table className="custom-table">
            <thead>
              <tr>
                <th>Title</th>
                <th>Category</th>
                <th>Status</th>
                <th>Last Updated</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {teamDecisions.slice(0, 6).map((dec) => (
                <tr key={dec.id}>
                  <td style={{ fontWeight: 600, color: '#ffffff' }}>{dec.title}</td>
                  <td>{dec.category}</td>
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
                      Inspect
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
};
