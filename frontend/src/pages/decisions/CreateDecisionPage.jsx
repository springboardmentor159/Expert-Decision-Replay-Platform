import React, { useState } from 'react';
import { ArrowLeft, Check, Plus, Trash2, Tag, AlertCircle, Sparkles } from 'lucide-react';
import { decisionsApi } from '../../api/decisions';
import { useNotification } from '../../context/NotificationContext';

export function CreateDecisionPage({ onCancel, onDecisionCreated }) {
  const { success, error } = useNotification();
  const [loading, setLoading] = useState(false);

  const [formData, setFormData] = useState({
    title: '',
    problem_statement: '',
    category: 'Architecture',
    rationale: '',
    stakeholders: '',
    evaluation_criteria: '',
    risks: '',
    tags: '',
  });

  const [errors, setErrors] = useState({});

  const validate = () => {
    const errs = {};
    if (!formData.title.trim()) {
      errs.title = 'Decision title is required';
    } else if (formData.title.length < 3) {
      errs.title = 'Title must be at least 3 characters long';
    }

    if (!formData.problem_statement.trim()) {
      errs.problem_statement = 'Problem statement is required';
    } else if (formData.problem_statement.length < 10) {
      errs.problem_statement = 'Please provide a meaningful problem statement (min 10 characters)';
    }

    if (!formData.category) {
      errs.category = 'Category selection is required';
    }

    setErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const handleChange = (field, value) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors((prev) => ({ ...prev, [field]: '' }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validate()) return;

    try {
      setLoading(true);

      // Construct payload
      const payload = {
        title: formData.title.trim(),
        problem_statement: formData.problem_statement.trim(),
        category: formData.category,
        rationale: formData.rationale.trim() || undefined,
      };

      // Create the decision
      const created = await decisionsApi.createDecision(payload);

      // Add tags if specified
      if (formData.tags.trim()) {
        const tagList = formData.tags.split(',').map((t) => t.trim()).filter(Boolean);
        for (const t of tagList) {
          try {
            await decisionsApi.addTag(created.id, t);
          } catch {
            // Non-critical tag addition
          }
        }
      }

      success('Decision successfully created in Draft status!');
      onDecisionCreated(created.id);
    } catch (err) {
      error(err.message || 'Failed to create decision');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '840px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <button className="btn btn-secondary btn-sm" onClick={onCancel}>
          <ArrowLeft size={16} /> Back to Decisions
        </button>
        <span className="badge badge-draft">Draft</span>
      </div>

      <div className="card" style={{ padding: '2rem' }}>
        <div style={{ marginBottom: '1.75rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '1rem' }}>
          <h1 style={{ fontSize: '1.5rem', marginBottom: '0.4rem' }}>Create New Decision</h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
            Formulate an audit-grade decision proposal with problem statements, rationale, and governance parameters.
          </p>
        </div>

        <form onSubmit={handleSubmit}>
          {/* Decision Title */}
          <div className="form-group">
            <label className="form-label">
              Decision Title <span style={{ color: 'var(--danger)' }}>*</span>
            </label>
            <input
              type="text"
              className="form-input"
              placeholder="e.g. Migration of Core Payment Service to Event-Driven Microservices"
              value={formData.title}
              onChange={(e) => handleChange('title', e.target.value)}
              disabled={loading}
            />
            {errors.title && <div className="form-error">{errors.title}</div>}
          </div>

          {/* Category & Tags Grid */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.25rem' }}>
            <div className="form-group">
              <label className="form-label">
                Category <span style={{ color: 'var(--danger)' }}>*</span>
              </label>
              <select
                className="form-select"
                value={formData.category}
                onChange={(e) => handleChange('category', e.target.value)}
                disabled={loading}
              >
                <option value="Architecture">Architecture</option>
                <option value="Infrastructure">Infrastructure</option>
                <option value="Technology">Technology</option>
                <option value="Process">Process</option>
                <option value="Security">Security</option>
                <option value="Operations">Operations</option>
              </select>
              {errors.category && <div className="form-error">{errors.category}</div>}
            </div>

            <div className="form-group">
              <label className="form-label">Tags (comma separated)</label>
              <input
                type="text"
                className="form-input"
                placeholder="e.g. cloud, postgres, latency, v2"
                value={formData.tags}
                onChange={(e) => handleChange('tags', e.target.value)}
                disabled={loading}
              />
            </div>
          </div>

          {/* Problem Statement */}
          <div className="form-group">
            <label className="form-label">
              Problem Statement <span style={{ color: 'var(--danger)' }}>*</span>
            </label>
            <textarea
              className="form-textarea"
              rows={4}
              placeholder="Describe the context, challenge, and why a formal architectural or business decision is required..."
              value={formData.problem_statement}
              onChange={(e) => handleChange('problem_statement', e.target.value)}
              disabled={loading}
            />
            {errors.problem_statement && <div className="form-error">{errors.problem_statement}</div>}
          </div>

          {/* Objectives & Rationale */}
          <div className="form-group">
            <label className="form-label">Objectives & Business Rationale</label>
            <textarea
              className="form-textarea"
              rows={3}
              placeholder="Detail the expected business outcomes, efficiency gains, SLA targets, or risk reductions..."
              value={formData.rationale}
              onChange={(e) => handleChange('rationale', e.target.value)}
              disabled={loading}
            />
          </div>

          {/* Stakeholders & Evaluation Criteria */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.25rem' }}>
            <div className="form-group">
              <label className="form-label">Key Stakeholders</label>
              <input
                type="text"
                className="form-input"
                placeholder="e.g. Lead Architect, Security Officer, VP Eng"
                value={formData.stakeholders}
                onChange={(e) => handleChange('stakeholders', e.target.value)}
                disabled={loading}
              />
            </div>

            <div className="form-group">
              <label className="form-label">Evaluation Criteria</label>
              <input
                type="text"
                className="form-input"
                placeholder="e.g. Total Cost, Feasibility, Latency < 50ms"
                value={formData.evaluation_criteria}
                onChange={(e) => handleChange('evaluation_criteria', e.target.value)}
                disabled={loading}
              />
            </div>
          </div>

          {/* Action Buttons */}
          <div style={{
            display: 'flex',
            justifyContent: 'flex-end',
            gap: '0.75rem',
            marginTop: '1.5rem',
            borderTop: '1px solid var(--border-color)',
            paddingTop: '1.25rem',
          }}>
            <button
              type="button"
              className="btn btn-secondary"
              onClick={onCancel}
              disabled={loading}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="btn btn-primary"
              disabled={loading}
            >
              {loading ? <span className="spinner" /> : <>Save & Proceed to Details <Check size={16} /></>}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
