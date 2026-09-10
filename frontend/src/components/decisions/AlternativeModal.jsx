import React, { useState, useEffect } from 'react';
import { Modal } from '../common/Modal';
import { alternativeService } from '../../services/alternativeService';
import { useToast } from '../common/Toast';

export const AlternativeModal = ({
  isOpen,
  onClose,
  decisionId,
  alternative = null, // null for create, object for edit
  onSuccess,
}) => {
  const { addToast } = useToast();
  const isEditing = !!alternative;

  const [formData, setFormData] = useState({
    name: '',
    description: '',
    pros: '',
    cons: '',
    estimated_cost: 0,
    feasibility_score: 3,
    risk_level: 'Medium',
  });

  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (alternative) {
      setFormData({
        name: alternative.name || '',
        description: alternative.description || '',
        pros: alternative.pros || '',
        cons: alternative.cons || '',
        estimated_cost: alternative.estimated_cost || 0,
        feasibility_score: alternative.feasibility_score || 3,
        risk_level: alternative.risk_level || 'Medium',
      });
    } else {
      setFormData({
        name: '',
        description: '',
        pros: '',
        cons: '',
        estimated_cost: 0,
        feasibility_score: 3,
        risk_level: 'Medium',
      });
    }
    setErrors({});
  }, [alternative, isOpen]);

  const validate = () => {
    const errs = {};
    if (!formData.name.trim()) errs.name = 'Alternative name is required';
    if (!formData.description.trim()) errs.description = 'Description is required';
    if (formData.estimated_cost < 0) errs.estimated_cost = 'Cost cannot be negative';
    
    // Part 18: Restrict feasibility score strictly to 1-5
    const score = Number(formData.feasibility_score);
    if (isNaN(score) || score < 1 || score > 5) {
      errs.feasibility_score = 'Feasibility score must be between 1 and 5';
    }

    setErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validate()) return;

    setIsSubmitting(true);
    try {
      const payload = {
        name: formData.name.trim(),
        description: formData.description.trim(),
        pros: formData.pros.trim() || null,
        cons: formData.cons.trim() || null,
        estimated_cost: Number(formData.estimated_cost) || 0,
        feasibility_score: Number(formData.feasibility_score),
        risk_level: formData.risk_level,
      };

      if (isEditing) {
        await alternativeService.updateAlternative(alternative.id, payload);
        addToast('Alternative updated successfully', 'success');
      } else {
        await alternativeService.createAlternative(decisionId, payload);
        addToast('Alternative added successfully', 'success');
      }

      onSuccess();
      onClose();
    } catch (err) {
      addToast(err.userMessage || 'Failed to save alternative', 'error');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={isEditing ? 'Edit Alternative' : 'Add New Alternative'}
      size="lg"
      footer={
        <>
          <button className="btn btn-secondary" onClick={onClose} disabled={isSubmitting}>
            Cancel
          </button>
          <button id="btn-save-alternative" className="btn btn-primary" onClick={handleSubmit} disabled={isSubmitting}>
            {isSubmitting ? 'Saving...' : isEditing ? 'Save Changes' : 'Save Alternative'}
          </button>
        </>
      }
    >
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label className="form-label form-label-required">Alternative Name</label>
          <input
            id="input-alt-name"
            type="text"
            className="form-input"
            placeholder="e.g. Migrate to AWS RDS PostgreSQL"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          />
          {errors.name && <span className="form-error">{errors.name}</span>}
        </div>

        <div className="form-group">
          <label className="form-label form-label-required">Description</label>
          <textarea
            id="input-alt-desc"
            className="form-textarea"
            placeholder="Detailed architectural approach, implementation plan, and scope..."
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            rows={3}
          />
          {errors.description && <span className="form-error">{errors.description}</span>}
        </div>

        <div className="form-row">
          <div className="form-group">
            <label className="form-label">Pros / Advantages</label>
            <textarea
              id="input-alt-pros"
              className="form-textarea"
              placeholder="High availability, automated backups, reduced maintenance..."
              value={formData.pros}
              onChange={(e) => setFormData({ ...formData, pros: e.target.value })}
              rows={3}
            />
          </div>

          <div className="form-group">
            <label className="form-label">Cons / Disadvantages</label>
            <textarea
              id="input-alt-cons"
              className="form-textarea"
              placeholder="Vendor lock-in, higher monthly cloud spend..."
              value={formData.cons}
              onChange={(e) => setFormData({ ...formData, cons: e.target.value })}
              rows={3}
            />
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label className="form-label">Estimated Cost ($)</label>
            <input
              id="input-alt-cost"
              type="number"
              min="0"
              step="100"
              className="form-input"
              value={formData.estimated_cost}
              onChange={(e) => setFormData({ ...formData, estimated_cost: e.target.value })}
            />
            {errors.estimated_cost && <span className="form-error">{errors.estimated_cost}</span>}
          </div>

          <div className="form-group">
            <label className="form-label form-label-required">
              Feasibility Score (1 = Lowest, 5 = Highest)
            </label>
            <select
              id="select-alt-feasibility"
              className="form-select"
              value={formData.feasibility_score}
              onChange={(e) => setFormData({ ...formData, feasibility_score: Number(e.target.value) })}
            >
              <option value={1}>1 - Very Low</option>
              <option value={2}>2 - Low</option>
              <option value={3}>3 - Moderate</option>
              <option value={4}>4 - High</option>
              <option value={5}>5 - Excellent</option>
            </select>
            {errors.feasibility_score && (
              <span className="form-error">{errors.feasibility_score}</span>
            )}
            <span className="form-hint">Score bounded to 1–5 per requirements</span>
          </div>

          <div className="form-group">
            <label className="form-label">Risk Level</label>
            <select
              id="select-alt-risk"
              className="form-select"
              value={formData.risk_level}
              onChange={(e) => setFormData({ ...formData, risk_level: e.target.value })}
            >
              <option value="Low">Low Risk</option>
              <option value="Medium">Medium Risk</option>
              <option value="High">High Risk</option>
            </select>
          </div>
        </div>
      </form>
    </Modal>
  );
};
