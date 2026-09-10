import React, { useState, useEffect } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { decisionService } from '../../services/decisionService';
import { StatusBadge } from '../../components/common/StatusBadge';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import { EmptyState } from '../../components/common/EmptyState';
import { Search, Filter, BookOpen, ArrowRight, ArrowLeft, Tag, Layers } from 'lucide-react';

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

const STATUSES = ['All Statuses', 'Approved', 'Under Review', 'Draft', 'Rejected', 'Archived'];

export const KnowledgeRepositoryPage = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const initialQuery = searchParams.get('q') || '';

  const [searchKeyword, setSearchKeyword] = useState(initialQuery);
  const [category, setCategory] = useState('All Categories');
  const [statusFilter, setStatusFilter] = useState('All Statuses');
  const [tagFilter, setTagFilter] = useState('');
  const [page, setPage] = useState(1);
  const [pageSize] = useState(9);

  const [data, setData] = useState({ items: [], total: 0, page: 1, page_size: 9 });
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchRepository = async () => {
    setIsLoading(true);
    setError('');
    try {
      const params = {
        page,
        page_size: pageSize,
      };
      if (searchKeyword.trim()) params.q = searchKeyword.trim();
      if (category !== 'All Categories') params.category = category;
      if (statusFilter !== 'All Statuses') params.status = statusFilter;
      if (tagFilter.trim()) params.tag = tagFilter.trim();

      const result = await decisionService.searchDecisions(params);
      setData(result);
    } catch (err) {
      setError(err.userMessage || 'Failed to search knowledge repository');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchRepository();
  }, [page, category, statusFilter]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    setPage(1);
    fetchRepository();
  };

  const totalPages = Math.ceil((data.total || 0) / pageSize) || 1;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.75rem' }}>
      {/* Header Banner */}
      <div
        style={{
          background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(6, 182, 212, 0.08) 100%)',
          border: '1px solid var(--border-subtle)',
          borderRadius: 'var(--radius-lg)',
          padding: '2rem',
        }}
      >
        <h1 className="page-title">
          <BookOpen size={28} />
          Organizational Knowledge Repository
        </h1>
        <p className="page-description">
          Search previous technical decisions, architecture trade-offs, and compliance rationales across teams.
        </p>

        {/* Global Search Input */}
        <form
          onSubmit={handleSearchSubmit}
          style={{ marginTop: '1.5rem', display: 'flex', gap: '0.75rem', maxWidth: '700px' }}
        >
          <div style={{ position: 'relative', flex: 1 }}>
            <Search
              size={18}
              style={{
                position: 'absolute',
                left: '1rem',
                top: '50%',
                transform: 'translateY(-50%)',
                color: 'var(--text-dim)',
              }}
            />
            <input
              type="text"
              className="form-input"
              placeholder="Search keyword in title, problem statement, rationale..."
              value={searchKeyword}
              onChange={(e) => setSearchKeyword(e.target.value)}
              style={{ paddingLeft: '2.75rem', height: '46px', fontSize: '0.95rem' }}
            />
          </div>
          <button type="submit" className="btn btn-primary btn-lg">
            Search
          </button>
        </form>
      </div>

      {/* Filter Bar */}
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
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
          <Filter size={16} /> Filters:
        </div>

        <select
          className="form-select"
          value={category}
          onChange={(e) => {
            setCategory(e.target.value);
            setPage(1);
          }}
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
          onChange={(e) => {
            setStatusFilter(e.target.value);
            setPage(1);
          }}
          style={{ width: '160px' }}
        >
          {STATUSES.map((st) => (
            <option key={st} value={st}>
              {st}
            </option>
          ))}
        </select>

        <div style={{ position: 'relative', width: '200px' }}>
          <Tag
            size={14}
            style={{
              position: 'absolute',
              left: '0.75rem',
              top: '50%',
              transform: 'translateY(-50%)',
              color: 'var(--text-dim)',
            }}
          />
          <input
            type="text"
            className="form-input"
            placeholder="Tag filter..."
            value={tagFilter}
            onChange={(e) => setTagFilter(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                setPage(1);
                fetchRepository();
              }
            }}
            style={{ paddingLeft: '2rem' }}
          />
        </div>

        <div style={{ marginLeft: 'auto', fontSize: '0.85rem', color: 'var(--text-dim)' }}>
          Found <strong style={{ color: 'var(--text-primary)' }}>{data.total || 0}</strong> decisions
        </div>
      </div>

      {/* Results Grid */}
      {isLoading ? (
        <LoadingSpinner message="Searching repository..." />
      ) : error ? (
        <div className="alert alert-error">
          <span>{error}</span>
        </div>
      ) : (data.items || []).length === 0 ? (
        <EmptyState
          icon={BookOpen}
          title="No repository matches found"
          description="Try broadening your search query or clearing category and status filters."
          actionText="Reset Search"
          onAction={() => {
            setSearchKeyword('');
            setCategory('All Categories');
            setStatusFilter('All Statuses');
            setTagFilter('');
            setPage(1);
          }}
        />
      ) : (
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))',
            gap: '1.25rem',
          }}
        >
          {(data.items || []).map((dec) => (
            <div
              key={dec.id}
              className="card"
              style={{
                display: 'flex',
                flexDirection: 'column',
                cursor: 'pointer',
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                <span className="badge badge-category">{dec.category}</span>
                <StatusBadge status={dec.status} />
              </div>

              <h3 style={{ fontSize: '1.1rem', color: 'var(--text-primary)', marginBottom: '0.5rem' }}>{dec.title}</h3>

              <p
                className="text-muted"
                style={{
                  fontSize: '0.85rem',
                  lineHeight: 1.6,
                  marginBottom: '1rem',
                  flexGrow: 1,
                  display: '-webkit-box',
                  WebkitLineClamp: 3,
                  WebkitBoxOrient: 'vertical',
                  overflow: 'hidden',
                }}
              >
                {dec.problem_statement}
              </p>

              {dec.tags && dec.tags.length > 0 && (
                <div style={{ display: 'flex', gap: '4px', flexWrap: 'wrap', marginBottom: '1rem' }}>
                  {dec.tags.slice(0, 4).map((t, idx) => (
                    <span
                      key={idx}
                      style={{
                        fontSize: '0.72rem',
                        background: 'var(--bg-elevated)',
                        padding: '1px 6px',
                        borderRadius: 'var(--radius-xs)',
                        color: 'var(--text-muted)',
                      }}
                    >
                      #{t}
                    </span>
                  ))}
                </div>
              )}

              <div
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  paddingTop: '0.75rem',
                  borderTop: '1px solid var(--border-subtle)',
                  fontSize: '0.78rem',
                  color: 'var(--text-dim)',
                }}
              >
                <span>{new Date(dec.created_at).toLocaleDateString()}</span>
                <Link
                  to={`/decisions/${dec.id}`}
                  className="btn btn-outline btn-sm"
                  style={{ gap: '4px' }}
                >
                  View Details <ArrowRight size={13} />
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Pagination Controls */}
      {totalPages > 1 && (
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '1rem', marginTop: '1rem' }}>
          <button
            className="btn btn-secondary btn-sm"
            disabled={page <= 1}
            onClick={() => setPage(page - 1)}
          >
            <ArrowLeft size={14} /> Previous
          </button>
          <span style={{ fontSize: '0.88rem', color: 'var(--text-muted)' }}>
            Page <strong style={{ color: 'var(--text-primary)' }}>{page}</strong> of {totalPages}
          </span>
          <button
            className="btn btn-secondary btn-sm"
            disabled={page >= totalPages}
            onClick={() => setPage(page + 1)}
          >
            Next <ArrowRight size={14} />
          </button>
        </div>
      )}
    </div>
  );
};
