import React, { useCallback, useEffect, useState } from 'react';
import apiClient from '../api/client';
import { useToast } from '../context/ToastContext';
import Table from '../components/common/Table';
import FilterBar from '../components/common/FilterBar';
import Button from '../components/common/Button';

export const AdminAuditPage = () => {
  const [items, setItems] = useState([]); const [action, setAction] = useState(''); const [entityType, setEntityType] = useState(''); const [loading, setLoading] = useState(true); const toast = useToast();
  const load = useCallback(async () => { setLoading(true); try { const response = await apiClient.get('/audit-logs', { params: { page: 1, page_size: 50, ...(action ? { action } : {}), ...(entityType ? { entity_type: entityType } : {}) } }); setItems(response.data?.items || []); } catch (error) { toast.error(error.formattedMessage || 'Unable to load audit trail'); } finally { setLoading(false); } }, [action, entityType, toast]);
  useEffect(() => { load(); }, [load]);
  return <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}><div style={{ display: 'flex', justifyContent: 'space-between' }}><div><h1>System audit trail</h1><p style={{ color: 'var(--color-ink-muted-48)' }}>Immutable record of decisions and account actions.</p></div><Button variant="primary" onClick={load}>Refresh</Button></div><div className="apple-card"><FilterBar searchValue={action} onSearchChange={setAction} searchPlaceholder="Filter by action..." filters={[{ key: 'entity_type', label: 'Entity type', value: entityType, options: ['', 'decision', 'user', 'auth'], onChange: setEntityType }]} onReset={() => { setAction(''); setEntityType(''); }} actionButton={<Button variant="pearl" onClick={load}>Apply</Button>} /><Table columns={[{ key: 'created_at', header: 'When' }, { key: 'action', header: 'Action' }, { key: 'entity_type', header: 'Entity' }, { key: 'entity_id', header: 'ID' }, { key: 'description', header: 'Description' }, { key: 'ip_address', header: 'IP' }]} data={items} loading={loading} emptyTitle="No audit events" /></div></div>;
};
export default AdminAuditPage;
