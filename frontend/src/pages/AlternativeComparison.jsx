import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { compareAlternatives, getDecision } from '../services/api';
import Layout from '../components/Layout';

export default function AlternativeComparison() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [comparison, setComparison] = useState(null);
  const [decision, setDecision] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => { fetchData(); }, [id]);

  const fetchData = async () => {
    try {
      const [compRes, decRes] = await Promise.all([
        compareAlternatives(id),
        getDecision(id),
      ]);
      setComparison(compRes.data);
      setDecision(decRes.data);
    } catch (err) {
      setError('Failed to load comparison data');
    } finally {
      setLoading(false);
    }
  };

  const getRiskColor = (risk) => {
    const colors = {
      'Low': '#27ae60', 'Medium': '#f39c12',
      'High': '#e74c3c', 'Critical': '#8e44ad'
    };
    return colors[risk] || '#95a5a6';
  };

  const getFeasibilityColor = (score) => {
    if (score >= 4) return '#27ae60';
    if (score >= 3) return '#f39c12';
    return '#e74c3c';
  };

  if (loading) return <Layout><div style={styles.center}>Loading comparison...</div></Layout>;
  if (error) return <Layout><div style={styles.center}>{error}</div></Layout>;

  const alternatives = comparison?.alternatives || [];

  return (
    <Layout>
      <div style={styles.header}>
        <button style={styles.backBtn}
          onClick={() => navigate(`/decisions/${id}`)}>
          ← Back to Decision
        </button>
        <h2 style={styles.title}>⚖️ Alternative Comparison</h2>
        <p style={styles.subtitle}>Decision: <strong>{decision?.title}</strong></p>
      </div>

      {alternatives.length === 0 ? (
        <div style={styles.empty}>
          <p>No alternatives found for this decision.</p>
          <p>Go back to the decision and add alternatives first.</p>
          <button style={styles.backBtnLarge}
            onClick={() => navigate(`/decisions/${id}`)}>
            ← Back to Decision
          </button>
        </div>
      ) : (
        <>
          {/* Comparison Table */}
          <div style={styles.tableWrapper}>
            <table style={styles.table}>
              <thead>
                <tr>
                  <th style={styles.criteriaHeader}>Criteria</th>
                  {alternatives.map(alt => (
                    <th key={alt.id} style={styles.altHeader}>
                      {alt.name}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                <tr style={styles.row}>
                  <td style={styles.criteria}><strong>💰 Estimated Cost</strong></td>
                  {alternatives.map(alt => (
                    <td key={alt.id} style={styles.cell}>
                      ${alt.estimated_cost?.toLocaleString() || 0}
                    </td>
                  ))}
                </tr>
                <tr style={styles.rowAlt}>
                  <td style={styles.criteria}><strong>📊 Feasibility Score</strong></td>
                  {alternatives.map(alt => (
                    <td key={alt.id} style={styles.cell}>
                      <span style={{
                        ...styles.scoreBadge,
                        backgroundColor: getFeasibilityColor(alt.feasibility_score)
                      }}>
                        {alt.feasibility_score}/5
                      </span>
                    </td>
                  ))}
                </tr>
                <tr style={styles.row}>
                  <td style={styles.criteria}><strong>⚠️ Risk Level</strong></td>
                  {alternatives.map(alt => (
                    <td key={alt.id} style={styles.cell}>
                      <span style={{
                        ...styles.riskBadge,
                        backgroundColor: getRiskColor(alt.risk_level)
                      }}>
                        {alt.risk_level}
                      </span>
                    </td>
                  ))}
                </tr>
                <tr style={styles.rowAlt}>
                  <td style={styles.criteria}><strong>✅ Pros</strong></td>
                  {alternatives.map(alt => (
                    <td key={alt.id} style={{...styles.cell, color: '#27ae60', textAlign: 'left'}}>
                      {alt.pros}
                    </td>
                  ))}
                </tr>
                <tr style={styles.row}>
                  <td style={styles.criteria}><strong>❌ Cons</strong></td>
                  {alternatives.map(alt => (
                    <td key={alt.id} style={{...styles.cell, color: '#e74c3c', textAlign: 'left'}}>
                      {alt.cons}
                    </td>
                  ))}
                </tr>
                <tr style={styles.rowAlt}>
                  <td style={styles.criteria}><strong>📝 Description</strong></td>
                  {alternatives.map(alt => (
                    <td key={alt.id} style={{...styles.cell, textAlign: 'left'}}>
                      {alt.description}
                    </td>
                  ))}
                </tr>
              </tbody>
            </table>
          </div>

          {/* Summary Cards */}
          <div style={styles.summarySection}>
            <h3 style={styles.summaryTitle}>Quick Summary</h3>
            <div style={styles.summaryGrid}>
              {alternatives.map(alt => (
                <div key={alt.id} style={styles.summaryCard}>
                  <h4 style={styles.summaryName}>{alt.name}</h4>
                  <div style={styles.summaryRow}>
                    <span style={styles.summaryLabel}>Cost</span>
                    <strong>${alt.estimated_cost}</strong>
                  </div>
                  <div style={styles.summaryRow}>
                    <span style={styles.summaryLabel}>Feasibility</span>
                    <strong style={{ color: getFeasibilityColor(alt.feasibility_score) }}>
                      {alt.feasibility_score}/5
                    </strong>
                  </div>
                  <div style={styles.summaryRow}>
                    <span style={styles.summaryLabel}>Risk</span>
                    <strong style={{ color: getRiskColor(alt.risk_level) }}>
                      {alt.risk_level}
                    </strong>
                  </div>
                  <div style={styles.recommendation}>
                    {alt.feasibility_score >= 4 && alt.risk_level === 'Low' && (
                      <span style={styles.recommended}>⭐ Recommended</span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </Layout>
  );
}

const styles = {
  header: { marginBottom: '24px' },
  backBtn: { padding: '8px 16px', backgroundColor: '#ecf0f1', border: 'none', borderRadius: '6px', cursor: 'pointer', fontSize: '14px', marginBottom: '12px', display: 'block' },
  title: { color: '#2C3E50', fontSize: '24px', margin: '8px 0 4px' },
  subtitle: { color: '#7f8c8d', fontSize: '14px', margin: 0 },
  tableWrapper: { backgroundColor: 'white', borderRadius: '12px', boxShadow: '0 2px 8px rgba(0,0,0,0.05)', overflowX: 'auto', marginBottom: '24px' },
  table: { width: '100%', borderCollapse: 'collapse' },
  criteriaHeader: { padding: '16px', backgroundColor: '#2C3E50', color: 'white', textAlign: 'left', fontSize: '14px', width: '180px' },
  altHeader: { padding: '16px', backgroundColor: '#2C3E50', color: 'white', textAlign: 'center', fontSize: '14px', minWidth: '200px' },
  row: { backgroundColor: 'white' },
  rowAlt: { backgroundColor: '#f8f9fa' },
  criteria: { padding: '16px', color: '#2C3E50', fontSize: '14px', borderRight: '2px solid #eee', verticalAlign: 'top' },
  cell: { padding: '16px', fontSize: '14px', color: '#2C3E50', textAlign: 'center', borderBottom: '1px solid #eee', verticalAlign: 'top' },
  scoreBadge: { padding: '4px 12px', borderRadius: '20px', color: 'white', fontSize: '14px', fontWeight: 'bold' },
  riskBadge: { padding: '4px 12px', borderRadius: '20px', color: 'white', fontSize: '12px', fontWeight: '600' },
  summarySection: { backgroundColor: 'white', padding: '24px', borderRadius: '12px', boxShadow: '0 2px 8px rgba(0,0,0,0.05)' },
  summaryTitle: { color: '#2C3E50', fontSize: '18px', marginBottom: '16px' },
  summaryGrid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' },
  summaryCard: { border: '1px solid #eee', borderRadius: '8px', padding: '16px' },
  summaryName: { color: '#2C3E50', fontSize: '16px', marginBottom: '12px', margin: '0 0 12px' },
  summaryRow: { display: 'flex', justifyContent: 'space-between', marginBottom: '8px', fontSize: '14px' },
  summaryLabel: { color: '#7f8c8d' },
  recommendation: { marginTop: '12px' },
  recommended: { backgroundColor: '#27ae60', color: 'white', padding: '4px 10px', borderRadius: '20px', fontSize: '12px', fontWeight: '600' },
  empty: { textAlign: 'center', padding: '60px', backgroundColor: 'white', borderRadius: '12px', color: '#7f8c8d' },
  backBtnLarge: { padding: '10px 20px', backgroundColor: '#2C3E50', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', marginTop: '12px' },
  center: { display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' },
};