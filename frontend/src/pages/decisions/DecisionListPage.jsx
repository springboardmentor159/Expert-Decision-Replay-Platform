import React, { useState, useEffect } from 'react';
import { decisionService } from '../../api/decisionService';
import { Card } from '../../components/common/Card';
import { Button } from '../../components/common/Button';
import { Input, Select } from '../../components/common/Input';
import { StatusBadge } from '../../components/common/Badge';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import { EmptyState } from '../../components/common/EmptyState';
import { Pagination } from '../../components/common/Pagination';
import { useToast } from '../../context/ToastContext';
import { useAuth } from '../../context/AuthContext';
import {
  PlusCircle,
  Search,
  Filter,
  Eye,
  Edit,
  Trash2,
  Send,
  SlidersHorizontal,
} from 'lucide-react';

export const DecisionListPage = ({ onNavigate }) => {
  const [decisions, setDecisions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');
  const [tagFilter, setTagFilter] = useState('');
  const [sortBy, setSortBy] = useState('created_at');
  const [sortOrder, setSortOrder] = useState('desc');
  const [searchQuery, setSearchQuery] = useState('');
  const [page, setPage] = useState(1);
  const [pageSize] = useState(10);
  const [total, setTotal] = useState(0);

  const { success, error } = useToast();
  const { user } = useAuth();

  const fetchDecisions = async () => {
    try {
      setLoading(true);
      if (searchQuery.trim() || statusFilter || categoryFilter || tagFilter) {
        const data = await decisionService.searchDecisions({
          q: searchQuery.trim() || undefined,
          status: statusFilter || undefined,
          category: categoryFilter || undefined,
          tag: tagFilter || undefined,
          sort: sortBy,
          order: sortOrder,
          page,
          page_size: pageSize,
        });
        setDecisions(data.items || data.results || []);
        setTotal(data.total || 0);
      } else {
        const data = await decisionService.getDecisions({
          sort: sortBy,
          order: sortOrder,
          page,
          page_size: pageSize,
        });
        setDecisions(data || []);
        setTotal(data.length);
      }
    } catch (err) {
      error(err.message || 'Failed to fetch decisions');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDecisions();
  }, [page, statusFilter, categoryFilter, tagFilter, sortBy, sortOrder]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    setPage(1);
    fetchDecisions();
  };

  const handleDelete = async (id, title) => {
    if (!window.confirm(`Are you sure you want to delete "${title}"?`)) return;
    try {
      await decisionService.deleteDecision(id);
      success(`Decision "${title}" deleted.`);
      fetchDecisions();
    } catch (err) {
      error(err.message || 'Failed to delete decision');
    }
  };

  return (
    <div>
      {/* Header Banner */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '1.5rem',
          flexWrap: 'wrap',
          gap: '1rem',
        }}
      >
        <div>
          <h2 style={{ fontSize: '1.75rem', fontWeight: 800, color: '#ffffff' }}>
            Decision Management
          </h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.925rem' }}>
            Explore, filter, and track technical architecture proposals through their review lifecycle.
          </p>
        </div>
        <Button
          variant="primary"
          icon={PlusCircle}
          onClick={() => onNavigate('create-decision')}
        >
          Create Decision
        </Button>
      </div>

      {/* Filter & Search Bar */}
      <Card style={{ marginBottom: '1.5rem' }}>
        <form onSubmit={handleSearchSubmit}>
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
              gap: '1rem',
              alignItems: 'flex-end',
            }}
          >
            <div>
              <Input
                label="Search Keyword"
                placeholder="Search title, problem, rationale..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>

            <div>
              <Select
                label="Filter Status"
                value={statusFilter}
                onChange={(e) => {
                  setStatusFilter(e.target.value);
                  setPage(1);
                }}
                placeholder="All Statuses"
                options={[
                  { value: 'Draft', label: 'Draft' },
                  { value: 'Under Review', label: 'Under Review' },
                  { value: 'Approved', label: 'Approved' },
                  { value: 'Rejected', label: 'Rejected' },
                  { value: 'Archived', label: 'Archived' },
                ]}
              />
            </div>

            <div>
              <Input
                label="Category"
                placeholder="e.g. Architecture, Database"
                value={categoryFilter}
                onChange={(e) => {
                  setCategoryFilter(e.target.value);
                  setPage(1);
                }}
              />
            </div>

            <div>
              <Input
                label="Tag"
                placeholder="e.g. Performance, Security"
                value={tagFilter}
                onChange={(e) => {
                  setTagFilter(e.target.value);
                  setPage(1);
                }}
              />
            </div>

            <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.25rem' }}>
              <Button type="submit" variant="primary" icon={Search} style={{ flex: 1 }}>
                Filter
              </Button>
              <Button
                type="button"
                variant="outline"
                onClick={() => {
                  setSearchQuery('');
                  setStatusFilter('');
                  setCategoryFilter('');
                  setTagFilter('');
                  setPage(1);
                }}
              >
                Reset
              </Button>
            </div>
          </div>
        </form>
      </Card>

      {/* Decisions List Table */}
      {loading ? (
        <LoadingSpinner message="Fetching decisions..." />
      ) : decisions.length === 0 ? (
        <EmptyState
          title="No decisions found"
          description="Try relaxing your filters or create a new technical decision record."
          actionLabel="Create New Decision"
          onAction={() => onNavigate('create-decision')}
        />
      ) : (
        <Card>
          <div className="table-container">
            <table className="custom-table">
              <thead>
                <tr>
                  <th>Decision Title</th>
                  <th>Category</th>
                  <th>Status</th>
                  <th>Tags</th>
                  <th>Created Date</th>
                  <th style={{ textAlign: 'right' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {decisions.map((dec) => (
                  <tr key={dec.id}>
                    <td style={{ fontWeight: 600, color: '#ffffff', maxWidth: '300px' }}>
                      {dec.title}
                    </td>
                    <td>{dec.category}</td>
                    <td>
                      <StatusBadge status={dec.status} />
                    </td>
                    <td>
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.25rem' }}>
                        {dec.tags && dec.tags.length > 0 ? (
                          dec.tags.map((t, idx) => (
                            <span
                              key={idx}
                              style={{
                                fontSize: '0.725rem',
                                background: 'rgba(255, 255, 255, 0.06)',
                                padding: '0.15rem 0.45rem',
                                borderRadius: 'var(--radius-sm)',
                                color: 'var(--accent-cyan)',
                              }}
                            >
                              #{typeof t === 'string' ? t : t.name}
                            </span>
                          ))
                        ) : (
                          <span style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>None</span>
                        )}
                      </div>
                    </td>
                    <td style={{ color: 'var(--text-muted)', fontSize: '0.825rem' }}>
                      {new Date(dec.created_at).toLocaleDateString()}
                    </td>
                    <td style={{ textAlign: 'right' }}>
                      <div style={{ display: 'inline-flex', gap: '0.5rem' }}>
                        <Button
                          variant="outline"
                          size="sm"
                          icon={Eye}
                          onClick={() => onNavigate('decision-detail', { id: dec.id })}
                        >
                          View
                        </Button>
                        {(user?.role === 'Administrator' || dec.created_by === user?.id) && (
                          <Button
                            variant="outline"
                            size="sm"
                            icon={Edit}
                            onClick={() => onNavigate('decision-detail', { id: dec.id, openEdit: true })}
                          >
                            Edit
                          </Button>
                        )}
                        {(user?.role === 'Administrator' || dec.created_by === user?.id) && (
                          <Button
                            variant="danger"
                            size="sm"
                            icon={Trash2}
                            onClick={() => handleDelete(dec.id, dec.title)}
                          />
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <Pagination
            page={page}
            pageSize={pageSize}
            totalItems={total}
            totalPages={Math.ceil(total / pageSize) || 1}
            onPageChange={(p) => setPage(p)}
          />
        </Card>
      )}
    </div>
  );
};
