import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { getAdminDashboard, getAuditLogs, getSecurityLogs } from '../services/api';
import Layout from '../components/Layout';

export default function AdminDashboard() {
  const [data, setData] = useState(null);
  const [auditLogs, setAuditLogs] = useState([]);
  const [securityLogs, setSecurityLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const { user } = useAuth();
  const navigate = useNavigate();

  useEffect(() => { fetchAll(); }, []);

  const fetchAll = async () => {
    try {
      const [dashRes, auditRes, secRes] = await Promise.all([
        getAdminDashboard(),
        getAuditLogs({ page_size: 5 }),
        getSecurityLogs({ page_size: 5 }),
      ]);
      setData(dashRes.data);
      setAuditLogs(auditRes.data.items || []);
      setSecurityLogs(secRes.data.items || []);
    } catch (err) {
      setError('Failed to load admin dashboard');
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <Layout><div style={styles.center}>Loading...</div></Layout>;
  if (error) return <Layout><div style={styles.center}>{error}</div></Layout>;

  return (
    <Layout>
      <h2 style={styles.welcome}>Admin Dashboard</h2>
      <p style={styles.role}>Welcome, {user?.full_name} | {user?.role}</p>

      {/* Stats Cards */}
      <div style={styles.cards}>
        <div style={styles.card}>
          <div style={styles.cardNumber}>{data?.total_users || 0}</div>
          <div style={styles.cardLabel}>Total Users</div>
        </div>
        <div style={{...styles.card, backgroundColor: '#3498db'}}>
          <div style={styles.cardNumber}>{data?.total_decisions || 0}</div>
          <div style={styles.cardLabel}>Total Decisions</div>
        </div>
        <div style={{...styles.card, backgroundColor: '#27ae60'}}>
          <div style={styles.cardNumber}>{data?.approved_decisions || 0}</div>
          <div style={styles.cardLabel}>Approved</div>
        </div>
        <div style={{...styles.card, backgroundColor: '#e74c3c'}}>
          <div style={styles.cardNumber}>{data?.rejected_decisions || 0}</div>
          <div style={styles.cardLabel}>Rejected</div>
        </div>
        <div style={{...styles.card, backgroundColor: '#f39c12'}}>
          <div style={styles.cardNumber}>{data?.under_review || 0}</div>
          <div style={styles.cardLabel}>Under Review</div>
        </div>
        <div style={{...styles.card, backgroundColor: '#9b59b6'}}>
          <div style={styles.cardNumber}>{data?.completion_rate || 0}%</div>
          <div style={styles.cardLabel}>Completion Rate</div>
        </div>
      </div>

      {/* Quick Actions */}
      <div style={styles.section}>
        <h3 style={styles.sectionTitle}>Quick Actions</h3>
        <div style={styles.actions}>
          <button style={styles.actionBtn} onClick={() => navigate('/decisions')}>
            📋 All Decisions
          </button>
          <button style={{...styles.actionBtn, backgroundColor: '#3498db'}}
            onClick={() => navigate('/reports')}>
            📊 Reports
          </button>
          <button style={{...styles.actionBtn, backgroundColor: '#9b59b6'}}
            onClick={() => navigate('/admin/audit')}>
            🔍 Audit Logs
          </button>
          <button style={{...styles.actionBtn, backgroundColor: '#27ae60'}}
            onClick={() => navigate('/repository')}>
            📚 Repository
          </button>
        </div>
      </div>

      <div style={styles.grid}>
        {/* Recent Audit Logs */}
        <div style={styles.section}>
          <div style={styles.sectionHeader}>
            <h3 style={styles.sectionTitle}>Recent Audit Logs</h3>
            <button style={styles.viewAllBtn}
              onClick={() => navigate('/admin/audit')}>
              View All →
            </button>
          </div>
          {auditLogs.length === 0 ? (
            <p style={styles.empty}>No audit logs found</p>
          ) : (
            <table style={styles.table}>
              <thead>
                <tr>
                  <th style={styles.th}>Action</th>
                  <th style={styles.th}>Entity</th>
                  <th style={styles.th}>User</th>
                  <th style={styles.th}>Date</th>
                </tr>
              </thead>
              <tbody>
                {auditLogs.map((log) => (
                  <tr key={log.id}>
                    <td style={styles.td}>
                      <span style={{
                        ...styles.actionBadge,
                        backgroundColor:
                          log.action === 'CREATE' ? '#27ae60' :
                          log.action === 'UPDATE' ? '#3498db' :
                          log.action === 'DELETE' ? '#e74c3c' : '#95a5a6'
                      }}>
                        {log.action}
                      </span>
                    </td>
                    <td style={styles.td}>{log.entity_type}</td>
                    <td style={styles.td}>User #{log.user_id}</td>
                    <td style={styles.td}>
                      {new Date(log.created_at).toLocaleDateString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        {/* Recent Security Logs */}
        <div style={styles.section}>
          <div style={styles.sectionHeader}>
            <h3 style={styles.sectionTitle}>Recent Security Events</h3>
            <button style={styles.viewAllBtn}
              onClick={() => navigate('/admin/audit')}>
              View All →
            </button>
          </div>
          {securityLogs.length === 0 ? (
            <p style={styles.empty}>No security logs found</p>
          ) : (
            <table style={styles.table}>
              <thead>
                <tr>
                  <th style={styles.th}>Event</th>
                  <th style={styles.th}>Email</th>
                  <th style={styles.th}>Date</th>
                </tr>
              </thead>
              <tbody>
                {securityLogs.map((log) => (
                  <tr key={log.id}>
                    <td style={styles.td}>
                      <span style={{
                        ...styles.actionBadge,
                        backgroundColor: log.event_type === 'LOGIN_SUCCESS' ? '#27ae60' : '#e74c3c'
                      }}>
                        {log.event_type}
                      </span>
                    </td>
                    <td style={styles.td}>{log.email}</td>
                    <td style={styles.td}>
                      {new Date(log.created_at).toLocaleDateString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </Layout>
  );
}

const styles = {
  welcome: { color: '#2C3E50', fontSize: '24px', marginBottom: '4px' },
  role: { color: '#7f8c8d', marginBottom: '24px' },
  cards: { display: 'grid', gridTemplateColumns: 'repeat(6, 1fr)', gap: '16px', marginBottom: '32px' },
  card: { backgroundColor: '#2C3E50', color: 'white', padding: '20px', borderRadius: '10px', textAlign: 'center' },
  cardNumber: { fontSize: '32px', fontWeight: 'bold' },
  cardLabel: { fontSize: '12px', marginTop: '4px', opacity: 0.8 },
  section: { backgroundColor: 'white', padding: '24px', borderRadius: '10px', marginBottom: '24px', boxShadow: '0 2px 8px rgba(0,0,0,0.05)' },
  sectionHeader: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' },
  sectionTitle: { color: '#2C3E50', fontSize: '18px', margin: 0 },
  viewAllBtn: { padding: '6px 14px', backgroundColor: '#ecf0f1', border: 'none', borderRadius: '6px', cursor: 'pointer', fontSize: '13px' },
  actions: { display: 'flex', gap: '12px', flexWrap: 'wrap' },
  actionBtn: { padding: '10px 20px', backgroundColor: '#2C3E50', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', fontSize: '14px' },
  grid: { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' },
  table: { width: '100%', borderCollapse: 'collapse' },
  th: { textAlign: 'left', padding: '10px', borderBottom: '2px solid #eee', color: '#7f8c8d', fontSize: '13px' },
  td: { padding: '10px', borderBottom: '1px solid #eee', fontSize: '14px' },
  actionBadge: { padding: '3px 8px', borderRadius: '4px', color: 'white', fontSize: '11px', fontWeight: '600' },
  empty: { color: '#7f8c8d', fontStyle: 'italic' },
  center: { display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' },
};