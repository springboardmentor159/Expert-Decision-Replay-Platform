import React, { useState } from 'react';
import { decisionService } from '../../api/decisionService';
import { Card } from '../../components/common/Card';
import { Button } from '../../components/common/Button';
import { Input, TextArea, Select } from '../../components/common/Input';
import { useToast } from '../../context/ToastContext';
import { ArrowLeft, Save, Sparkles, Tag, AlertTriangle } from 'lucide-react';

export const CreateDecisionPage = ({ onNavigate }) => {
  const [formData, setFormData] = useState({
    title: '',
    category: 'Architecture',
    problem_statement: '',
    rationale: '',
    tags: '',
    stakeholders: '',
    evaluation_criteria: '',
    risks: '',
  });

  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});
  const { success, error } = useToast();

  const validate = () => {
    const errs = {};
    if (!formData.title.trim()) errs.title = 'Decision title is required.';
    else if (formData.title.length < 5) errs.title = 'Title should be at least 5 characters.';

    if (!formData.category.trim()) errs.category = 'Category is required.';

    if (!formData.problem_statement.trim()) errs.problem_statement = 'Problem statement is required.';
    else if (formData.problem_statement.length < 15) {
      errs.problem_statement = 'Please provide a descriptive problem statement (min 15 characters).';
    }

    setErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const handleChange = (field, value) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors((prev) => ({ ...prev, [field]: null }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validate()) return;

    setLoading(true);
    try {
      // 1. Create Decision
      const newDecision = await decisionService.createDecision({
        title: formData.title.trim(),
        category: formData.category.trim(),
        problem_statement: formData.problem_statement.trim(),
      });

      // 2. Set Rationale if provided
      if (formData.rationale.trim()) {
        await decisionService.updateRationale(newDecision.id, formData.rationale.trim());
      }

      // 3. Assign tags if provided (comma-separated)
      if (formData.tags.trim()) {
        const tagList = formData.tags
          .split(',')
          .map((t) => t.trim())
          .filter(Boolean);

        for (const tag of tagList) {
          try {
            await decisionService.assignTag(newDecision.id, tag);
          } catch (tErr) {
            console.warn('Tag assign error', tErr);
          }
        }
      }

      success(`Decision "${newDecision.title}" created successfully!`);
      onNavigate('decision-detail', { id: newDecision.id });
    } catch (err) {
      error(err.message || 'Failed to create decision record');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '900px', margin: '0 auto' }}>
      {/* Back button and page title */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1.5rem' }}>
        <Button
          variant="outline"
          size="sm"
          icon={ArrowLeft}
          onClick={() => onNavigate('decisions')}
        >
          Back to Decisions
        </Button>
        <div>
          <h2 style={{ fontSize: '1.65rem', fontWeight: 800, color: '#ffffff' }}>
            Author New Architecture Decision
          </h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
            Formulate the problem, document architectural constraints, and establish review context.
          </p>
        </div>
      </div>

      <Card>
        <form onSubmit={handleSubmit}>
          <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '1.25rem' }}>
            <Input
              id="dec-title"
              label="Decision Title"
              placeholder="e.g. Migrate Core Message Broker from RabbitMQ to Apache Kafka"
              value={formData.title}
              onChange={(e) => handleChange('title', e.target.value)}
              error={errors.title}
              required
            />

            <Select
              id="dec-category"
              label="Category"
              value={formData.category}
              onChange={(e) => handleChange('category', e.target.value)}
              options={[
                { value: 'Architecture', label: 'Architecture' },
                { value: 'Database', label: 'Database' },
                { value: 'Security', label: 'Security & Compliance' },
                { value: 'Infrastructure', label: 'Infrastructure & Cloud' },
                { value: 'Frontend', label: 'Frontend & UX' },
                { value: 'Integration', label: 'Integration & API' },
                { value: 'DevOps', label: 'DevOps & Tooling' },
              ]}
              required
            />
          </div>

          <TextArea
            id="dec-problem"
            label="Problem Statement & Context"
            placeholder="Describe the challenges, architectural pain points, or requirements necessitating this decision..."
            rows={4}
            value={formData.problem_statement}
            onChange={(e) => handleChange('problem_statement', e.target.value)}
            error={errors.problem_statement}
            required
          />

          <TextArea
            id="dec-rationale"
            label="Initial Decision Rationale (Optional)"
            placeholder="Explain why a particular technical direction or methodology is favored..."
            rows={3}
            value={formData.rationale}
            onChange={(e) => handleChange('rationale', e.target.value)}
          />

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.25rem' }}>
            <Input
              id="dec-stakeholders"
              label="Key Stakeholders"
              placeholder="e.g. Enterprise Architects, Security Ops, Data Platform Team"
              value={formData.stakeholders}
              onChange={(e) => handleChange('stakeholders', e.target.value)}
              helperText="Teams impacted by or responsible for this decision"
            />

            <Input
              id="dec-tags"
              label="Tags (Comma separated)"
              placeholder="e.g. streaming, latency, cost-efficiency"
              value={formData.tags}
              onChange={(e) => handleChange('tags', e.target.value)}
              helperText="Used for taxonomy indexing and search in the Knowledge Repository"
            />
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.25rem' }}>
            <TextArea
              id="dec-criteria"
              label="Evaluation Criteria"
              placeholder="e.g. Throughput > 50k eps, 99.99% availability, vendor lock-in risk..."
              rows={2}
              value={formData.evaluation_criteria}
              onChange={(e) => handleChange('evaluation_criteria', e.target.value)}
            />

            <TextArea
              id="dec-risks"
              label="Known Risks & Mitigations"
              placeholder="e.g. Cluster migration complexity, ops learning curve..."
              rows={2}
              value={formData.risks}
              onChange={(e) => handleChange('risks', e.target.value)}
            />
          </div>

          <div
            style={{
              display: 'flex',
              justifyContent: 'flex-end',
              gap: '1rem',
              marginTop: '1.5rem',
              paddingTop: '1.25rem',
              borderTop: '1px solid var(--border-subtle)',
            }}
          >
            <Button
              type="button"
              variant="secondary"
              onClick={() => onNavigate('decisions')}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              variant="primary"
              loading={loading}
              icon={Save}
            >
              Save & Initialize Decision
            </Button>
          </div>
        </form>
      </Card>
    </div>
  );
};
