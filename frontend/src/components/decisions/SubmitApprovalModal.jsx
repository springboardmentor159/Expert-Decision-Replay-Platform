import React, { useState, useEffect } from 'react';
import { Modal } from '../common/Modal';
import { authService } from '../../services/authService';
import { approvalService } from '../../services/approvalService';
import { useToast } from '../common/Toast';

export const SubmitApprovalModal = ({ isOpen, onClose, decisionId, decisionTitle, onSuccess }) => {
  const { addToast } = useToast();
  const [users, setUsers] = useState([]);
  const [selectedReviewerId, setSelectedReviewerId] = useState('');
  const [approvalLevel, setApprovalLevel] = useState(1);
  const [comments, setComments] = useState('');
  const [isLoadingUsers, setIsLoadingUsers] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (isOpen) {
      const fetchUsers = async () => {
        setIsLoadingUsers(true);
        try {
          const userList = await authService.getUsers();
          // Filter reviewers, managers, or admins
          const eligible = userList.filter(
            (u) => u.role === 'Reviewer' || u.role === 'Manager' || u.role === 'Administrator'
          );
          setUsers(eligible.length > 0 ? eligible : userList);
          if (eligible.length > 0) {
            setSelectedReviewerId(eligible[0].id);
          }
        } catch (err) {
          console.error('Failed to load reviewers:', err);
        } finally {
          setIsLoadingUsers(false);
        }
      };
      fetchUsers();
    }
  }, [isOpen]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!selectedReviewerId) {
      setError('Please select a reviewer');
      return;
    }

    setIsSubmitting(true);
    setError('');

    try {
      await approvalService.submitDecision(decisionId, {
        reviewer_id: Number(selectedReviewerId),
        approval_level: Number(approvalLevel),
        comments: comments.trim() || undefined,
      });

      addToast('Decision successfully submitted for review!', 'success');
      onSuccess();
      onClose();
    } catch (err) {
      setError(err.userMessage || 'Failed to submit decision for approval');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Submit Decision for Review"
      size="md"
      footer={
        <>
          <button className="btn btn-secondary" onClick={onClose} disabled={isSubmitting}>
            Cancel
          </button>
          <button className="btn btn-primary" onClick={handleSubmit} disabled={isSubmitting}>
            {isSubmitting ? 'Submitting...' : 'Submit for Review'}
          </button>
        </>
      }
    >
      <form onSubmit={handleSubmit}>
        <p className="text-muted" style={{ fontSize: '0.88rem', marginBottom: '1.25rem' }}>
          Submitting <strong style={{ color: 'var(--text-primary)' }}>{decisionTitle}</strong> will transition its status to{' '}
          <span className="badge badge-under-review">Under Review</span> and notify the assigned reviewer.
        </p>

        {error && (
          <div className="alert alert-error">
            <span>{error}</span>
          </div>
        )}

        <div className="form-group">
          <label className="form-label form-label-required">Select Reviewer</label>
          {isLoadingUsers ? (
            <div className="text-muted" style={{ fontSize: '0.85rem' }}>Loading reviewers...</div>
          ) : (
            <select
              className="form-select"
              value={selectedReviewerId}
              onChange={(e) => setSelectedReviewerId(e.target.value)}
              required
            >
              <option value="">-- Choose Assigned Reviewer --</option>
              {users.map((u) => (
                <option key={u.id} value={u.id}>
                  {u.full_name} ({u.role} - {u.department || 'General'})
                </option>
              ))}
            </select>
          )}
        </div>

        <div className="form-group">
          <label className="form-label">Approval Level</label>
          <select
            className="form-select"
            value={approvalLevel}
            onChange={(e) => setApprovalLevel(Number(e.target.value))}
          >
            <option value={1}>Level 1 - Initial Technical Review</option>
            <option value={2}>Level 2 - Managerial Architecture Review</option>
            <option value={3}>Level 3 - Executive Board Sign-off</option>
          </select>
        </div>

        <div className="form-group">
          <label className="form-label">Submission Notes / Instructions</label>
          <textarea
            className="form-textarea"
            placeholder="Provide context, critical deadlines, or specific areas for the reviewer to focus on..."
            value={comments}
            onChange={(e) => setComments(e.target.value)}
            rows={3}
          />
        </div>
      </form>
    </Modal>
  );
};
