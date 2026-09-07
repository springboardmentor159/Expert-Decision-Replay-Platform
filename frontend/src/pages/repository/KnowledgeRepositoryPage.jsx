import React, { useState, useEffect, useCallback } from 'react';
import { Search, BookOpen, Filter, ArrowRight, Tag, Calendar, Layers } from 'lucide-react';
import { decisionsApi } from '../../api/decisions';
import { useNotification } from '../../context/NotificationContext';
import { StatusBadge } from '../../components/common/StatusBadge';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import { EmptyState } from '../../components/common/EmptyState';
import { Pagination } from '../../components/common/Pagination';

export function KnowledgeRepositoryPage({ onSelectDecision }) {
  const { error } = useNotification();
  const [results, setResults] = useState([]);
  const [total, setTotal] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);

  // Filters
  const [query, setQuery] = useState('');
  const [category, setCategory] = useState('');
  const [status, setStatus] = useState('');
  const [tag, setTag] = useState('');

  const executeSearch = useCallback(async () => {
    setLoading(true);
    try {
      const data = await decisionsApi.searchDecisions({
        q: query.trim() || undefined,
        category: category || undefined,
        status: status || undefined,
        tag: tag.trim() || undefined,
        page,
        page_size: 9,
      });

      setResults(data.results || data.items || []);
      setTotal(data.total || 0);
      setTotalPages(data.total_pages || 1);
    } catch (err) {
      error(err.message || 'Search failed');
    } finally {
      setLoading(false);
    }
  }, [query, category, status, tag, page, error]);

  useEffect(() => {
    executeSearch();
  }, [executeSearch]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    setPage(1);
    executeSearch();
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.75rem' }}>
      {/* Knowledge Repository Hero */}
      <div style={{
        background: 'radial-gradient(ellipse at center, var(--primary-light), transparent 70%), var(--bg-card)',
        padding: '2.5rem 2rem',
        borderRadius: '16px',
        border: '1px solid var(--border-color)',
        textAlign: 'center',
        boxShadow: 'var(--shadow-sm)',
      }}>
        <div style={{
          width: '50px',
          height: '50px',
          borderRadius: '50%',
          background: 'var(--primary)',
          color: '#fff',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          margin: '0 auto 1rem',
          boxShadow: '0 4px 14px var(--primary-glow)',
        }}>
          <BookOpen size={24} />
        </div>
        <h1 style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>Organizational Knowledge Repository</h1>
        <p style={{ color: 'var(--text-secondary)', maxWidth: '600px', margin: '0 auto 1.5rem', fontSize: '0.95rem' }}>
          Explore previous architectural deliberations, trade-off matrices, and lessons learned across your enterprise.
        </p>

        {/* Global Search Bar */}
        <form onSubmit={handleSearchSubmit} style={{ maxWidth: '680px', margin: '0 auto', display: 'flex', gap: '0.5rem' }}>
          <div style={{ flex: 1, position: 'relative' }}>
            <Search size={20} style={{
              position: 'absolute',
              left: '14px',
              top: '50%',
              transform: 'translateY(-50%)',
              color: 'var(--text-muted)',
            }} />
            <input
              type="text"
              className="form-input"
              style={{ paddingLeft: '2.75rem', height: '48px', fontSize: '1rem' }}
              placeholder="Search previous decisions, technologies, or keywords..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
          </div>
          <button type="submit" className="btn btn-primary" style={{ height: '48px', padding: '0 1.5rem' }}>
            Search
          </button>
        </form>
      </div>

      {/* Quick Filters */}
      <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap', alignItems: 'center' }}>
        <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '4px' }}>
          <Filter size={15} /> Category:
        </span>
        {['', 'Architecture', 'Infrastructure', 'Technology', 'Process', 'Security'].map((cat) => (
          <button
            key={cat}
            onClick={() => { setCategory(cat); setPage(1); }}
            className={`btn btn-sm ${category === cat ? 'btn-primary' : 'btn-secondary'}`}
          >
            {cat || 'All'}
          </button>
        ))}

        <div style={{ marginLeft: 'auto', display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
          <select
            className="form-select"
            style={{ width: 'auto', padding: '0.35rem 0.75rem', fontSize: '0.8rem' }}
            value={status}
            onChange={(e) => { setStatus(e.target.value); setPage(1); }}
          >
            <option value="">All Statuses</option>
            <option value="Approved">Approved Only</option>
            <option value="Under Review">Under Review</option>
            <option value="Draft">Draft</option>
            <option value="Archived">Archived</option>
          </select>
        </div>
      </div>

      {/* Results Section */}
      {loading ? (
        <LoadingSpinner message="Searching repository knowledge items..." />
      ) : results.length === 0 ? (
        <EmptyState
          title="No repository records match your search"
          description="Try broadening your keywords or clearing selected filters."
        />
      ) : (
        <>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '1.25rem' }}>
            {results.map((item) => (
              <div
                key={item.id}
                className="card card-interactive"
                style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}
                onClick={() => onSelectDecision(item.id)}
              >
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.5rem' }}>
                    <span className="badge badge-role">{item.category || 'General'}</span>
                    <StatusBadge status={item.status} />
                  </div>
                  <h3 style={{ fontSize: '1.15rem', color: 'var(--text-primary)', marginBottom: '0.5rem' }}>
                    {item.title}
                  </h3>
                  <p style={{
                    fontSize: '0.85rem',
                    color: 'var(--text-secondary)',
                    lineHeight: 1.5,
                    display: '-webkit-box',
                    WebkitLineClamp: 3,
                    WebkitBoxOrient: 'vertical',
                    overflow: 'hidden',
                    marginBottom: '1rem',
                  }}>
                    {item.problem_statement}
                  </p>
                </div>

                <div style={{
                  borderTop: '1px solid var(--border-color)',
                  paddingTop: '0.75rem',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  fontSize: '0.8rem',
                  color: 'var(--text-muted)',
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                    <Calendar size={13} />
                    {new Date(item.created_at).toLocaleDateString()}
                  </div>
                  <span style={{ color: 'var(--primary)', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '4px' }}>
                    Explore <ArrowRight size={14} />
                  </span>
                </div>
              </div>
            ))}
          </div>

          <Pagination
            currentPage={page}
            totalPages={totalPages}
            onPageChange={(p) => setPage(p)}
          />
        </>
      )}
    </div>
  );
}
