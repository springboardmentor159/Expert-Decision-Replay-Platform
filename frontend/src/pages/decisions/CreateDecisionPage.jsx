import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { decisionService } from '../../services/decisionService';
import { useToast } from '../../components/common/Toast';
import { FileText, ArrowLeft, ArrowRight, PlusCircle, AlertCircle } from 'lucide-react';

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

export const CreateDecisionPage = () => {
  const navigate = useNavigate();
  const { addToast } = useToast();

  const [formData, setFormData] = useState({
    title: '',
    category: 'Architecture',
    problem_statement: '',
    rationale: '',
    tags: '',
  });

  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [serverError, setServerError] = useState('');

  const validate = () => {
    const errs = {};
    if (!formData.title.trim()) {
      errs.title = 'Decision Title is required';
    } else if (formData.title.trim().length < 5) {
      errs.title = 'Title should be at least 5 characters';
    }

    if (!formData.category) {
      errs.category = 'Category is required';
    }

    if (!formData.problem_statement.trim()) {
      errs.problem_statement = 'Problem statement is required';
    } else if (formData.problem_statement.trim().length < 15) {
      errs.problem_statement = 'Please provide a more descriptive problem statement (min 15 chars)';
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
      // 1. Create Decision
      const newDecision = await decisionService.createDecision({
        title: formData.title.trim(),
        category: formData.category,
        problem_statement: formData.problem_statement.trim(),
      });

      // 2. If rationale was provided, save rationale
      if (formData.rationale.trim()) {
        try {
          await decisionService.updateRationale(newDecision.id, formData.rationale.trim());
        } catch (ratErr) {
          console.warn('Rationale update note:', ratErr);
        }
      }

      // 3. If tags were entered, assign tags
      if (formData.tags.trim()) {
        const tagList = formData.tags
          .split(',')
          .map((t) => t.trim())
          .filter(Boolean);
        if (tagList.length > 0) {
          try {
            await decisionService.assignTags(newDecision.id, tagList);
          } catch (tagErr) {
            console.warn('Tag assignment note:', tagErr);
          }
        }
      }

      addToast('Decision successfully created! You can now add alternatives and start collaboration.', 'success');
      // Redirect to the Decision Details page
      navigate(`/decisions/${newDecision.id}`);
    } catch (err) {
      setServerError(err.userMessage || 'Failed to create decision.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div style={{ maxWidth: '840px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '1.75rem' }}>
      {/* Top Header */}
      <div>
        <Link
          to="/decisions"
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '6px',
            fontSize: '0.85rem',
            color: 'var(--text-muted)',
            marginBottom: '0.75rem',
          }}
        >
          <ArrowLeft size={16} /> Back to Decisions
        </Link>
        <h1 className="page-title">
          <FileText size={28} />
          Create New Decision
        </h1>
        <p className="page-description">
          Initiate a new architectural, technical, or strategic proposal for organizational evaluation.
        </p>
      </div>

      {serverError && (
        <div className="alert alert-error">
          <AlertCircle size={18} />
          <span>{serverError}</span>
        </div>
      )}

      {/* Decision Creation Form */}
      <div className="card">
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label form-label-required">Decision Title</label>
            <input
              type="text"
              className="form-input"
              placeholder="e.g., Adopt Event-Driven Microservices Architecture for Payment Processing"
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
            {errors.category && <span className="form-error">{errors.category}</span>}
          </div>

          <div className="form-group">
            <label className="form-label form-label-required">Problem Statement & Context</label>
            <textarea
              className="form-textarea"
              placeholder="Describe the problem, business drivers, background context, and why a decision must be made now..."
              value={formData.problem_statement}
              onChange={(e) => setFormData({ ...formData, problem_statement: e.target.value })}
              rows={4}
            />
            {errors.problem_statement && (
              <span className="form-error">{errors.problem_statement}</span>
            )}
            <span className="form-hint">
              Explain current bottlenecks, latency, scaling challenges, or business requirements.
            </span>
          </div>

          <div className="form-group">
            <label className="form-label">Rationale & Objectives</label>
            <textarea
              className="form-textarea"
              placeholder="What core objectives, evaluation criteria, and constraints will guide this decision?"
              value={formData.rationale}
              onChange={(e) => setFormData({ ...formData, rationale: e.target.value })}
              rows={4}
            />
            <span className="form-hint">
              Define target SLAs, cost limits, compliance requirements, or risk boundaries.
            </span>
          </div>

          <div className="form-group">
            <label className="form-label">Tags (comma-separated)</label>
            <input
              type="text"
              className="form-input"
              placeholder="e.g., microservices, aws, kafka, payment-gateway, v2"
              value={formData.tags}
              onChange={(e) => setFormData({ ...formData, tags: e.target.value })}
            />
            <span className="form-hint">Keywords used for repository search and filtering</span>
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
            <Link to="/decisions" className="btn btn-secondary">
              Cancel
            </Link>
            <button type="submit" className="btn btn-primary btn-lg" disabled={isSubmitting}>
              {isSubmitting ? 'Creating Decision...' : 'Save & Continue to Details'}
              <ArrowRight size={18} />
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
