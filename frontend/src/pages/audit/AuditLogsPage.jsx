import React, { useState, useEffect, useCallback } from 'react';
import { ShieldAlert, Filter, Calendar, User, FileText, Info } from 'lucide-react';
import { auditApi } from '../../api/audit';
import { useAuth } from '../../context/AuthContext';
import { useNotification } from '../../context/NotificationContext';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import { Pagination } from '../../components/common/Pagination';
import { EmptyState } from '../../components/common/EmptyState';
import { Modal } from '../../components/common/Modal';

export function AuditLogsPage() {
  const { isAdmin, isManager } = useAuth();
  const { error } = useNotification();

  const [logs, setLogs] = useState([]);
  const [total, setTotal] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);

  // Filters
  const [action, setAction] = useState('');
  const [entityType, setEntityType] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [selectedLog, setSelectedLog] = useState(null);

  const fetchLogs = useCallback(async () => {
    if (!isAdmin && !isManager) return;
    setLoading(true);
    try {
      const res = await auditApi.getLogs({
        action: action || undefined,
        entity_type: entityType || undefined,
        start_date: startDate || undefined,
        end_date: endDate || undefined,
        page,
        page_size: 15,
      });

      setLogs(res.items || []);
      setTotal(res.total || 0);
      setTotalPages(res.total_pages || 1);
    } catch (err) {
      error(err.message || 'Failed to fetch audit logs');
    } finally {
      setLoading(false);
    }
  }, [isAdmin, isManager, action, entityType, startDate, endDate, page, error]);

  useEffect(() => {
    fetchLogs();
  }, [fetchLogs]);

  if (!isAdmin && !isManager) {
    return (
      <EmptyState
        icon={ShieldAlert}
        title="Restricted Governance Log"
        description="Your role does not have authorization to view sensitive administrative audit trails."
      />
    );
  }

  const getActionColor = (act) => {
    if (!act) return 'var(--text-muted)';
    const a = act.toUpperCase();
    if (a.includes('APPROVE')) return 'var(--success)';
    if (a.includes('REJECT') || a.includes('DELETE')) return 'var(--danger)';
    if (a.includes('SUBMIT') || a.includes('CREATE')) return 'var(--primary)';
    return 'var(--warning)';
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      <div>
        <h1 style={{ fontSize: '1.75rem', marginBottom: '0.25rem', display: 'flex', alignItems: 'center', gap: '10px' }}>
          <ShieldAlert size={26} style={{ color: 'var(--primary)' }} /> Audit & Governance Activity Trail
        </h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
          Tamper-evident logs of all system state changes, authorization decisions, and access events ({total} total).
        </p>
      </div>

      {/* Filter Card */}
      <div className="card" style={{ padding: '1.25rem' }}>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '1rem', alignItems: 'center' }}>
          <select
            className="form-select"
            style={{ width: 'auto', minWidth: '160px' }}
            value={action}
            onChange={(e) => { setAction(e.target.value); setPage(1); }}
          >
            <option value="">All Actions</option>
            <option value="CREATE">CREATE</option>
            <option value="UPDATE">UPDATE</option>
            <option value="DELETE">DELETE</option>
            <option value="SUBMIT">SUBMIT</option>
            <option value="APPROVE">APPROVE</option>
            <option value="REJECT">REJECT</option>
            <option value="ARCHIVE">ARCHIVE</option>
          </select>

          <select
            className="form-select"
            style={{ width: 'auto', minWidth: '160px' }}
            value={entityType}
            onChange={(e) => { setEntityType(e.target.value); setPage(1); }}
          >
            <option value="">All Entity Types</option>
            <option value="Decision">Decision</option>
            <option value="Alternative">Alternative</option>
            <option value="Comment">Comment</option>
            <option value="Approval">Approval</option>
            <option value="Tag">Tag</option>
          </select>

          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>From:</span>
            <input
              type="date"
              className="form-input"
              style={{ width: 'auto' }}
              value={startDate}
              onChange={(e) => { setStartDate(e.target.value); setPage(1); }}
            />
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>To:</span>
            <input
              type="date"
              className="form-input"
              style={{ width: 'auto' }}
              value={endDate}
              onChange={(e) => { setEndDate(e.target.value); setPage(1); }}
            />
          </div>

          {(action || entityType || startDate || endDate) && (
            <button
              className="btn btn-secondary btn-sm"
              onClick={() => {
                setAction('');
                setEntityType('');
                setStartDate('');
                setEndDate('');
                setPage(1);
              }}
            >
              Reset Filters
            </button>
          )}
        </div>
      </div>

      {/* Logs Table */}
      {loading ? (
        <LoadingSpinner message="Fetching audit trail..." />
      ) : logs.length === 0 ? (
        <EmptyState
          title="No audit records found"
          description="No activities recorded matching the selected criteria."
        />
      ) : (
        <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
          <div className="table-container" style={{ border: 'none', borderRadius: 0 }}>
            <table className="table">
              <thead>
                <tr>
                  <th>Timestamp</th>
                  <th>Action</th>
                  <th>Entity</th>
                  <th>User ID</th>
                  <th>Description</th>
                  <th style={{ textAlign: 'right' }}>Details</th>
                </tr>
              </thead>
              <tbody>
                {logs.map((log) => (
                  <tr key={log.id}>
                    <td style={{ whiteSpace: 'nowrap', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                      {new Date(log.created_at).toLocaleString()}
                    </td>
                    <td>
                      <span
                        className="badge"
                        style={{
                          color: getActionColor(log.action),
                          border: `1px solid ${getActionColor(log.action)}`,
                          background: 'var(--bg-hover)',
                        }}
                      >
                        {log.action}
                      </span>
                    </td>
                    <td>
                      <span className="badge badge-role">
                        {log.entity_type} #{log.entity_id}
                      </span>
                    </td>
                    <td>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                        <User size={13} style={{ color: 'var(--text-muted)' }} />
                        User #{log.user_id}
                      </div>
                    </td>
                    <td style={{ maxWidth: '400px', fontSize: '0.85rem' }}>
                      {log.description || 'System state change'}
                    </td>
                    <td style={{ textAlign: 'right' }}>
                      <button
                        className="btn btn-secondary btn-sm"
                        onClick={() => setSelectedLog(log)}
                      >
                        <Info size={14} /> Inspect
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <Pagination
            currentPage={page}
            totalPages={totalPages}
            onPageChange={(p) => setPage(p)}
          />
        </div>
      )}

      {/* Detail Modal */}
      <Modal
        isOpen={!!selectedLog}
        onClose={() => setSelectedLog(null)}
        title="Audit Record Inspection"
      >
        {selectedLog && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', fontSize: '0.875rem' }}>
            <div>
              <strong>Action:</strong> <span style={{ color: getActionColor(selectedLog.action) }}>{selectedLog.action}</span>
            </div>
            <div>
              <strong>Target Entity:</strong> {selectedLog.entity_type} #{selectedLog.entity_id}
            </div>
            <div>
              <strong>Decision ID:</strong> {selectedLog.decision_id || 'N/A'}
            </div>
            <div>
              <strong>Performed By User:</strong> #{selectedLog.user_id}
            </div>
            <div>
              <strong>Timestamp:</strong> {new Date(selectedLog.created_at).toLocaleString()}
            </div>
            <div>
              <strong>Summary:</strong> {selectedLog.description}
            </div>
            {selectedLog.old_value && (
              <div>
                <strong>Old Value:</strong>
                <pre style={{
                  background: 'var(--bg-input)',
                  padding: '0.75rem',
                  borderRadius: '6px',
                  marginTop: '4px',
                  overflowX: 'auto',
                  fontSize: '0.775rem',
                }}>
                  {JSON.stringify(selectedLog.old_value, null, 2)}
                </pre>
              </div>
            )}
            {selectedLog.new_value && (
              <div>
                <strong>New Value:</strong>
                <pre style={{
                  background: 'var(--bg-input)',
                  padding: '0.75rem',
                  borderRadius: '6px',
                  marginTop: '4px',
                  overflowX: 'auto',
                  fontSize: '0.775rem',
                }}>
                  {JSON.stringify(selectedLog.new_value, null, 2)}
                </pre>
              </div>
            )}
          </div>
        )}
      </Modal>
    </div>
  );
}
