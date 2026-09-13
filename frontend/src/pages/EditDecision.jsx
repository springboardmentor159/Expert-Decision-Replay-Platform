import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { getDecision, updateDecision } from '../services/api';
import Layout from '../components/Layout';

export default function EditDecision() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    title: '', problem_statement: '', category: '', rationale: '',
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => { fetchDecision(); }, [id]);

  const fetchDecision = async () => {
    try {
      const response = await getDecision(id);
      const d = response.data;
      setFormData({
        title: d.title || '',
        problem_statement: d.problem_statement || '',
        category: d.category || '',
        rationale: d.rationale || '',
      });
    } catch (err) {
      setError('Failed to load decision');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    if (!formData.title || !formData.problem_statement || !formData.category) {
      setError('Title, problem statement and category are required');
      return;
    }
    setSaving(true);
    try {
      await updateDecision(id, formData);
      alert('Decision updated successfully!');
      navigate(`/decisions/${id}`);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to update decision');
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <Layout><div style={styles.center}>Loading...</div></Layout>;

  return (
    <Layout>
      <div style={styles.card}>
        <div style={styles.cardHeader}>
          <h2 style={styles.title}>Edit Decision</h2>
          <button style={styles.backBtn}
            onClick={() => navigate(`/decisions/${id}`)}>← Back</button>
        </div>

        {error && <div style={styles.error}>{error}</div>}

        <form onSubmit={handleSubmit}>
          <div style={styles.field}>
            <label style={styles.label}>Decision Title *</label>
            <input name="title" value={formData.title}
              onChange={handleChange} style={styles.input}
              placeholder="Enter decision title" />
          </div>
          <div style={styles.field}>
            <label style={styles.label}>Category *</label>
            <select name="category" value={formData.category}
              onChange={handleChange} style={styles.input}>
              <option value="">Select Category</option>
              <option value="Technology">Technology</option>
              <option value="Finance">Finance</option>
              <option value="Operations">Operations</option>
              <option value="HR">HR</option>
              <option value="Marketing">Marketing</option>
              <option value="Strategy">Strategy</option>
              <option value="Other">Other</option>
            </select>
          </div>
          <div style={styles.field}>
            <label style={styles.label}>Problem Statement *</label>
            <textarea name="problem_statement" value={formData.problem_statement}
              onChange={handleChange} style={styles.textarea}
              placeholder="Describe the problem" rows={4} />
          </div>
          <div style={styles.field}>
            <label style={styles.label}>Rationale</label>
            <textarea name="rationale" value={formData.rationale}
              onChange={handleChange} style={styles.textarea}
              placeholder="Explain the rationale" rows={3} />
          </div>
          <div style={styles.buttons}>
            <button type="button" style={styles.cancelBtn}
              onClick={() => navigate(`/decisions/${id}`)}>Cancel</button>
            <button type="submit" style={styles.submitBtn} disabled={saving}>
              {saving ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        </form>
      </div>
    </Layout>
  );
}

const styles = {
  card: { backgroundColor: 'white', padding: '32px', borderRadius: '12px', boxShadow: '0 2px 8px rgba(0,0,0,0.05)', maxWidth: '800px', margin: '0 auto' },
  cardHeader: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' },
  title: { color: '#2C3E50', fontSize: '22px', margin: 0 },
  backBtn: { padding: '8px 16px', backgroundColor: '#ecf0f1', border: 'none', borderRadius: '6px', cursor: 'pointer', fontSize: '14px' },
  error: { backgroundColor: '#fde8e8', color: '#c0392b', padding: '12px', borderRadius: '6px', marginBottom: '16px', fontSize: '14px' },
  field: { marginBottom: '20px' },
  label: { display: 'block', marginBottom: '6px', color: '#2C3E50', fontWeight: '600', fontSize: '14px' },
  input: { width: '100%', padding: '10px', borderRadius: '6px', border: '1px solid #ddd', fontSize: '14px', boxSizing: 'border-box' },
  textarea: { width: '100%', padding: '10px', borderRadius: '6px', border: '1px solid #ddd', fontSize: '14px', boxSizing: 'border-box', resize: 'vertical' },
  buttons: { display: 'flex', gap: '12px', justifyContent: 'flex-end', marginTop: '24px' },
  cancelBtn: { padding: '10px 24px', backgroundColor: '#ecf0f1', border: 'none', borderRadius: '6px', cursor: 'pointer', fontSize: '14px' },
  submitBtn: { padding: '10px 24px', backgroundColor: '#2C3E50', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', fontSize: '14px' },
  center: { display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' },
};