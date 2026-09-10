import React, { useState, useEffect } from 'react';
import { auditService } from '../../api/auditService';
import { Card } from '../../components/common/Card';
import { Button } from '../../components/common/Button';
import { Input, Select } from '../../components/common/Input';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import { EmptyState } from '../../components/common/EmptyState';
import { Pagination } from '../../components/common/Pagination';
import { useToast } from '../../context/ToastContext';
import { useAuth } from '../../context/AuthContext';
import {
  ShieldAlert,
  ShieldCheck,
  Lock,
  Search,
  Calendar,
  Filter,
  Eye,
  Activity,
  AlertTriangle,
} from 'lucide-react';

export const AuditLogsPage = () => {
  const [activeTab, setActiveTab] = useState('audit'); // 'audit', 'security', 'access', 'activities'
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [forbidden, setForbidden] = useState(false);

  // Filters
  const [userIdFilter, setUserIdFilter] = useState('');
  const [actionFilter, setActionFilter] = useState('');
  const [entityFilter, setEntityFilter] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [page, setPage] = useState(1);
  const [pageSize] = useState(15);
  const [total, setTotal] = useState(0);

  const { error } = useToast();
  const { user } = useAuth();

  const fetchLogs = async () => {
    try {
      setLoading(true);
      setForbidden(false);

      const params = {
        user_id: userIdFilter ? Number(userIdFilter) : undefined,
        action: actionFilter.trim() || undefined,
        entity_type: entityFilter.trim() || undefined,
        start_date: startDate || undefined,
        end_date: endDate || undefined,
        page,
        page_size: pageSize,
      };

      let res;
      if (activeTab === 'audit') {
        res = await auditService.getAuditLogs(params);
      } else if (activeTab === 'security') {
        res = await auditService.getSecurityLogs(params);
      } else if (activeTab === 'access') {
        res = await auditService.getAccessLogs(params);
      } else {
        res = await auditService.getActivities(params);
      }

      setLogs(res.items || res || []);
      setTotal(res.total || (res.items ? res.items.length : res.length || 0));
    } catch (err) {
      if (err.status === 403) {
        setForbidden(true);
      } else {
        error(err.message || 'Failed to fetch compliance logs');
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    setPage(1);
    fetchLogs();
  }, [activeTab]);

  useEffect(() => {
    fetchLogs();
  }, [page]);

  const handleFilterSubmit = (e) => {
    e.preventDefault();
    setPage(1);
    fetchLogs();
  };

  if (forbidden) {
    return (
      <EmptyState
        icon={Lock}
        title="403 Forbidden: Restricted Audit Area"
        description="System audit logs, security events, and compliance telemetry are restricted to Administrator accounts. Your current role is not authorized to inspect administrative audit data."
      />
    );
  }

  return (
    <div>
      {/* Header Banner */}
      <div style={{ marginBottom: '1.5rem' }}>
        <h2 style={{ fontSize: '1.75rem', fontWeight: 800, color: '#ffffff' }}>
          Audit, Compliance & Security Logs
        </h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.925rem' }}>
          Immutable system-wide event trails, security authentication logs, and data access records.
        </p>
      </div>

      {/* Tabs for Audit Category */}
      <div className="tabs-header">
        <button
          className={`tab-btn ${activeTab === 'audit' ? 'active' : ''}`}
          onClick={() => setActiveTab('audit')}
        >
          <ShieldAlert size={16} /> Audit Logs (CRUD Operations)
        </button>
        <button
          className={`tab-btn ${activeTab === 'security' ? 'active' : ''}`}
          onClick={() => setActiveTab('security')}
        >
          <Lock size={16} /> Security Logs (Auth Events)
        </button>
        <button
          className={`tab-btn ${activeTab === 'access' ? 'active' : ''}`}
          onClick={() => setActiveTab('access')}
        >
          <Eye size={16} /> Access Logs (Read/Download)
        </button>
        <button
          className={`tab-btn ${activeTab === 'activities' ? 'active' : ''}`}
          onClick={() => setActiveTab('activities')}
        >
          <Activity size={16} /> Activity Stream
        </button>
      </div>

      {/* Filter Control Bar */}
      <Card style={{ marginBottom: '1.5rem' }}>
        <form onSubmit={handleFilterSubmit}>
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))',
              gap: '1rem',
              alignItems: 'flex-end',
            }}
          >
            <div>
              <Input
                label="User ID"
                type="number"
                placeholder="Filter by ID..."
                value={userIdFilter}
                onChange={(e) => setUserIdFilter(e.target.value)}
              />
            </div>

            <div>
              <Input
                label="Action"
                placeholder="e.g. CREATE, APPROVE"
                value={actionFilter}
                onChange={(e) => setActionFilter(e.target.value)}
              />
            </div>

            {activeTab !== 'security' && (
              <div>
                <Input
                  label="Entity Type"
                  placeholder="e.g. Decision, Alternative"
                  value={entityFilter}
                  onChange={(e) => setEntityFilter(e.target.value)}
                />
              </div>
            )}

            <div>
              <Input
                label="Start Date (YYYY-MM-DD)"
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
              />
            </div>

            <div>
              <Input
                label="End Date (YYYY-MM-DD)"
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
              />
            </div>

            <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.25rem' }}>
              <Button type="submit" variant="primary" icon={Search} style={{ flex: 1 }}>
                Filter
              </Button>
              <Button
                type="button"
                variant="outline"
                onClick={() => {
                  setUserIdFilter('');
                  setActionFilter('');
                  setEntityFilter('');
                  setStartDate('');
                  setEndDate('');
                  setPage(1);
                  fetchLogs();
                }}
              >
                Reset
              </Button>
            </div>
          </div>
        </form>
      </Card>

      {/* Logs Table */}
      {loading ? (
        <LoadingSpinner message="Querying compliance log repository..." />
      ) : logs.length === 0 ? (
        <EmptyState
          icon={ShieldCheck}
          title="No logs found"
          description="No events match your current filter criteria."
        />
      ) : (
        <Card>
          <div className="table-container">
            <table className="custom-table">
              <thead>
                <tr>
                  <th>Timestamp</th>
                  <th>User</th>
                  <th>Action / Event</th>
                  {activeTab !== 'security' && <th>Entity</th>}
                  <th>IP Address</th>
                  <th>Description / Details</th>
                </tr>
              </thead>
              <tbody>
                {logs.map((item) => (
                  <tr key={item.id}>
                    <td style={{ color: 'var(--text-muted)', fontSize: '0.8rem', whiteSpace: 'nowrap' }}>
                      {new Date(item.created_at || item.timestamp).toLocaleString()}
                    </td>
                    <td style={{ fontWeight: 600, color: '#ffffff' }}>
                      {item.user_id ? `User #${item.user_id}` : 'System'}
                    </td>
                    <td>
                      <span
                        className="badge"
                        style={{
                          background: 'rgba(59, 130, 246, 0.15)',
                          color: '#60a5fa',
                          borderColor: 'rgba(59, 130, 246, 0.3)',
                        }}
                      >
                        {item.action || item.event_type}
                      </span>
                    </td>
                    {activeTab !== 'security' && (
                      <td style={{ color: 'var(--accent-cyan)', fontSize: '0.85rem' }}>
                        {item.entity_type} {item.entity_id ? `#${item.entity_id}` : ''}
                      </td>
                    )}
                    <td style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                      {item.ip_address || '127.0.0.1'}
                    </td>
                    <td style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', maxWidth: '350px' }}>
                      {item.description || JSON.stringify(item.details || item.new_value || '-')}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <Pagination
            page={page}
            pageSize={pageSize}
            totalItems={total}
            totalPages={Math.ceil(total / pageSize) || 1}
            onPageChange={(p) => setPage(p)}
          />
        </Card>
      )}
    </div>
  );
};
