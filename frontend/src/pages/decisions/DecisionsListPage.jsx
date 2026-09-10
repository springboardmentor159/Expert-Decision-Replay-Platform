import React, { useState, useEffect, useCallback } from 'react';
import {
  Search,
  Plus,
  Filter,
  Eye,
  Trash2,
  Send,
  Calendar,
  Tag,
  AlertTriangle,
  FolderOpen,
} from 'lucide-react';
import { decisionsApi } from '../../api/decisions';
import { useAuth } from '../../context/AuthContext';
import { useNotification } from '../../context/NotificationContext';
import { StatusBadge } from '../../components/common/StatusBadge';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import { EmptyState } from '../../components/common/EmptyState';
import { Pagination } from '../../components/common/Pagination';
import { Modal } from '../../components/common/Modal';

export function DecisionsListPage({
  onSelectDecision,
  onNavigateCreate,
  initialFilter = {},
  title = 'Decisions Directory',
  subtitle,
  onlyMine = false,
}) {
  const { user, isEmployee, isManager, isAdmin } = useAuth();
  const { success, error } = useNotification();

  const [decisions, setDecisions] = useState([]);
  const [total, setTotal] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);

  // Filters
  const [searchQuery, setSearchQuery] = useState(initialFilter.q || '');
  const [category, setCategory] = useState(initialFilter.category || '');
  const [status, setStatus] = useState(initialFilter.status || '');
  const [tag, setTag] = useState(initialFilter.tag || '');

  // Delete modal state
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [decisionToDelete, setDecisionToDelete] = useState(null);
  const [submittingId, setSubmittingId] = useState(null);

  const fetchDecisions = useCallback(async () => {
    setLoading(true);
    try {
      const res = await decisionsApi.getDecisions({
        q: searchQuery.trim() || undefined,
        category: category || undefined,
        status: status || undefined,
        tag: tag.trim() || undefined,
        created_by: onlyMine ? user?.id : (initialFilter.created_by || undefined),
        page,
        page_size: 10,
      });

      setDecisions(res.items || []);
      setTotal(res.total || 0);
      setTotalPages(res.total_pages || 1);
    } catch (err) {
      error(err.message || 'Failed to load decisions');
    } finally {
      setLoading(false);
    }
  }, [searchQuery, category, status, tag, page, onlyMine, user?.id, initialFilter.created_by, error]);

  useEffect(() => {
    fetchDecisions();
  }, [fetchDecisions]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    setPage(1);
    fetchDecisions();
  };

  const handleResetFilters = () => {
    setSearchQuery('');
    setCategory('');
    setStatus('');
    setTag('');
    setPage(1);
  };

  const handleSubmitForReview = async (id, e) => {
    e.stopPropagation();
    try {
      setSubmittingId(id);
      await decisionsApi.submitDecision(id);
      success('Decision successfully submitted for review!');
      fetchDecisions();
    } catch (err) {
      error(err.message || 'Could not submit decision');
    } finally {
      setSubmittingId(null);
    }
  };

  const confirmDelete = async () => {
    if (!decisionToDelete) return;
    try {
      await decisionsApi.deleteDecision(decisionToDelete.id);
      success('Decision deleted successfully');
      setDeleteModalOpen(false);
      setDecisionToDelete(null);
      fetchDecisions();
    } catch (err) {
      error(err.message || 'Failed to delete decision');
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Top Header */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '1rem',
      }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '0.25rem' }}>
            <h1 style={{ fontSize: '1.75rem', margin: 0 }}>{title}</h1>
            {onlyMine && (
              <span className="badge badge-role" style={{ fontSize: '0.78rem' }}>
                👤 Authored by You
              </span>
            )}
          </div>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
            {subtitle || (onlyMine
              ? `Showing your personal architectural and engineering decisions (${total} total)`
              : `Manage, review, and track organizational decision artifacts (${total} total)`)}
          </p>
        </div>
        {(isEmployee || isManager || isAdmin) && (
          <button onClick={onNavigateCreate} className="btn btn-primary">
            <Plus size={18} /> Create Decision
          </button>
        )}
      </div>

      {/* Filter Toolbar */}
      <div className="card" style={{ padding: '1.25rem' }}>
        <form onSubmit={handleSearchSubmit} style={{ display: 'flex', flexWrap: 'wrap', gap: '0.75rem', alignItems: 'center' }}>
          <div style={{ flex: '1 1 240px', position: 'relative' }}>
            <Search size={18} style={{
              position: 'absolute',
              left: '12px',
              top: '50%',
              transform: 'translateY(-50%)',
              color: 'var(--text-muted)',
            }} />
            <input
              type="text"
              className="form-input"
              style={{ paddingLeft: '2.4rem' }}
              placeholder="Search by title, problem, or rationale..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>

          <select
            className="form-select"
            style={{ width: 'auto', minWidth: '160px' }}
            value={category}
            onChange={(e) => { setCategory(e.target.value); setPage(1); }}
          >
            <option value="">All Categories</option>
            <option value="Architecture">Architecture</option>
            <option value="Infrastructure">Infrastructure</option>
            <option value="Technology">Technology</option>
            <option value="Process">Process</option>
            <option value="Security">Security</option>
            <option value="Operations">Operations</option>
          </select>

          <select
            className="form-select"
            style={{ width: 'auto', minWidth: '160px' }}
            value={status}
            onChange={(e) => { setStatus(e.target.value); setPage(1); }}
          >
            <option value="">All Statuses</option>
            <option value="Draft">Draft</option>
            <option value="Under Review">Under Review</option>
            <option value="Approved">Approved</option>
            <option value="Rejected">Rejected</option>
            <option value="Archived">Archived</option>
          </select>

          <div style={{ position: 'relative', width: 'auto', minWidth: '140px' }}>
            <Tag size={16} style={{
              position: 'absolute',
              left: '10px',
              top: '50%',
              transform: 'translateY(-50%)',
              color: 'var(--text-muted)',
            }} />
            <input
              type="text"
              className="form-input"
              style={{ paddingLeft: '2rem' }}
              placeholder="Filter by tag..."
              value={tag}
              onChange={(e) => { setTag(e.target.value); setPage(1); }}
            />
          </div>

          <button type="submit" className="btn btn-primary btn-sm">
            <Filter size={16} /> Filter
          </button>

          {(searchQuery || category || status || tag) && (
            <button
              type="button"
              className="btn btn-secondary btn-sm"
              onClick={handleResetFilters}
            >
              Reset
            </button>
          )}
        </form>
      </div>

      {/* Decisions Content Table */}
      {loading ? (
        <LoadingSpinner message="Loading decisions..." />
      ) : decisions.length === 0 ? (
        <EmptyState
          title={onlyMine ? "You haven't created any decisions yet" : "No decisions match your filter criteria"}
          description={
            onlyMine
              ? "You have not authored any decision records. Click below to draft your first decision."
              : (searchQuery || category || status || tag
                ? "Try clearing search filters or create a new decision."
                : "No decisions found in your organization. Get started by creating one.")
          }
          action={
            (isEmployee || isManager || isAdmin) && (
              <button onClick={onNavigateCreate} className="btn btn-primary btn-sm">
                <Plus size={16} /> {onlyMine ? "Create Your First Decision" : "Create Decision"}
              </button>
            )
          }
        />
      ) : (
        <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
          <div className="table-container" style={{ border: 'none', borderRadius: 0 }}>
            <table className="table">
              <thead>
                <tr>
                  <th>Decision Title & Summary</th>
                  <th>Category</th>
                  <th>Status</th>
                  <th>Created Date</th>
                  <th style={{ textAlign: 'right' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {decisions.map((decision) => {
                  const canModify =
                    decision.created_by === user?.id ||
                    user?.role === 'Manager' ||
                    user?.role === 'Administrator';
                  const canSubmit =
                    canModify && (decision.status === 'Draft' || decision.status === 'Rejected');

                  return (
                    <tr
                      key={decision.id}
                      style={{ cursor: 'pointer' }}
                      onClick={() => onSelectDecision(decision.id)}
                    >
                      <td>
                        <div style={{ fontWeight: 600, color: 'var(--text-primary)', fontSize: '0.95rem' }}>
                          {decision.title}
                        </div>
                        <div style={{
                          fontSize: '0.775rem',
                          color: 'var(--text-secondary)',
                          display: '-webkit-box',
                          WebkitLineClamp: 1,
                          WebkitBoxOrient: 'vertical',
                          overflow: 'hidden',
                          maxWidth: '450px',
                          marginTop: '2px',
                        }}>
                          {decision.problem_statement}
                        </div>
                        {decision.tags && decision.tags.length > 0 && (
                          <div style={{ display: 'flex', gap: '0.35rem', marginTop: '0.4rem' }}>
                            {decision.tags.map((t) => (
                              <span key={t.id} style={{
                                fontSize: '0.7rem',
                                background: 'var(--bg-hover)',
                                border: '1px solid var(--border-color)',
                                padding: '1px 6px',
                                borderRadius: '4px',
                                color: 'var(--text-muted)',
                              }}>
                                #{t.name}
                              </span>
                            ))}
                          </div>
                        )}
                      </td>
                      <td>
                        <span className="badge badge-role">
                          {decision.category || 'General'}
                        </span>
                      </td>
                      <td>
                        <StatusBadge status={decision.status} />
                      </td>
                      <td>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                          <Calendar size={14} />
                          {new Date(decision.created_at).toLocaleDateString()}
                        </div>
                      </td>
                      <td style={{ textAlign: 'right' }}>
                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: '0.5rem' }} onClick={(e) => e.stopPropagation()}>
                          <button
                            className="btn btn-secondary btn-sm"
                            onClick={() => onSelectDecision(decision.id)}
                            title="View Decision Details"
                          >
                            <Eye size={15} /> View
                          </button>

                          {canSubmit && (
                            <button
                              className="btn btn-primary btn-sm"
                              disabled={submittingId === decision.id}
                              onClick={(e) => handleSubmitForReview(decision.id, e)}
                              title="Submit for Review"
                            >
                              <Send size={14} />
                              {submittingId === decision.id ? 'Submitting...' : 'Submit'}
                            </button>
                          )}

                          {canModify && (
                            <button
                              className="btn btn-secondary btn-sm"
                              style={{ color: 'var(--danger)', borderColor: 'rgba(239, 68, 68, 0.3)' }}
                              onClick={() => {
                                setDecisionToDelete(decision);
                                setDeleteModalOpen(true);
                              }}
                              title="Delete Decision"
                            >
                              <Trash2 size={15} />
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          <Pagination
            currentPage={page}
            totalPages={totalPages}
            onPageChange={(newPage) => setPage(newPage)}
          />
        </div>
      )}

      {/* Delete Confirmation Modal */}
      <Modal
        isOpen={deleteModalOpen}
        onClose={() => setDeleteModalOpen(false)}
        title="Confirm Decision Deletion"
        footer={
          <>
            <button className="btn btn-secondary" onClick={() => setDeleteModalOpen(false)}>
              Cancel
            </button>
            <button className="btn btn-danger" onClick={confirmDelete}>
              Delete Decision
            </button>
          </>
        }
      >
        <div style={{ display: 'flex', gap: '1rem', alignItems: 'flex-start' }}>
          <div style={{
            background: 'var(--danger-light)',
            color: 'var(--danger)',
            padding: '0.75rem',
            borderRadius: '50%',
          }}>
            <AlertTriangle size={24} />
          </div>
          <div>
            <p style={{ fontWeight: 600, color: 'var(--text-primary)', marginBottom: '0.4rem' }}>
              Are you sure you want to delete this decision?
            </p>
            <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
              "{decisionToDelete?.title}". This will remove all associated alternatives, criteria, and threads. This action cannot be undone.
            </p>
          </div>
        </div>
      </Modal>
    </div>
  );
}
