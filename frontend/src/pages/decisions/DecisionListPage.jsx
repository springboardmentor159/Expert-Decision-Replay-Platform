import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { decisionService } from '../../services/decisionService';
import { StatusBadge } from '../../components/common/StatusBadge';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import { EmptyState } from '../../components/common/EmptyState';
import { SubmitApprovalModal } from '../../components/decisions/SubmitApprovalModal';
import { useAuth } from '../../context/AuthContext';
import { useToast } from '../../components/common/Toast';
import {
  FileText,
  PlusCircle,
  Search,
  Filter,
  Trash2,
  Edit,
  Send,
  Eye,
  Tag,
} from 'lucide-react';

const CATEGORIES = [
  'All Categories',
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

const STATUSES = ['All Statuses', 'Draft', 'Under Review', 'Approved', 'Rejected', 'Archived'];

export const DecisionListPage = () => {
  const { user, isAdmin, isManager } = useAuth();
  const navigate = useNavigate();
  const { addToast } = useToast();

  const [decisions, setDecisions] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  // Filters
  const [categoryFilter, setCategoryFilter] = useState('All Categories');
  const [statusFilter, setStatusFilter] = useState('All Statuses');
  const [searchQuery, setSearchQuery] = useState('');

  // Approval Submission Modal state
  const [submittingDecision, setSubmittingDecision] = useState(null);

  const fetchDecisions = async () => {
    setIsLoading(true);
    setError('');
    try {
      const params = {};
      if (categoryFilter !== 'All Categories') params.category = categoryFilter;
      if (statusFilter !== 'All Statuses') params.status = statusFilter;

      const data = await decisionService.getDecisions(params);
      setDecisions(data);
    } catch (err) {
      setError(err.userMessage || 'Failed to load decisions');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchDecisions();
  }, [categoryFilter, statusFilter]);

  // Client-side search filtering by title/tags
  const filteredDecisions = decisions.filter((d) => {
    if (!searchQuery.trim()) return true;
    const query = searchQuery.toLowerCase();
    const matchesTitle = d.title?.toLowerCase().includes(query);
    const matchesProblem = d.problem_statement?.toLowerCase().includes(query);
    const matchesCategory = d.category?.toLowerCase().includes(query);
    const matchesTags = (d.tags || []).some((t) => t.toLowerCase().includes(query));
    return matchesTitle || matchesProblem || matchesCategory || matchesTags;
  });

  const handleDelete = async (id, title) => {
    if (!window.confirm(`Are you sure you want to delete decision "${title}"?`)) {
      return;
    }
    try {
      await decisionService.deleteDecision(id);
      addToast('Decision deleted successfully', 'success');
      fetchDecisions();
    } catch (err) {
      addToast(err.userMessage || 'Failed to delete decision', 'error');
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Top Header */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '1rem',
        }}
      >
        <div>
          <h1 className="page-title">
            <FileText size={28} />
            Decision Management
          </h1>
          <p className="page-description">
            Explore, filter, and track technical and strategic decisions across the enterprise.
          </p>
        </div>

        <Link to="/decisions/create" className="btn btn-primary">
          <PlusCircle size={18} />
          <span>Create Decision</span>
        </Link>
      </div>

      {/* Filter & Search Bar */}
      <div
        className="card"
        style={{
          padding: '1rem 1.25rem',
          display: 'flex',
          alignItems: 'center',
          gap: '1rem',
          flexWrap: 'wrap',
        }}
      >
        <div style={{ position: 'relative', flex: '1 1 240px' }}>
          <Search
            size={16}
            style={{
              position: 'absolute',
              left: '0.85rem',
              top: '50%',
              transform: 'translateY(-50%)',
              color: 'var(--text-dim)',
            }}
          />
          <input
            type="text"
            className="form-input"
            placeholder="Search by title, tag, problem statement..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={{ paddingLeft: '2.4rem' }}
          />
        </div>

        <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
          <select
            className="form-select"
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            style={{ width: '180px' }}
          >
            {CATEGORIES.map((cat) => (
              <option key={cat} value={cat}>
                {cat}
              </option>
            ))}
          </select>

          <select
            className="form-select"
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            style={{ width: '160px' }}
          >
            {STATUSES.map((st) => (
              <option key={st} value={st}>
                {st}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Main Decisions Table */}
      {isLoading ? (
        <LoadingSpinner message="Loading decisions..." />
      ) : error ? (
        <div className="alert alert-error">
          <span>{error}</span>
        </div>
      ) : filteredDecisions.length === 0 ? (
        <EmptyState
          title="No decisions found"
          description="No decisions match the current filter criteria or keyword search."
          actionText="Clear Filters"
          onAction={() => {
            setCategoryFilter('All Categories');
            setStatusFilter('All Statuses');
            setSearchQuery('');
          }}
        />
      ) : (
        <div className="table-container">
          <table className="table">
            <thead>
              <tr>
                <th>Decision Title</th>
                <th>Category</th>
                <th>Status</th>
                <th>Created Date</th>
                <th>Tags</th>
                <th style={{ textAlign: 'right' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredDecisions.map((dec) => {
                const canEditOrDelete =
                  dec.created_by === user?.id || isAdmin || isManager;
                const canSubmit =
                  (dec.status === 'Draft' || dec.status === 'Rejected') &&
                  canEditOrDelete;

                return (
                  <tr key={dec.id}>
                    <td>
                      <div className="table-cell-title">{dec.title}</div>
                      <p
                        className="text-muted"
                        style={{
                          fontSize: '0.8rem',
                          maxWidth: '380px',
                          whiteSpace: 'nowrap',
                          overflow: 'hidden',
                          textOverflow: 'ellipsis',
                        }}
                      >
                        {dec.problem_statement}
                      </p>
                    </td>
                    <td>
                      <span className="badge badge-category">{dec.category}</span>
                    </td>
                    <td>
                      <StatusBadge status={dec.status} />
                    </td>
                    <td style={{ fontSize: '0.82rem', color: 'var(--text-dim)' }}>
                      {new Date(dec.created_at).toLocaleDateString()}
                    </td>
                    <td>
                      <div style={{ display: 'flex', gap: '4px', flexWrap: 'wrap' }}>
                        {(dec.tags || []).slice(0, 3).map((t, idx) => (
                          <span
                            key={idx}
                            style={{
                              fontSize: '0.72rem',
                              background: 'var(--bg-card-muted)',
                              padding: '1px 6px',
                              borderRadius: 'var(--radius-xs)',
                              color: 'var(--text-muted)',
                            }}
                          >
                            #{t}
                          </span>
                        ))}
                      </div>
                    </td>
                    <td style={{ textAlign: 'right' }}>
                      <div style={{ display: 'inline-flex', gap: '0.4rem' }}>
                        <Link
                          to={`/decisions/${dec.id}`}
                          className="btn btn-secondary btn-sm"
                          title="View complete details"
                        >
                          <Eye size={15} />
                        </Link>

                        {canSubmit && (
                          <button
                            className="btn btn-primary btn-sm"
                            title="Submit for Review"
                            onClick={() => setSubmittingDecision(dec)}
                          >
                            <Send size={14} />
                            <span>Submit</span>
                          </button>
                        )}

                        {canEditOrDelete && (
                          <>
                            <Link
                              to={`/decisions/${dec.id}/edit`}
                              className="btn btn-secondary btn-sm"
                              title="Edit decision"
                            >
                              <Edit size={14} />
                            </Link>
                            <button
                              className="btn btn-secondary btn-sm"
                              title="Delete decision"
                              onClick={() => handleDelete(dec.id, dec.title)}
                              style={{ color: '#f87171' }}
                            >
                              <Trash2 size={14} />
                            </button>
                          </>
                        )}
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* Submission Modal */}
      {submittingDecision && (
        <SubmitApprovalModal
          isOpen={!!submittingDecision}
          onClose={() => setSubmittingDecision(null)}
          decisionId={submittingDecision.id}
          decisionTitle={submittingDecision.title}
          onSuccess={fetchDecisions}
        />
      )}
    </div>
  );
};
