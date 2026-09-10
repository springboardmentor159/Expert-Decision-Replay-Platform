import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { decisionService } from '../../services/decisionService';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import { useToast } from '../../components/common/Toast';
import { FileText, ArrowLeft, ArrowRight, Save, AlertCircle } from 'lucide-react';

const CATEGORIES = [
  'Technology',
  'Finance',
  'Operations',
  'Human Resources',
  'Security',
  'Product',
  'Infrastructure',
  'Strategy',
  'Architecture',
];

export const EditDecisionPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { addToast } = useToast();

  const [formData, setFormData] = useState({
    title: '',
    category: '',
    problem_statement: '',
    rationale: '',
  });

  const [errors, setErrors] = useState({});
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [serverError, setServerError] = useState('');

  useEffect(() => {
    const fetchDecision = async () => {
      setIsLoading(true);
      try {
        const dec = await decisionService.getDecisionById(id);
        setFormData({
          title: dec.title || '',
          category: dec.category || 'Architecture',
          problem_statement: dec.problem_statement || '',
          rationale: dec.rationale || '',
        });
      } catch (err) {
        setServerError(err.userMessage || 'Failed to load decision for editing');
      } finally {
        setIsLoading(false);
      }
    };

    fetchDecision();
  }, [id]);

  const validate = () => {
    const errs = {};
    if (!formData.title.trim()) errs.title = 'Title is required';
    if (!formData.category) errs.category = 'Category is required';
    if (!formData.problem_statement.trim()) {
      errs.problem_statement = 'Problem statement is required';
    }
    setErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setServerError('');
    if (!validate()) return;

    setIsSubmitting(true);
    try {
      await decisionService.updateDecision(id, {
        title: formData.title.trim(),
        category: formData.category,
        problem_statement: formData.problem_statement.trim(),
      });

      if (formData.rationale) {
        await decisionService.updateRationale(id, formData.rationale.trim());
      }

      addToast('Decision updated successfully!', 'success');
      navigate(`/decisions/${id}`);
    } catch (err) {
      setServerError(err.userMessage || 'Failed to update decision');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isLoading) return <LoadingSpinner message="Loading decision details..." />;

  return (
    <div style={{ maxWidth: '840px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '1.75rem' }}>
      <div>
        <Link
          to={`/decisions/${id}`}
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '6px',
            fontSize: '0.85rem',
            color: 'var(--text-muted)',
            marginBottom: '0.75rem',
          }}
        >
          <ArrowLeft size={16} /> Back to Decision
        </Link>
        <h1 className="page-title">
          <FileText size={28} />
          Edit Decision #{id}
        </h1>
      </div>

      {serverError && (
        <div className="alert alert-error">
          <AlertCircle size={18} />
          <span>{serverError}</span>
        </div>
      )}

      <div className="card">
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label form-label-required">Decision Title</label>
            <input
              type="text"
              className="form-input"
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
            />
            {errors.title && <span className="form-error">{errors.title}</span>}
          </div>

          <div className="form-group">
            <label className="form-label form-label-required">Category</label>
            <select
              className="form-select"
              value={formData.category}
              onChange={(e) => setFormData({ ...formData, category: e.target.value })}
            >
              {CATEGORIES.map((cat) => (
                <option key={cat} value={cat}>
                  {cat}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label className="form-label form-label-required">Problem Statement</label>
            <textarea
              className="form-textarea"
              value={formData.problem_statement}
              onChange={(e) => setFormData({ ...formData, problem_statement: e.target.value })}
              rows={4}
            />
            {errors.problem_statement && (
              <span className="form-error">{errors.problem_statement}</span>
            )}
          </div>

          <div className="form-group">
            <label className="form-label">Rationale & Objectives</label>
            <textarea
              className="form-textarea"
              value={formData.rationale}
              onChange={(e) => setFormData({ ...formData, rationale: e.target.value })}
              rows={4}
            />
          </div>

          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'flex-end',
              gap: '1rem',
              marginTop: '2rem',
              paddingTop: '1.25rem',
              borderTop: '1px solid var(--border-subtle)',
            }}
          >
            <Link to={`/decisions/${id}`} className="btn btn-secondary">
              Cancel
            </Link>
            <button type="submit" className="btn btn-primary" disabled={isSubmitting}>
              <Save size={16} />
              {isSubmitting ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
