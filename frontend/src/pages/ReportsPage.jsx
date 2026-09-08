import React, { useEffect, useState } from 'react';
import { Download, RefreshCw } from 'lucide-react';
import apiClient from '../api/client';
import { useToast } from '../context/ToastContext';
import Button from '../components/common/Button';
import Input from '../components/common/Input';
import Select from '../components/common/Select';
import Table from '../components/common/Table';
import FilterBar from '../components/common/FilterBar';
import Badge from '../components/common/Badge';
import Pagination from '../components/common/Pagination';

const reportTypes = { decisions: 'Decisions', approvals: 'Approvals', teams: 'Teams', audit: 'Audit' };
const statusOptions = {
  decisions: ['', 'Draft', 'Under Review', 'Approved', 'Rejected', 'Archived'],
  approvals: ['', 'pending', 'approved', 'rejected'],
  teams: ['', 'Draft', 'Under Review', 'Approved', 'Rejected', 'Archived'],
};
const auditActionOptions = ['', 'create', 'update', 'delete', 'status_change', 'login', 'logout', 'export', 'approve', 'reject'];
const auditEntityOptions = ['', 'decision', 'alternative', 'comment', 'discussion_thread', 'meeting_note', 'document', 'user', 'auth', 'system'];
const sortOptions = {
  decisions: ['', 'created_date', 'updated_date', 'title'],
  approvals: ['', 'created_date', 'approval_date'],
  teams: ['', 'team_name'],
  audit: ['', 'created_date'],
};
const columnsByType = {
  decisions: [{ key: 'title', header: 'Decision' }, { key: 'category', header: 'Category' }, { key: 'status', header: 'Status', render: (value) => <Badge variant={value}>{value}</Badge> }, { key: 'creator', header: 'Creator' }],
  approvals: [{ key: 'decision_title', header: 'Decision' }, { key: 'reviewer', header: 'Reviewer' }, { key: 'status', header: 'Status' }, { key: 'turnaround_hours', header: 'Turnaround' }],
  teams: [{ key: 'team', header: 'Team' }, { key: 'member_count', header: 'Members' }, { key: 'decision_count', header: 'Decisions' }, { key: 'approval_stats', header: 'Approval stats', render: (value) => value ? `${value.approved || 0} approved / ${value.rejected || 0} rejected` : '-' }],
  audit: [{ key: 'user', header: 'User', render: (value) => value?.full_name || value?.email || value || '-' }, { key: 'action', header: 'Action' }, { key: 'entity_type', header: 'Entity' }, { key: 'description', header: 'Description' }],
};

