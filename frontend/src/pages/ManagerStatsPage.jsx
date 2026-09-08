import React, { useEffect, useState } from 'react';
import { BarChart3, RefreshCw } from 'lucide-react';
import apiClient from '../api/client';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import Button from '../components/common/Button';
import Badge from '../components/common/Badge';
import Table from '../components/common/Table';
import Alert from '../components/common/Alert';
import LoadingSpinner from '../components/common/LoadingSpinner';

export const ManagerStatsPage = () => {
  const { isAdmin } = useAuth();
  const toast = useToast();
  const [stats, setStats] = useState(null);
  const [activity, setActivity] = useState([]);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const load = async () => {
    setLoading(true);
    try {
      const requests = [apiClient.get('/dashboard/manager/statistics')];
      if (isAdmin) requests.push(apiClient.get('/dashboard/admin/analytics'), apiClient.get('/dashboard/admin/user-activity'));
      const responses = await Promise.all(requests);
      setStats(responses[0].data);
      if (isAdmin) { setActivity(responses[1].data?.user_stats?.by_role || []); setUsers(responses[2].data?.users || []); }
    } catch (error) { toast.error(error.formattedMessage || 'Unable to load statistics'); }
    finally { setLoading(false); }
  };
  useEffect(() => { load(); }, [isAdmin]);
  if (loading) return <LoadingSpinner size="large" text="Loading statistics..." />;
  const cards = [['Total', stats?.total], ['Draft', stats?.draft], ['Under Review', stats?.under_review], ['Approved', stats?.approved], ['Rejected', stats?.rejected], ['Archived', stats?.archived]];
  return <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}><div style={{ display: 'flex', justifyContent: 'space-between' }}><div><h1>Manager statistics</h1><p style={{ color: 'var(--color-ink-muted-48)' }}>Decision volume and status health for {stats?.scope || 'your scope'}.</p></div><Button variant="primary" icon={RefreshCw} onClick={load}>Refresh</Button></div><div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '12px' }}>{cards.map(([label, value]) => <div className="apple-card" key={label}><BarChart3 size={18} color="var(--color-primary)" /><div style={{ fontSize: '28px', fontWeight: 600, marginTop: '12px' }}>{value || 0}</div><div style={{ color: 'var(--color-ink-muted-48)', fontSize: '13px' }}>{label}</div></div>)}</div><Alert type="info" title="Approval queue">Pending approval workflow is not implemented by the backend yet, so the pending-approvals endpoint is intentionally unavailable.</Alert>{isAdmin && <><div className="apple-card"><h2>Users by role</h2><Table columns={[{ key: 'role', header: 'Role', render: (value) => <Badge variant="role">{value}</Badge> }, { key: 'count', header: 'Users' }]} data={activity} emptyTitle="No role data" /></div><div className="apple-card"><h2>Recent user activity</h2><Table columns={[{ key: 'full_name', header: 'User' }, { key: 'role', header: 'Role' }, { key: 'total_actions', header: 'Actions' }, { key: 'last_active', header: 'Last active' }]} data={users} emptyTitle="No activity data" /></div></>}</div>;
};
export default ManagerStatsPage;
