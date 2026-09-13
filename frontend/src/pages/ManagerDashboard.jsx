import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { getManagerDashboard } from '../services/api';
import Layout from '../components/Layout';

export default function ManagerDashboard() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const { user } = useAuth();
  const navigate = useNavigate();

  useEffect(() => { fetchDashboard(); }, []);

  const fetchDashboard = async () => {
    try {
      const response = await getManagerDashboard();
      setData(response.data);
    } catch (err) {
      setError('Failed to load manager dashboard');
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <Layout><div style={styles.center}>Loading...</div></Layout>;
  if (error) return <Layout><div style={styles.center}>{error}</div></Layout>;

  return (
    <Layout>
      <h2 style={styles.welcome}>Manager Dashboard</h2>
      <p style={styles.role}>Welcome, {user?.full_name} | {user?.role}</p>

      {/* Stats Cards */}
      <div style={styles.cards}>
        <div style={styles.card}>
          <div style={styles.cardNumber}>{data?.team_decisions || 0}</div>
          <div style={styles.cardLabel}>Team Decisions</div>
        </div>
        <div style={{...styles.card, backgroundColor: '#f39c12'}}>
          <div style={styles.cardNumber}>{data?.pending_approvals || 0}</div>
          <div style={styles.cardLabel}>Pending Approvals</div>
        </div>
        <div style={{...styles.card, backgroundColor: '#27ae60'}}>
          <div style={styles.cardNumber}>{data?.approved_decisions || 0}</div>
          <div style={styles.cardLabel}>Approved</div>
        </div>
        <div style={{...styles.card, backgroundColor: '#e74c3c'}}>
          <div style={styles.cardNumber}>{data?.rejected_decisions || 0}</div>
          <div style={styles.cardLabel}>Rejected</div>
        </div>
        <div style={{...styles.card, backgroundColor: '#3498db'}}>
          <div style={styles.cardNumber}>{data?.under_review || 0}</div>
          <div style={styles.cardLabel}>Under Review</div>
        </div>
      </div>

      {/* Quick Actions */}
      <div style={styles.section}>
        <h3 style={styles.sectionTitle}>Quick Actions</h3>
        <div style={styles.actions}>
          <button style={styles.actionBtn}
            onClick={() => navigate('/decisions')}>
            📋 View All Decisions
          </button>
          <button style={{...styles.actionBtn, backgroundColor: '#3498db'}}
            onClick={() => navigate('/repository')}>
            📚 Knowledge Repository
          </button>
          <button style={{...styles.actionBtn, backgroundColor: '#27ae60'}}
            onClick={() => navigate('/reports')}>
            📊 Generate Reports
          </button>
        </div>
      </div>

      {/* Team Statistics */}
      <div style={styles.section}>
        <h3 style={styles.sectionTitle}>Team Statistics</h3>
        <div style={styles.statsGrid}>
          <div style={styles.statItem}>
            <div style={styles.statLabel}>Total Team Decisions</div>
            <div style={styles.statValue}>{data?.team_decisions || 0}</div>
            <div style={styles.statBar}>
              <div style={{...styles.statBarFill, width: '100%', backgroundColor: '#2C3E50'}} />
            </div>
          </div>
          <div style={styles.statItem}>
            <div style={styles.statLabel}>Approved</div>
            <div style={styles.statValue}>{data?.approved_decisions || 0}</div>
            <div style={styles.statBar}>
              <div style={{
                ...styles.statBarFill,
                width: data?.team_decisions ?
                  `${(data.approved_decisions / data.team_decisions) * 100}%` : '0%',
                backgroundColor: '#27ae60'
              }} />
            </div>
          </div>
          <div style={styles.statItem}>
            <div style={styles.statLabel}>Rejected</div>
            <div style={styles.statValue}>{data?.rejected_decisions || 0}</div>
            <div style={styles.statBar}>
              <div style={{
                ...styles.statBarFill,
                width: data?.team_decisions ?
                  `${(data.rejected_decisions / data.team_decisions) * 100}%` : '0%',
                backgroundColor: '#e74c3c'
              }} />
            </div>
          </div>
          <div style={styles.statItem}>
            <div style={styles.statLabel}>Under Review</div>
            <div style={styles.statValue}>{data?.under_review || 0}</div>
            <div style={styles.statBar}>
              <div style={{
                ...styles.statBarFill,
                width: data?.team_decisions ?
                  `${(data.under_review / data.team_decisions) * 100}%` : '0%',
                backgroundColor: '#3498db'
              }} />
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}

const styles = {
  welcome: { color: '#2C3E50', fontSize: '24px', marginBottom: '4px' },
  role: { color: '#7f8c8d', marginBottom: '24px' },
  cards: { display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '16px', marginBottom: '32px' },
  card: { backgroundColor: '#2C3E50', color: 'white', padding: '20px', borderRadius: '10px', textAlign: 'center' },
  cardNumber: { fontSize: '32px', fontWeight: 'bold' },
  cardLabel: { fontSize: '12px', marginTop: '4px', opacity: 0.8 },
  section: { backgroundColor: 'white', padding: '24px', borderRadius: '10px', marginBottom: '24px', boxShadow: '0 2px 8px rgba(0,0,0,0.05)' },
  sectionTitle: { color: '#2C3E50', marginBottom: '16px', fontSize: '18px' },
  actions: { display: 'flex', gap: '12px', flexWrap: 'wrap' },
  actionBtn: { padding: '10px 20px', backgroundColor: '#2C3E50', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', fontSize: '14px' },
  statsGrid: { display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '20px' },
  statItem: { padding: '16px', backgroundColor: '#f8f9fa', borderRadius: '8px' },
  statLabel: { color: '#7f8c8d', fontSize: '13px', marginBottom: '8px' },
  statValue: { color: '#2C3E50', fontSize: '28px', fontWeight: 'bold', marginBottom: '8px' },
  statBar: { height: '6px', backgroundColor: '#ecf0f1', borderRadius: '3px', overflow: 'hidden' },
  statBarFill: { height: '100%', borderRadius: '3px' },
  center: { display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' },
};