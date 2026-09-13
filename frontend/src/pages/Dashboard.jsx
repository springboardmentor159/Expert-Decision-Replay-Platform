import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { getEmployeeDashboard } from '../services/api';
import Layout from '../components/Layout';

export default function Dashboard() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const { user } = useAuth();
  const navigate = useNavigate();

  useEffect(() => { fetchDashboard(); }, []);

  const fetchDashboard = async () => {
    try {
      const response = await getEmployeeDashboard();
      setData(response.data);
    } catch (err) {
      setError('Failed to load dashboard');
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <Layout><div style={styles.center}>Loading dashboard...</div></Layout>;
  if (error) return <Layout><div style={styles.center}>{error}</div></Layout>;

  return (
    <Layout>
      <h2 style={styles.welcome}>Welcome, {user?.full_name}!</h2>
      <p style={styles.role}>Role: {user?.role}</p>

      <div style={styles.cards}>
        <div style={styles.card}>
          <div style={styles.cardNumber}>{data?.total_decisions || 0}</div>
          <div style={styles.cardLabel}>Total Decisions</div>
        </div>
        <div style={{...styles.card, backgroundColor: '#3498db'}}>
          <div style={styles.cardNumber}>{data?.draft_decisions || 0}</div>
          <div style={styles.cardLabel}>Draft</div>
        </div>
        <div style={{...styles.card, backgroundColor: '#f39c12'}}>
          <div style={styles.cardNumber}>{data?.under_review || 0}</div>
          <div style={styles.cardLabel}>Under Review</div>
        </div>
        <div style={{...styles.card, backgroundColor: '#27ae60'}}>
          <div style={styles.cardNumber}>{data?.approved_decisions || 0}</div>
          <div style={styles.cardLabel}>Approved</div>
        </div>
        <div style={{...styles.card, backgroundColor: '#e74c3c'}}>
          <div style={styles.cardNumber}>{data?.rejected_decisions || 0}</div>
          <div style={styles.cardLabel}>Rejected</div>
        </div>
        <div style={{...styles.card, backgroundColor: '#9b59b6'}}>
          <div style={styles.cardNumber}>{data?.pending_reviews || 0}</div>
          <div style={styles.cardLabel}>Pending Reviews</div>
        </div>
      </div>

      <div style={styles.section}>
        <h3 style={styles.sectionTitle}>Recent Activities</h3>
        {data?.recent_activities?.length === 0 ? (
          <p style={styles.empty}>No recent activities</p>
        ) : (
          <table style={styles.table}>
            <thead>
              <tr>
                <th style={styles.th}>Action</th>
                <th style={styles.th}>Entity</th>
                <th style={styles.th}>Description</th>
                <th style={styles.th}>Date</th>
              </tr>
            </thead>
            <tbody>
              {data?.recent_activities?.map((activity) => (
                <tr key={activity.id}>
                  <td style={styles.td}>{activity.action}</td>
                  <td style={styles.td}>{activity.entity_type}</td>
                  <td style={styles.td}>{activity.description}</td>
                  <td style={styles.td}>{new Date(activity.created_at).toLocaleDateString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      <div style={styles.section}>
        <h3 style={styles.sectionTitle}>Quick Actions</h3>
        <div style={styles.actions}>
          <button style={styles.actionBtn} onClick={() => navigate('/decisions/create')}>
            + Create Decision
          </button>
          <button style={{...styles.actionBtn, backgroundColor: '#3498db'}}
            onClick={() => navigate('/decisions')}>
            View My Decisions
          </button>
          <button style={{...styles.actionBtn, backgroundColor: '#27ae60'}}
            onClick={() => navigate('/repository')}>
            Knowledge Repository
          </button>
          <button style={{...styles.actionBtn, backgroundColor: '#9b59b6'}}
            onClick={() => navigate('/reports')}>
            View Reports
          </button>
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
  sectionTitle: { color: '#2C3E50', marginBottom: '16px', fontSize: '18px' },
  table: { width: '100%', borderCollapse: 'collapse' },
  th: { textAlign: 'left', padding: '10px', borderBottom: '2px solid #eee', color: '#7f8c8d', fontSize: '13px' },
  td: { padding: '10px', borderBottom: '1px solid #eee', fontSize: '14px' },
  empty: { color: '#7f8c8d', fontStyle: 'italic' },
  actions: { display: 'flex', gap: '12px', flexWrap: 'wrap' },
  actionBtn: { padding: '10px 20px', backgroundColor: '#2C3E50', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', fontSize: '14px' },
  center: { display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' },
};