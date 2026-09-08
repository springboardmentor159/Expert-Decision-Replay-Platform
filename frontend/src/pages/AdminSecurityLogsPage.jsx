import React, { useEffect, useState } from 'react';
import apiClient from '../api/client';
import { useToast } from '../context/ToastContext';
import Button from '../components/common/Button';
import Table from '../components/common/Table';
import Badge from '../components/common/Badge';

export const AdminSecurityLogsPage = () => {
  const [security, setSecurity] = useState([]); const [access, setAccess] = useState([]); const [loading, setLoading] = useState(true); const toast = useToast();
  const load = async () => { setLoading(true); try { const [securityResponse, accessResponse] = await Promise.all([apiClient.get('/security/logs', { params: { offset: 0, limit: 100 } }), apiClient.get('/access/logs', { params: { offset: 0, limit: 100 } })]); setSecurity(securityResponse.data || []); setAccess(accessResponse.data || []); } catch (error) { toast.error(error.formattedMessage || 'Unable to load security logs'); } finally { setLoading(false); } };
  useEffect(() => { load(); }, []);
  return <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}><div style={{ display: 'flex', justifyContent: 'space-between' }}><div><h1>Security & access logs</h1><p style={{ color: 'var(--color-ink-muted-48)' }}>Authentication events and API access records.</p></div><Button variant="primary" onClick={load}>Refresh</Button></div><div className="apple-card"><h2>Security events</h2><Table columns={[{ key: 'created_at', header: 'When' }, { key: 'event_type', header: 'Event', render: (value) => <Badge variant="role">{value}</Badge> }, { key: 'user_id', header: 'User' }, { key: 'description', header: 'Description' }, { key: 'ip_address', header: 'IP' }]} data={security} loading={loading} emptyTitle="No security events" /></div><div className="apple-card"><h2>API access</h2><Table columns={[{ key: 'created_at', header: 'When' }, { key: 'method', header: 'Method' }, { key: 'path', header: 'Path' }, { key: 'status_code', header: 'Status' }, { key: 'response_time_ms', header: 'Response ms' }]} data={access} loading={loading} emptyTitle="No access events" /></div></div>;
};
export default AdminSecurityLogsPage;
