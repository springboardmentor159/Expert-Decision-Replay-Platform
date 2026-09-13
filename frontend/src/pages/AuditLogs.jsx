import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { getAuditLogs, getSecurityLogs } from '../services/api';
import Layout from '../components/Layout';

export default function AuditLogs() {
  const [auditLogs, setAuditLogs] = useState([]);
  const [securityLogs, setSecurityLogs] = useState([]);
  const [activeTab, setActiveTab] = useState('audit');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [filters, setFilters] = useState({
    action: '', entity_type: '', start_date: '', end_date: ''
  });

  useEffect(() => { fetchLogs(); }, [activeTab, page]);

  const fetchLogs = async () => {
    setLoading(true);
    setError('');
    try {
      const params = { page, page_size: 20 };
      if (filters.action) params.action = filters.action;
      if (filters.entity_type) params.entity_type = filters.entity_type;
      if (filters.start_date) params.start_date = filters.start_date;
      if (filters.end_date) params.end_date = filters.end_date;

      if (activeTab === 'audit') {
        const response = await getAuditLogs(params);
        setAuditLogs(response.data.items || []);
        setTotal(response.data.total || 0);
      } else {
        const response = await getSecurityLogs(params);
        setSecurityLogs(response.data.items || []);
        setTotal(response.data.total || 0);
      }
    } catch (err) {
      if (err.response?.status === 403) {
        setError('Access denied. Administrator access required.');
      } else {
        setError('Failed to load logs');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (e) => {
    setFilters({ ...filters, [e.target.name]: e.target.value });
  };

  const getActionColor = (action) => {
    const colors = {
      'CREATE': '#27ae60', 'UPDATE': '#3498db', 'DELETE': '#e74c3c',
      'SUBMIT': '#f39c12', 'APPROVE': '#27ae60', 'REJECT': '#e74c3c',
    };
    return colors[action] || '#95a5a6';
  };

  const totalPages = Math.ceil(total / 20);

  return (
    <Layout>
      <h2 style={styles.title}>🔍 Audit & Compliance</h2>

      {/* Tabs */}
      <div style={styles.tabs}>
        <button
          style={{...styles.tab, ...(activeTab === 'audit' ? styles.activeTab : {})}}
          onClick={() => { setActiveTab('audit'); setPage(1); }}>
          📋 Audit Logs
        </button>
        <button
          style={{...styles.tab, ...(activeTab === 'security' ? styles.activeTab : {})}}
          onClick={() => { setActiveTab('security'); setPage(1); }}>
          🔐 Security Logs
        </button>
      </div>

      {/* Filters */}
      <div style={styles.filterCard}>
        <div style={styles.filterGrid}>
          {activeTab === 'audit' && (
            <>
              <div>
                <label style={styles.label}>Action</label>
                <select name="action" value={filters.action}
                  onChange={handleFilterChange} style={styles.select}>
                  <option value="">All Actions</option>
                  <option value="CREATE">CREATE</option>
                  <option value="UPDATE">UPDATE</option>
                  <option value="DELETE">DELETE</option>
                  <option value="SUBMIT">SUBMIT</option>
                  <option value="APPROVE">APPROVE</option>
                  <option value="REJECT">REJECT</option>
                </select>
              </div>
              <div>
                <label style={styles.label}>Entity Type</label>
                <select name="entity_type" value={filters.entity_type}
                  onChange={handleFilterChange} style={styles.select}>
                  <option value="">All Entities</option>
                  <option value="Decision">Decision</option>
                  <option value="Alternative">Alternative</option>
                  <option value="Comment">Comment</option>
                  <option value="DecisionVersion">DecisionVersion</option>
                </select>
              </div>
            </>
          )}
          <div>
            <label style={styles.label}>Start Date</label>
            <input type="date" name="start_date" value={filters.start_date}
              onChange={handleFilterChange} style={styles.select} />
          </div>
          <div>
            <label style={styles.label}>End Date</label>
            <input type="date" name="end_date" value={filters.end_date}
              onChange={handleFilterChange} style={styles.select} />
          </div>
          <div style={styles.applyBtnWrapper}>
            <label style={styles.label}>&nbsp;</label>
            <button style={styles.applyBtn} onClick={() => { setPage(1); fetchLogs(); }}>
              Apply Filters
            </button>
          </div>
        </div>
      </div>

      {error && <div style={styles.error}>{error}</div>}

      {/* Table */}
      <div style={styles.tableCard}>
        <div style={styles.tableHeader}>
          <h3 style={styles.tableTitle}>
            {activeTab === 'audit' ? 'Audit Logs' : 'Security Logs'}
          </h3>
          <span style={styles.totalCount}>{total} records</span>
        </div>

        {loading ? (
          <div style={styles.center}>Loading logs...</div>
        ) : activeTab === 'audit' ? (
          auditLogs.length === 0 ? (
            <p style={styles.empty}>No audit logs found.</p>
          ) : (
            <table style={styles.table}>
              <thead>
                <tr style={styles.thead}>
                  <th style={styles.th}>ID</th>
                  <th style={styles.th}>Action</th>
                  <th style={styles.th}>Entity</th>
                  <th style={styles.th}>Entity ID</th>
                  <th style={styles.th}>User</th>
                  <th style={styles.th}>Description</th>
                  <th style={styles.th}>Date</th>
                </tr>
              </thead>
              <tbody>
                {auditLogs.map(log => (
                  <tr key={log.id} style={styles.tr}>
                    <td style={styles.td}>{log.id}</td>
                    <td style={styles.td}>
                      <span style={{...styles.badge, backgroundColor: getActionColor(log.action)}}>
                        {log.action}
                      </span>
                    </td>
                    <td style={styles.td}>{log.entity_type}</td>
                    <td style={styles.td}>{log.entity_id}</td>
                    <td style={styles.td}>User #{log.user_id}</td>
                    <td style={styles.td}>{log.description}</td>
                    <td style={styles.td}>{new Date(log.created_at).toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )
        ) : (
          securityLogs.length === 0 ? (
            <p style={styles.empty}>No security logs found.</p>
          ) : (
            <table style={styles.table}>
              <thead>
                <tr style={styles.thead}>
                  <th style={styles.th}>ID</th>
                  <th style={styles.th}>Event</th>
                  <th style={styles.th}>Email</th>
                  <th style={styles.th}>User ID</th>
                  <th style={styles.th}>Description</th>
                  <th style={styles.th}>Date</th>
                </tr>
              </thead>
              <tbody>
                {securityLogs.map(log => (
                  <tr key={log.id} style={styles.tr}>
                    <td style={styles.td}>{log.id}</td>
                    <td style={styles.td}>
                      <span style={{
                        ...styles.badge,
                        backgroundColor: log.event_type === 'LOGIN_SUCCESS' ? '#27ae60' : '#e74c3c'
                      }}>
                        {log.event_type}
                      </span>
                    </td>
                    <td style={styles.td}>{log.email}</td>
                    <td style={styles.td}>{log.user_id ? `User #${log.user_id}` : 'N/A'}</td>
                    <td style={styles.td}>{log.description}</td>
                    <td style={styles.td}>{new Date(log.created_at).toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )
        )}

        {/* Pagination */}
        {totalPages > 1 && (
          <div style={styles.pagination}>
            <button
              style={{...styles.pageBtn, opacity: page === 1 ? 0.5 : 1}}
              onClick={() => setPage(page - 1)} disabled={page === 1}>
              ← Previous
            </button>
            <span style={styles.pageInfo}>Page {page} of {totalPages}</span>
            <button
              style={{...styles.pageBtn, opacity: page === totalPages ? 0.5 : 1}}
              onClick={() => setPage(page + 1)} disabled={page === totalPages}>
              Next →
            </button>
          </div>
        )}
      </div>
    </Layout>
  );
}

const styles = {
  title: { color: '#2C3E50', fontSize: '24px', marginBottom: '24px' },
  tabs: { display: 'flex', gap: '8px', marginBottom: '20px' },
  tab: { padding: '10px 24px', border: 'none', borderRadius: '6px', cursor: 'pointer', backgroundColor: '#ecf0f1', color: '#7f8c8d', fontSize: '14px' },
  activeTab: { backgroundColor: '#2C3E50', color: 'white' },
  filterCard: { backgroundColor: 'white', padding: '20px', borderRadius: '10px', marginBottom: '20px', boxShadow: '0 2px 8px rgba(0,0,0,0.05)' },
  filterGrid: { display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '16px', alignItems: 'end' },
  label: { display: 'block', marginBottom: '4px', color: '#2C3E50', fontWeight: '600', fontSize: '13px' },
  select: { width: '100%', padding: '8px', borderRadius: '6px', border: '1px solid #ddd', fontSize: '13px', boxSizing: 'border-box' },
  applyBtnWrapper: {},
  applyBtn: { width: '100%', padding: '8px', backgroundColor: '#2C3E50', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', fontSize: '13px' },
  error: { backgroundColor: '#fde8e8', color: '#c0392b', padding: '12px', borderRadius: '6px', marginBottom: '16px' },
  tableCard: { backgroundColor: 'white', borderRadius: '10px', padding: '24px', boxShadow: '0 2px 8px rgba(0,0,0,0.05)' },
  tableHeader: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' },
  tableTitle: { color: '#2C3E50', fontSize: '18px', margin: 0 },
  totalCount: { color: '#7f8c8d', fontSize: '14px' },
  table: { width: '100%', borderCollapse: 'collapse', overflowX: 'auto' },
  thead: { backgroundColor: '#f8f9fa' },
  th: { padding: '12px', textAlign: 'left', color: '#7f8c8d', fontSize: '12px', fontWeight: '600', borderBottom: '2px solid #eee' },
  tr: { borderBottom: '1px solid #eee' },
  td: { padding: '12px', fontSize: '13px', color: '#2C3E50' },
  badge: { padding: '3px 8px', borderRadius: '4px', color: 'white', fontSize: '11px', fontWeight: '600' },
  pagination: { display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '16px', marginTop: '20px' },
  pageBtn: { padding: '8px 20px', backgroundColor: '#2C3E50', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer' },
  pageInfo: { color: '#7f8c8d', fontSize: '14px' },
  empty: { textAlign: 'center', padding: '40px', color: '#7f8c8d' },
  center: { textAlign: 'center', padding: '40px', color: '#7f8c8d' },
};