export const ReportsPage = () => {
  const [type, setType] = useState('decisions');
  const [status, setStatus] = useState('');
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState('');
  const [team, setTeam] = useState('');
  const [action, setAction] = useState('');
  const [entityType, setEntityType] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [sortBy, setSortBy] = useState('');
  const [sortOrder, setSortOrder] = useState('desc');
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [report, setReport] = useState({ items: [], summary: {}, total: 0 });
  const [loading, setLoading] = useState(false);
  const toast = useToast();

  const queryParams = {
    ...(status ? { status } : {}),
    ...(category && type === 'decisions' ? { category } : {}),
    ...(team && type === 'teams' ? { team } : {}),
    ...(action && type === 'audit' ? { action } : {}),
    ...(entityType && type === 'audit' ? { entity_type: entityType } : {}),
    ...(startDate ? { start_date: startDate } : {}),
    ...(endDate ? { end_date: endDate } : {}),
    ...(sortBy ? { sort_by: sortBy, sort_order: sortOrder } : {}),
    page,
    page_size: pageSize,
  };

  const load = async () => {
    setLoading(true);
    try { const response = await apiClient.get(`/reports/${type}`, { params: queryParams }); setReport(response.data?.items ? response.data : { items: response.data || [] }); }
    catch (error) { toast.error(error.formattedMessage || 'Unable to load report'); }
    finally { setLoading(false); }
  };
  useEffect(() => { setPage(1); }, [type, status, category, team, action, entityType, startDate, endDate, sortBy, sortOrder, pageSize]);
  useEffect(() => { load(); }, [type, status, category, team, action, entityType, startDate, endDate, sortBy, sortOrder, page, pageSize]);

  const exportReport = async (format) => {
    try { const response = await apiClient.get(`/reports/${type}/export/${format}`, { params: { ...queryParams, page: undefined, page_size: undefined }, responseType: 'blob' }); const url = URL.createObjectURL(response.data); const anchor = document.createElement('a'); anchor.href = url; anchor.download = `${type}-report.${format === 'excel' ? 'xlsx' : 'pdf'}`; anchor.click(); URL.revokeObjectURL(url); }
    catch (error) { toast.error(error.formattedMessage || 'Export failed'); }
  };

  const filteredItems = (report.items || []).filter((item) => JSON.stringify(item).toLowerCase().includes(search.toLowerCase()));
  return <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
    <div style={{ display: 'flex', justifyContent: 'space-between', gap: '12px', flexWrap: 'wrap' }}><div><h1>Reports & exports</h1><p style={{ color: 'var(--color-ink-muted-48)' }}>Operational views built from the audit and decision APIs.</p></div><div style={{ display: 'flex', gap: '8px' }}><Button variant="pearl" icon={Download} onClick={() => exportReport('pdf')}>PDF</Button><Button variant="pearl" icon={Download} onClick={() => exportReport('excel')}>Excel</Button><Button variant="primary" icon={RefreshCw} onClick={load}>Refresh</Button></div></div>
    <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>{Object.entries(reportTypes).map(([key, label]) => <Button key={key} variant={type === key ? 'primary' : 'pearl'} onClick={() => setType(key)}>{label}</Button>)}</div>
    <div className="apple-card"><FilterBar searchValue={search} onSearchChange={setSearch} searchPlaceholder="Search this report..." filters={[...(statusOptions[type] ? [{ key: 'status', label: 'Status', value: status, options: statusOptions[type], onChange: setStatus }] : []), ...(type === 'audit' ? [{ key: 'action', label: 'Action', value: action, options: auditActionOptions, onChange: setAction }, { key: 'entity_type', label: 'Entity', value: entityType, options: auditEntityOptions, onChange: setEntityType }] : [])]} onReset={() => { setSearch(''); setStatus(''); setCategory(''); setTeam(''); setAction(''); setEntityType(''); setStartDate(''); setEndDate(''); setSortBy(''); setPage(1); }} /><div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginBottom: '20px' }}><Input type="date" value={startDate} onChange={(event) => setStartDate(event.target.value)} aria-label="Start date" /><Input type="date" value={endDate} onChange={(event) => setEndDate(event.target.value)} aria-label="End date" />{type === 'decisions' && <Input placeholder="Category" value={category} onChange={(event) => setCategory(event.target.value)} />}{type === 'teams' && <Input placeholder="Team" value={team} onChange={(event) => setTeam(event.target.value)} />}<Select value={sortBy} onChange={(event) => setSortBy(event.target.value)} options={sortOptions[type]} placeholder="Sort by" /><Button variant="pearl" onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}>{sortOrder === 'asc' ? 'Ascending' : 'Descending'}</Button></div>{report.summary && Object.keys(report.summary).length > 0 && <div style={{ display: 'flex', flexWrap: 'wrap', gap: '12px', marginBottom: '20px' }}>{Object.entries(report.summary).map(([key, value]) => <div key={key} style={{ padding: '10px 14px', background: 'var(--color-surface-pearl)', borderRadius: 'var(--radius-sm)' }}><strong>{String(value ?? 0)}</strong><div style={{ fontSize: '12px', color: 'var(--color-ink-muted-48)' }}>{key.replaceAll('_', ' ')}</div></div>)}</div>}<Table columns={columnsByType[type]} data={filteredItems} loading={loading} emptyTitle={`No ${reportTypes[type].toLowerCase()} found`} /><Pagination currentPage={report.page || page} totalPages={report.pages || 1} totalItems={report.total || 0} pageSize={report.page_size || pageSize} onPageChange={setPage} onPageSizeChange={(value) => { setPageSize(value); setPage(1); }} /></div>
  </div>;
};
export default ReportsPage;
