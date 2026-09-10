import React, { useState, useEffect } from 'react';
import { auditService } from '../../services/auditService';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import { EmptyState } from '../../components/common/EmptyState';
import { Modal } from '../../components/common/Modal';
import { useAuth } from '../../context/AuthContext';
import { ShieldCheck, Filter, Search, Eye, ArrowLeft, ArrowRight, Activity, Calendar } from 'lucide-react';

const ACTIONS = [
  'ALL',
  'CREATE',
  'UPDATE',
  'DELETE',
  'APPROVE',
  'REJECT',
  'SUBMIT',
  'LOGIN',
  'VIEW',
];

const ENTITY_TYPES = [
  'ALL',
  'Decision',
  'Alternative',
  'Comment',
  'DiscussionThread',
  'MeetingNote',
  'Approval',
  'User',
  'Tag',
];

export const AuditLogsPage = () => {
  const { isAdmin } = useAuth();

  const [logs, setLogs] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(15);

  const [actionFilter, setActionFilter] = useState('ALL');
  const [entityFilter, setEntityFilter] = useState('ALL');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');

  const [selectedLog, setSelectedLog] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchAuditLogs = async () => {
    setIsLoading(true);
    setError('');
    try {
      const params = {
        page,
        page_size: pageSize,
      };
      if (actionFilter !== 'ALL') params.action = actionFilter;
      if (entityFilter !== 'ALL') params.entity_type = entityFilter;
      if (startDate) params.start_date = startDate;
      if (endDate) params.end_date = endDate;

      const data = await auditService.getAuditLogs(params);
      setLogs(data.items || []);
      setTotal(data.total || 0);
    } catch (err) {
      setError(err.userMessage || 'Failed to load audit logs.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchAuditLogs();
  }, [page, actionFilter, entityFilter]);

  const handleApplyDateFilters = (e) => {
    e.preventDefault();
    setPage(1);
    fetchAuditLogs();
  };

  const totalPages = Math.ceil(total / pageSize) || 1;

  if (!isAdmin) {
    return (
      <div style={{ margin: '3rem auto', maxWidth: '500px', textAlign: 'center' }}>
        <div className="alert alert-error">
          <span>Access Denied: Only Administrators are authorized to view system compliance audit logs.</span>
        </div>
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.75rem' }}>
      <div>
        <h1 className="page-title">
          <ShieldCheck size={28} />
          Compliance & Audit Trail
        </h1>
        <p className="page-description">
          Immutable system-wide log of all user actions, security authorizations, and decision mutations.
        </p>
      </div>

      {/* Filter Bar */}
      <div className="card" style={{ padding: '1.25rem' }}>
        <form
          onSubmit={handleApplyDateFilters}
          style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', alignItems: 'flex-end' }}
        >
          <div className="form-group" style={{ marginBottom: 0, minWidth: '150px' }}>
            <label className="form-label" style={{ fontSize: '0.78rem' }}>Action</label>
            <select
              className="form-select"
              value={actionFilter}
              onChange={(e) => {
                setActionFilter(e.target.value);
                setPage(1);
              }}
            >
              {ACTIONS.map((a) => (
                <option key={a} value={a}>{a}</option>
              ))}
            </select>
          </div>

          <div className="form-group" style={{ marginBottom: 0, minWidth: '150px' }}>
            <label className="form-label" style={{ fontSize: '0.78rem' }}>Entity Type</label>
            <select
              className="form-select"
              value={entityFilter}
              onChange={(e) => {
                setEntityFilter(e.target.value);
                setPage(1);
              }}
            >
              {ENTITY_TYPES.map((e) => (
                <option key={e} value={e}>{e}</option>
              ))}
            </select>
          </div>

          <div className="form-group" style={{ marginBottom: 0, minWidth: '150px' }}>
            <label className="form-label" style={{ fontSize: '0.78rem' }}>Start Date</label>
            <input
              type="date"
              className="form-input"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
            />
          </div>

          <div className="form-group" style={{ marginBottom: 0, minWidth: '150px' }}>
            <label className="form-label" style={{ fontSize: '0.78rem' }}>End Date</label>
            <input
              type="date"
              className="form-input"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
            />
          </div>

          <button type="submit" className="btn btn-secondary" style={{ height: '40px' }}>
            <Filter size={16} /> Filter
          </button>
        </form>
      </div>

      {/* Audit Log Table */}
      {isLoading ? (
        <LoadingSpinner message="Fetching audit logs..." />
      ) : error ? (
        <div className="alert alert-error">
          <span>{error}</span>
        </div>
      ) : logs.length === 0 ? (
        <EmptyState
          icon={ShieldCheck}
          title="No audit logs found"
          description="No activity matches the current audit filter criteria."
        />
      ) : (
        <div className="table-container">
          <table className="table">
            <thead>
              <tr>
                <th>Timestamp</th>
                <th>User</th>
                <th>Action</th>
                <th>Entity</th>
                <th>IP Address</th>
                <th>Description</th>
                <th style={{ textAlign: 'right' }}>Details</th>
              </tr>
            </thead>
            <tbody>
              {logs.map((log) => {
                let actionColor = 'var(--text-muted)';
                if (log.action === 'CREATE') actionColor = '#34d399';
                if (log.action === 'APPROVE') actionColor = '#10b981';
                if (log.action === 'REJECT' || log.action === 'DELETE') actionColor = '#f87171';
                if (log.action === 'SUBMIT') actionColor = '#fbbf24';

                return (
                  <tr key={log.id}>
                    <td style={{ fontSize: '0.8rem', color: 'var(--text-dim)', whiteSpace: 'nowrap' }}>
                      {new Date(log.created_at).toLocaleString()}
                    </td>
                    <td>
                      <div className="table-cell-title">{log.user_name || `User #${log.user_id}`}</div>
                    </td>
                    <td>
                      <span
                        style={{
                          fontWeight: 700,
                          fontSize: '0.78rem',
                          color: actionColor,
                          background: 'var(--bg-elevated)',
                          padding: '2px 8px',
                          borderRadius: 'var(--radius-xs)',
                        }}
                      >
                        {log.action}
                      </span>
                    </td>
                    <td>
                      <span className="badge badge-category">
                        {log.entity_type} {log.entity_id ? `#${log.entity_id}` : ''}
                      </span>
                    </td>
                    <td style={{ fontSize: '0.8rem', fontFamily: 'var(--font-mono)', color: 'var(--text-muted)' }}>
                      {log.ip_address || '127.0.0.1'}
                    </td>
                    <td style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', maxWidth: '300px' }}>
                      {log.description}
                    </td>
                    <td style={{ textAlign: 'right' }}>
                      <button
                        className="btn btn-outline btn-sm"
                        onClick={() => setSelectedLog(log)}
                        title="View JSON metadata diff"
                      >
                        <Eye size={14} /> Diff
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '1rem' }}>
          <button
            className="btn btn-secondary btn-sm"
            disabled={page <= 1}
            onClick={() => setPage(page - 1)}
          >
            <ArrowLeft size={14} /> Prev
          </button>
          <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
            Page {page} of {totalPages} (Total: {total})
          </span>
          <button
            className="btn btn-secondary btn-sm"
            disabled={page >= totalPages}
            onClick={() => setPage(page + 1)}
          >
            Next <ArrowRight size={14} />
          </button>
        </div>
      )}

      {/* Audit Detail / Diff Modal */}
      {selectedLog && (
        <Modal
          isOpen={!!selectedLog}
          onClose={() => setSelectedLog(null)}
          title={`Audit Record #${selectedLog.id} Details`}
          size="lg"
          footer={
            <button className="btn btn-secondary" onClick={() => setSelectedLog(null)}>
              Close
            </button>
          }
        >
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div>
              <span className="text-dim" style={{ fontSize: '0.78rem' }}>Operation Description</span>
              <p style={{ fontSize: '0.95rem', fontWeight: 600, color: 'var(--text-primary)', marginTop: '2px' }}>
                {selectedLog.description}
              </p>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
              <div>
                <span className="text-dim" style={{ fontSize: '0.78rem' }}>User Performing Action</span>
                <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
                  {selectedLog.user_name || `User ID: ${selectedLog.user_id}`}
                </p>
              </div>
              <div>
                <span className="text-dim" style={{ fontSize: '0.78rem' }}>API Endpoint & Method</span>
                <p style={{ fontSize: '0.85rem', fontFamily: 'var(--font-mono)', color: 'var(--primary-light)' }}>
                  {selectedLog.request_method || 'POST'} {selectedLog.endpoint || '—'}
                </p>
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
              <div>
                <span className="text-dim" style={{ fontSize: '0.78rem' }}>Old Value (Previous State)</span>
                <pre
                  style={{
                    background: 'var(--bg-app)',
                    padding: '0.75rem',
                    borderRadius: 'var(--radius-sm)',
                    fontSize: '0.78rem',
                    fontFamily: 'var(--font-mono)',
                    color: '#b91c1c',
                    maxHeight: '200px',
                    overflowY: 'auto',
                    marginTop: '4px',
                    border: '1px solid var(--border-subtle)',
                  }}
                >
                  {selectedLog.old_value ? JSON.stringify(selectedLog.old_value, null, 2) : 'null (None)'}
                </pre>
              </div>

              <div>
                <span className="text-dim" style={{ fontSize: '0.78rem' }}>New Value (Mutated State)</span>
                <pre
                  style={{
                    background: 'var(--bg-app)',
                    padding: '0.75rem',
                    borderRadius: 'var(--radius-sm)',
                    fontSize: '0.78rem',
                    fontFamily: 'var(--font-mono)',
                    color: '#047857',
                    maxHeight: '200px',
                    overflowY: 'auto',
                    marginTop: '4px',
                    border: '1px solid var(--border-subtle)',
                  }}
                >
                  {selectedLog.new_value ? JSON.stringify(selectedLog.new_value, null, 2) : 'null'}
                </pre>
              </div>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
};
