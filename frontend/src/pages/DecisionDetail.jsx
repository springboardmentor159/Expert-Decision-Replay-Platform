import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import {
  getDecision, getAlternatives, getVersions,
  getHistory, submitDecision, getThreads
} from '../services/api';
import Layout from '../components/Layout';

export default function DecisionDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [decision, setDecision] = useState(null);
  const [alternatives, setAlternatives] = useState([]);
  const [versions, setVersions] = useState([]);
  const [history, setHistory] = useState([]);
  const [threads, setThreads] = useState([]);
  const [activeTab, setActiveTab] = useState('info');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => { fetchAll(); }, [id]);

  const fetchAll = async () => {
    try {
      const [decRes, altRes, verRes, hisRes, thrRes] = await Promise.all([
        getDecision(id),
        getAlternatives(id),
        getVersions(id),
        getHistory(id),
        getThreads(id),
      ]);
      setDecision(decRes.data);
      setAlternatives(altRes.data);
      setVersions(verRes.data);
      setHistory(hisRes.data.history || []);
      setThreads(thrRes.data);
    } catch (err) {
      setError('Failed to load decision details');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async () => {
    if (!window.confirm('Submit this decision for review?')) return;
    try {
      await submitDecision(id);
      fetchAll();
      alert('Decision submitted for review!');
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to submit');
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      'Draft': '#f39c12', 'Under Review': '#3498db',
      'Approved': '#27ae60', 'Rejected': '#e74c3c', 'Archived': '#95a5a6',
    };
    return colors[status] || '#95a5a6';
  };

  if (loading) return <Layout><div style={styles.center}>Loading decision...</div></Layout>;
  if (error) return <Layout><div style={styles.center}>{error}</div></Layout>;

  return (
    <Layout>
      {/* Header */}
      <div style={styles.header}>
        <div>
          <button style={styles.backBtn} onClick={() => navigate('/decisions')}>← Back</button>
          <h2 style={styles.title}>{decision?.title}</h2>
          <span style={{...styles.badge, backgroundColor: getStatusColor(decision?.status)}}>
            {decision?.status}
          </span>
          <span style={styles.category}>📁 {decision?.category}</span>
        </div>
        <div style={styles.headerActions}>
          {decision?.status === 'Draft' && (
            <>
              <button style={styles.editBtn}
                onClick={() => navigate(`/decisions/${id}/edit`)}>
                ✏️ Edit
              </button>
              <button style={styles.submitBtn} onClick={handleSubmit}>
                📤 Submit for Review
              </button>
            </>
          )}
        </div>
      </div>

      {/* Tabs */}
      <div style={styles.tabs}>
        {['info', 'alternatives', 'discussions', 'versions', 'history'].map(tab => (
          <button
            key={tab}
            style={{...styles.tab, ...(activeTab === tab ? styles.activeTab : {})}}
            onClick={() => setActiveTab(tab)}
          >
            {tab === 'info' && '📋 '}
            {tab === 'alternatives' && '🔄 '}
            {tab === 'discussions' && '💬 '}
            {tab === 'versions' && '📝 '}
            {tab === 'history' && '📅 '}
            {tab.charAt(0).toUpperCase() + tab.slice(1)}
            {tab === 'alternatives' && ` (${alternatives.length})`}
            {tab === 'discussions' && ` (${threads.length})`}
            {tab === 'versions' && ` (${versions.length})`}
          </button>
        ))}
        <button
          style={{...styles.tab, backgroundColor: '#27ae60', color: 'white'}}
          onClick={() => navigate(`/decisions/${id}/compare`)}
        >
          ⚖️ Compare
        </button>
      </div>

      {/* Tab Content */}
      <div style={styles.tabContent}>

        {/* Info Tab */}
        {activeTab === 'info' && (
          <div style={styles.card}>
            <h3 style={styles.sectionTitle}>Decision Information</h3>
            <div style={styles.infoGrid}>
              <div style={styles.infoItem}>
                <span style={styles.infoLabel}>Category</span>
                <span style={styles.infoValue}>{decision?.category}</span>
              </div>
              <div style={styles.infoItem}>
                <span style={styles.infoLabel}>Status</span>
                <span style={{
                  ...styles.badge,
                  backgroundColor: getStatusColor(decision?.status)
                }}>
                  {decision?.status}
                </span>
              </div>
              <div style={styles.infoItem}>
                <span style={styles.infoLabel}>Created By</span>
                <span style={styles.infoValue}>User #{decision?.created_by}</span>
              </div>
              <div style={styles.infoItem}>
                <span style={styles.infoLabel}>Created At</span>
                <span style={styles.infoValue}>
                  {new Date(decision?.created_at).toLocaleDateString()}
                </span>
              </div>
              <div style={styles.infoItem}>
                <span style={styles.infoLabel}>Last Updated</span>
                <span style={styles.infoValue}>
                  {new Date(decision?.updated_at).toLocaleDateString()}
                </span>
              </div>
            </div>
            <div style={styles.field}>
              <span style={styles.infoLabel}>Problem Statement</span>
              <p style={styles.infoText}>{decision?.problem_statement}</p>
            </div>
            {decision?.rationale && (
              <div style={styles.field}>
                <span style={styles.infoLabel}>Rationale</span>
                <p style={styles.infoText}>{decision?.rationale}</p>
              </div>
            )}
          </div>
        )}

        {/* Alternatives Tab */}
        {activeTab === 'alternatives' && (
          <div style={styles.card}>
            <div style={styles.sectionHeader}>
              <h3 style={styles.sectionTitle}>
                Alternatives ({alternatives.length})
              </h3>
              <button style={styles.addBtn}
                onClick={() => navigate(`/decisions/${id}/compare`)}>
                ⚖️ Compare All
              </button>
            </div>
            {alternatives.length === 0 ? (
              <p style={styles.empty}>No alternatives added yet.</p>
            ) : (
              <div style={styles.alternativeGrid}>
                {alternatives.map(alt => (
                  <div key={alt.id} style={styles.altCard}>
                    <h4 style={styles.altTitle}>{alt.name}</h4>
                    <p style={styles.altDesc}>{alt.description}</p>
                    <div style={styles.altStats}>
                      <div style={styles.altStat}>
                        <span style={styles.statLabel}>Cost</span>
                        <span style={styles.statValue}>${alt.estimated_cost}</span>
                      </div>
                      <div style={styles.altStat}>
                        <span style={styles.statLabel}>Feasibility</span>
                        <span style={{
                          ...styles.statValue,
                          color: alt.feasibility_score >= 4 ? '#27ae60' :
                            alt.feasibility_score >= 3 ? '#f39c12' : '#e74c3c'
                        }}>
                          {alt.feasibility_score}/5
                        </span>
                      </div>
                      <div style={styles.altStat}>
                        <span style={styles.statLabel}>Risk</span>
                        <span style={{
                          ...styles.statValue,
                          color: alt.risk_level === 'Low' ? '#27ae60' :
                            alt.risk_level === 'Medium' ? '#f39c12' : '#e74c3c'
                        }}>
                          {alt.risk_level}
                        </span>
                      </div>
                    </div>
                    <div style={styles.proscons}>
                      <div style={styles.pros}>✅ {alt.pros}</div>
                      <div style={styles.cons}>❌ {alt.cons}</div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Discussions Tab */}
        {activeTab === 'discussions' && (
          <div style={styles.card}>
            <div style={styles.sectionHeader}>
              <h3 style={styles.sectionTitle}>
                Discussions ({threads.length})
              </h3>
              <button style={styles.addBtn}
                onClick={() => navigate(`/decisions/${id}/discussions`)}>
                💬 Open Discussions
              </button>
            </div>
            {threads.length === 0 ? (
              <p style={styles.empty}>No discussions yet.</p>
            ) : (
              threads.map(thread => (
                <div key={thread.id} style={styles.threadCard}>
                  <h4 style={styles.threadTitle}>{thread.title}</h4>
                  <p style={styles.threadContent}>{thread.content}</p>
                  <div style={styles.threadFooter}>
                    <span style={styles.threadDate}>
                      {new Date(thread.created_at).toLocaleDateString()}
                    </span>
                    <button style={styles.viewCommentsBtn}
                      onClick={() => navigate(`/decisions/${id}/discussions`)}>
                      View Comments →
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        )}

        {/* Versions Tab */}
        {activeTab === 'versions' && (
          <div style={styles.card}>
            <h3 style={styles.sectionTitle}>
              Version History ({versions.length})
            </h3>
            {versions.length === 0 ? (
              <p style={styles.empty}>No versions created yet.</p>
            ) : (
              <table style={styles.table}>
                <thead>
                  <tr>
                    <th style={styles.th}>Version</th>
                    <th style={styles.th}>Title</th>
                    <th style={styles.th}>Status</th>
                    <th style={styles.th}>Created At</th>
                  </tr>
                </thead>
                <tbody>
                  {versions.map(ver => (
                    <tr key={ver.id} style={styles.tr}>
                      <td style={styles.td}>
                        <span style={styles.versionBadge}>v{ver.version_number}</span>
                      </td>
                      <td style={styles.td}>{ver.title}</td>
                      <td style={styles.td}>{ver.status}</td>
                      <td style={styles.td}>
                        {new Date(ver.created_at).toLocaleDateString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        )}

        {/* History Tab */}
        {activeTab === 'history' && (
          <div style={styles.card}>
            <h3 style={styles.sectionTitle}>Decision Timeline</h3>
            {history.length === 0 ? (
              <p style={styles.empty}>No history available.</p>
            ) : (
              <div style={styles.timeline}>
                {history.map((item, index) => (
                  <div key={index} style={styles.timelineItem}>
                    <div style={styles.timelineDot} />
                    <div style={styles.timelineContent}>
                      <strong style={styles.timelineEvent}>{item.event}</strong>
                      <p style={styles.timelineDesc}>{item.description}</p>
                      <span style={styles.timelineDate}>
                        {new Date(item.timestamp).toLocaleString()}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </Layout>
  );
}

const styles = {
  header: { display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '24px' },
  headerActions: { display: 'flex', gap: '12px' },
  backBtn: { padding: '6px 14px', backgroundColor: '#ecf0f1', border: 'none', borderRadius: '6px', cursor: 'pointer', fontSize: '13px', marginBottom: '8px', display: 'block' },
  title: { color: '#2C3E50', fontSize: '24px', margin: '8px 0' },
  badge: { padding: '4px 12px', borderRadius: '20px', color: 'white', fontSize: '12px', fontWeight: '600', marginRight: '8px' },
  category: { color: '#7f8c8d', fontSize: '14px' },
  editBtn: { padding: '10px 20px', backgroundColor: '#f39c12', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer' },
  submitBtn: { padding: '10px 20px', backgroundColor: '#27ae60', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer' },
  tabs: { display: 'flex', gap: '4px', marginBottom: '20px', flexWrap: 'wrap' },
  tab: { padding: '10px 16px', border: 'none', borderRadius: '6px', cursor: 'pointer', backgroundColor: '#ecf0f1', color: '#7f8c8d', fontSize: '13px' },
  activeTab: { backgroundColor: '#2C3E50', color: 'white' },
  tabContent: {},
  card: { backgroundColor: 'white', padding: '24px', borderRadius: '10px', boxShadow: '0 2px 8px rgba(0,0,0,0.05)' },
  sectionTitle: { color: '#2C3E50', fontSize: '18px', marginBottom: '16px', margin: '0 0 16px' },
  sectionHeader: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' },
  infoGrid: { display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '16px', marginBottom: '20px' },
  infoItem: { display: 'flex', flexDirection: 'column', gap: '4px' },
  infoLabel: { color: '#7f8c8d', fontSize: '11px', fontWeight: '600', textTransform: 'uppercase' },
  infoValue: { color: '#2C3E50', fontSize: '14px', fontWeight: '500' },
  infoText: { color: '#2C3E50', fontSize: '14px', lineHeight: '1.6', marginTop: '8px' },
  field: { marginBottom: '16px' },
  alternativeGrid: { display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px' },
  altCard: { border: '1px solid #eee', borderRadius: '8px', padding: '16px', backgroundColor: '#f8f9fa' },
  altTitle: { color: '#2C3E50', fontSize: '16px', marginBottom: '8px', margin: '0 0 8px' },
  altDesc: { color: '#7f8c8d', fontSize: '13px', marginBottom: '12px' },
  altStats: { display: 'flex', gap: '16px', marginBottom: '12px' },
  altStat: { display: 'flex', flexDirection: 'column', gap: '2px' },
  statLabel: { color: '#7f8c8d', fontSize: '11px', fontWeight: '600' },
  statValue: { color: '#2C3E50', fontSize: '14px', fontWeight: '600' },
  proscons: { fontSize: '13px' },
  pros: { color: '#27ae60', marginBottom: '4px' },
  cons: { color: '#e74c3c' },
  addBtn: { padding: '8px 16px', backgroundColor: '#2C3E50', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', fontSize: '13px' },
  threadCard: { border: '1px solid #eee', borderRadius: '8px', padding: '16px', marginBottom: '12px' },
  threadTitle: { color: '#2C3E50', fontSize: '16px', margin: '0 0 8px' },
  threadContent: { color: '#7f8c8d', fontSize: '14px', marginBottom: '8px' },
  threadFooter: { display: 'flex', justifyContent: 'space-between', alignItems: 'center' },
  threadDate: { color: '#95a5a6', fontSize: '12px' },
  viewCommentsBtn: { padding: '4px 12px', backgroundColor: '#3498db', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', fontSize: '12px' },
  table: { width: '100%', borderCollapse: 'collapse' },
  th: { padding: '12px', textAlign: 'left', borderBottom: '2px solid #eee', color: '#7f8c8d', fontSize: '13px' },
  tr: { borderBottom: '1px solid #eee' },
  td: { padding: '12px', fontSize: '14px' },
  versionBadge: { backgroundColor: '#2C3E50', color: 'white', padding: '3px 8px', borderRadius: '4px', fontSize: '12px' },
  timeline: { paddingLeft: '24px' },
  timelineItem: { display: 'flex', gap: '16px', marginBottom: '20px' },
  timelineDot: { width: '12px', height: '12px', borderRadius: '50%', backgroundColor: '#2C3E50', flexShrink: 0, marginTop: '4px' },
  timelineContent: { flex: 1 },
  timelineEvent: { color: '#2C3E50', fontSize: '14px' },
  timelineDesc: { color: '#7f8c8d', fontSize: '13px', margin: '4px 0' },
  timelineDate: { color: '#95a5a6', fontSize: '12px' },
  empty: { color: '#7f8c8d', fontStyle: 'italic', textAlign: 'center', padding: '20px' },
  center: { display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' },
};