import React, { useState, useEffect } from 'react';
import {
  FileText,
  Clock,
  CheckCircle2,
  XCircle,
  Users,
  Activity,
  AlertCircle,
  ArrowRight,
  TrendingUp,
  Shield,
  Layers,
  ChevronRight,
  Building,
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { dashboardApi } from '../../api/dashboard';
import { approvalsApi } from '../../api/approvals';
import { organizationsApi } from '../../api/organizations';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import { StatusBadge } from '../../components/common/StatusBadge';

export function DashboardPage({ onSelectDecision, onNavigateCreate, onNavigateReviews }) {
  const { user, role, isEmployee, isReviewer, isManager, isAdmin } = useAuth();
  const [data, setData] = useState(null);
  const [orgName, setOrgName] = useState('');
  const [recentDecisions, setRecentDecisions] = useState([]);
  const [recentActivities, setRecentActivities] = useState([]);
  const [pendingReviews, setPendingReviews] = useState([]);
  const [categoryStats, setCategoryStats] = useState([]);
  const [statusStats, setStatusStats] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadDashboard() {
      setLoading(true);
      setError(null);
      try {
        if (isAdmin) {
          const [adminDash, catStats, statStats, usersAct] = await Promise.all([
            dashboardApi.getAdminDashboard().catch(() => ({})),
            dashboardApi.getAdminCategoryAnalytics().catch(() => ({ categories: [] })),
            dashboardApi.getAdminStatusAnalytics().catch(() => ({ statuses: [] })),
            dashboardApi.getAdminUserActivity().catch(() => ({ active_users: [] })),
          ]);
          setData(adminDash);
          setCategoryStats(catStats.categories || []);
          setStatusStats(statStats.statuses || []);
          setRecentActivities(usersAct.active_users || []);
        } else if (isManager) {
          const [mgrDash, teamDecs, pendingApps] = await Promise.all([
            dashboardApi.getManagerDashboard().catch(() => ({})),
            dashboardApi.getManagerTeamDecisions(1, 6).catch(() => []),
            dashboardApi.getManagerPendingApprovals(1, 6).catch(() => []),
          ]);
          setData(mgrDash);
          setRecentDecisions(teamDecs || []);
          setPendingReviews(pendingApps || []);
        } else if (isReviewer) {
          const [myApprovals] = await Promise.all([
            approvalsApi.getMyApprovals().catch(() => []),
          ]);
          setPendingReviews(myApprovals.filter(a => a.status === 'Pending') || []);
          setData({
            total_assigned: myApprovals.length,
            pending_count: myApprovals.filter(a => a.status === 'Pending').length,
            approved_count: myApprovals.filter(a => a.status === 'Approved').length,
            rejected_count: myApprovals.filter(a => a.status === 'Rejected').length,
          });
          setRecentDecisions(myApprovals);
        } else {
          // Employee
          const [empDash, empDecs, empActs] = await Promise.all([
            dashboardApi.getEmployeeDashboard().catch(() => ({})),
            dashboardApi.getEmployeeDecisions(1, 6).catch(() => []),
            dashboardApi.getEmployeeRecentActivities().catch(() => []),
          ]);
          setData(empDash);
          setRecentDecisions(empDecs || []);
          setRecentActivities(empActs || []);
        }
      } catch (err) {
        setError(err.message || 'Failed to load dashboard data');
      } finally {
        setLoading(false);
      }
    }
    loadDashboard();
  }, [role, isEmployee, isReviewer, isManager, isAdmin]);

  useEffect(() => {
    async function loadOrgName() {
      try {
        const orgs = await organizationsApi.getPublicList();
        if (Array.isArray(orgs)) {
          const matched = orgs.find((o) => o.id === user?.organization_id);
          if (matched) {
            setOrgName(matched.name);
          }
        }
      } catch {
        // ignore
      }
    }
    if (user?.organization_id) {
      loadOrgName();
    }
  }, [user?.organization_id]);

  if (loading) {
    return <LoadingSpinner message="Loading your dashboard analytics..." size="large" />;
  }

  if (error) {
    return (
      <div className="card" style={{ borderColor: 'var(--danger)', background: 'var(--danger-light)' }}>
        <h3 style={{ color: 'var(--danger)', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <AlertCircle size={20} /> Dashboard Error
        </h3>
        <p style={{ marginTop: '0.5rem', color: 'var(--text-primary)' }}>{error}</p>
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      {/* Header Banner */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        background: 'var(--bg-card)',
        padding: '1.75rem 2rem',
        borderRadius: '14px',
        border: '1px solid var(--border-color)',
        boxShadow: 'var(--shadow-sm)',
      }}>
        <div>
          <h1 style={{ fontSize: '1.75rem', marginBottom: '0.35rem' }}>
            {role} Dashboard
          </h1>
          <div style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap', marginTop: '4px' }}>
            <span>Welcome back, <strong style={{ color: 'var(--text-primary)' }}>{user?.full_name}</strong>.</span>
            {orgName && (
              <span style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '5px',
                background: 'var(--bg-hover)',
                border: '1px solid var(--border-color)',
                padding: '2px 10px',
                borderRadius: '20px',
                fontSize: '0.8rem',
                color: 'var(--text-primary)',
                fontWeight: 500,
              }}>
                <Building size={13} style={{ color: 'var(--primary)' }} />
                {orgName}
              </span>
            )}
            <span>Here is your governance overview.</span>
          </div>
        </div>
        {isEmployee && (
          <button onClick={onNavigateCreate} className="btn btn-primary">
            + Create New Decision
          </button>
        )}
      </div>

      {/* KPI Cards Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1.25rem' }}>
        {isAdmin ? (
          <>
            <MetricCard title="Total Users" value={data?.total_users ?? 0} icon={Users} color="var(--primary)" />
            <MetricCard title="Total Decisions" value={data?.total_decisions ?? 0} icon={FileText} color="var(--purple)" />
            <MetricCard title="Pending Approvals" value={data?.pending_approvals ?? 0} icon={Clock} color="var(--warning)" />
            <MetricCard title="Approved Decisions" value={data?.approved_decisions ?? 0} icon={CheckCircle2} color="var(--success)" />
          </>
        ) : isManager ? (
          <>
            <MetricCard title="Team Decisions" value={data?.total_decisions ?? 0} icon={FileText} color="var(--primary)" />
            <MetricCard title="Pending Approvals" value={data?.pending_approvals ?? 0} icon={Clock} color="var(--warning)" />
            <MetricCard title="Under Review" value={data?.under_review ?? 0} icon={Activity} color="var(--info)" />
            <MetricCard title="Approved Decisions" value={data?.approved_decisions ?? 0} icon={CheckCircle2} color="var(--success)" />
          </>
        ) : isReviewer ? (
          <>
            <MetricCard title="Assigned Decisions" value={data?.total_assigned ?? 0} icon={Layers} color="var(--primary)" />
            <MetricCard title="Pending Reviews" value={data?.pending_count ?? 0} icon={Clock} color="var(--warning)" />
            <MetricCard title="Approved by Me" value={data?.approved_count ?? 0} icon={CheckCircle2} color="var(--success)" />
            <MetricCard title="Rejected by Me" value={data?.rejected_count ?? 0} icon={XCircle} color="var(--danger)" />
          </>
        ) : (
          <>
            <MetricCard title="My Decisions" value={data?.total_decisions ?? 0} icon={FileText} color="var(--primary)" />
            <MetricCard title="Draft Decisions" value={data?.draft_decisions ?? 0} icon={Clock} color="var(--warning)" />
            <MetricCard title="Under Review" value={data?.under_review ?? 0} icon={Activity} color="var(--info)" />
            <MetricCard title="Approved Decisions" value={data?.approved_decisions ?? 0} icon={CheckCircle2} color="var(--success)" />
          </>
        )}
      </div>

      {/* Reviewer / Manager Pending Review Queue */}
      {(isReviewer || isManager) && pendingReviews.length > 0 && (
        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
            <h2 style={{ fontSize: '1.2rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Clock size={20} style={{ color: 'var(--warning)' }} /> Pending Review Requests ({pendingReviews.length})
            </h2>
          </div>
          <div className="table-container">
            <table className="table">
              <thead>
                <tr>
                  <th>Decision ID</th>
                  <th>Reviewer / Target</th>
                  <th>Current Status</th>
                  <th>Created At</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {pendingReviews.map((rev) => (
                  <tr key={rev.id}>
                    <td>
                      <span style={{ fontWeight: 600, color: 'var(--primary)' }}>
                        #{rev.decision_id}
                      </span>
                    </td>
                    <td>{rev.reviewer?.full_name || `Reviewer ID: ${rev.reviewer_id}`}</td>
                    <td><StatusBadge status={rev.status} /></td>
                    <td>{new Date(rev.created_at).toLocaleDateString()}</td>
                    <td>
                      <button
                        onClick={() => onSelectDecision(rev.decision_id)}
                        className="btn btn-primary btn-sm"
                      >
                        Inspect & Review <ArrowRight size={14} />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Admin Analytics Sections */}
      {isAdmin && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
          <div className="card">
            <h2 style={{ fontSize: '1.15rem', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <TrendingUp size={18} style={{ color: 'var(--primary)' }} /> Decisions by Status
            </h2>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              {statusStats.length === 0 ? (
                <div style={{ color: 'var(--text-muted)' }}>No decision status data available.</div>
              ) : (
                statusStats.map((st) => (
                  <div key={st.status} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <StatusBadge status={st.status} />
                    <span style={{ fontWeight: 600, fontSize: '0.95rem' }}>{st.count} decisions</span>
                  </div>
                ))
              )}
            </div>
          </div>

          <div className="card">
            <h2 style={{ fontSize: '1.15rem', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Layers size={18} style={{ color: 'var(--purple)' }} /> Decisions by Category
            </h2>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              {categoryStats.length === 0 ? (
                <div style={{ color: 'var(--text-muted)' }}>No category data available.</div>
              ) : (
                categoryStats.map((cat) => (
                  <div key={cat.category} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <span style={{ fontWeight: 500 }}>{cat.category || 'General'}</span>
                    <span style={{ fontWeight: 600, fontSize: '0.95rem' }}>{cat.count}</span>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      )}

      {/* Recent Decisions Table for Employee / Manager */}
      {!isAdmin && recentDecisions.length > 0 && (
        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
            <h2 style={{ fontSize: '1.2rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <FileText size={20} style={{ color: 'var(--primary)' }} />
              {isManager ? 'Recent Team Decisions' : 'Recently Created Decisions'}
            </h2>
          </div>
          <div className="table-container">
            <table className="table">
              <thead>
                <tr>
                  <th>Title</th>
                  <th>Category</th>
                  <th>Status</th>
                  <th>Created Date</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {recentDecisions.map((dec) => (
                  <tr key={dec.id}>
                    <td>
                      <div style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{dec.title}</div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>ID: #{dec.id}</div>
                    </td>
                    <td>
                      <span className="badge badge-role">{dec.category || 'General'}</span>
                    </td>
                    <td><StatusBadge status={dec.status} /></td>
                    <td>{new Date(dec.created_at).toLocaleDateString()}</td>
                    <td>
                      <button
                        onClick={() => onSelectDecision(dec.id)}
                        className="btn btn-secondary btn-sm"
                      >
                        View Details <ChevronRight size={14} />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Recent Activities Section for Employee */}
      {isEmployee && recentActivities.length > 0 && (
        <div className="card">
          <h2 style={{ fontSize: '1.2rem', marginBottom: '1.25rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Activity size={20} style={{ color: 'var(--primary)' }} /> Recent Activity Trail
          </h2>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {recentActivities.map((act) => (
              <div key={act.id} style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: '0.75rem 1rem',
                background: 'var(--bg-hover)',
                borderRadius: '8px',
                border: '1px solid var(--border-color)',
              }}>
                <div>
                  <div style={{ fontWeight: 500, fontSize: '0.9rem' }}>{act.description}</div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                    Action: <strong>{act.action}</strong> • Entity: {act.entity_type} #{act.entity_id}
                  </div>
                </div>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                  {new Date(act.created_at).toLocaleString()}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function MetricCard({ title, value, icon: Icon, color }) {
  return (
    <div className="card" style={{ display: 'flex', alignItems: 'center', gap: '1.25rem' }}>
      <div style={{
        width: '48px',
        height: '48px',
        borderRadius: '12px',
        background: `rgba(${color === 'var(--primary)' ? '59, 130, 246' : color === 'var(--success)' ? '16, 185, 129' : color === 'var(--warning)' ? '245, 158, 11' : color === 'var(--danger)' ? '239, 68, 68' : '139, 92, 246'}, 0.15)`,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        color: color,
        flexShrink: 0,
      }}>
        <Icon size={24} />
      </div>
      <div>
        <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', fontWeight: 500, textTransform: 'uppercase' }}>
          {title}
        </div>
        <div style={{ fontSize: '1.75rem', fontWeight: 700, fontFamily: 'Outfit', color: 'var(--text-primary)' }}>
          {value}
        </div>
      </div>
    </div>
  );
}
