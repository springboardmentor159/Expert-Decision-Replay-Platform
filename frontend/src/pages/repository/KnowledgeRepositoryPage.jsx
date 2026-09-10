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
import {
  Search,
  BookOpen,
  Sparkles,
  Filter,
  ArrowUpRight,
  Clock,
  Tag as TagIcon,
  Layers,
} from 'lucide-react';

export const KnowledgeRepositoryPage = ({ onNavigate }) => {
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [category, setCategory] = useState('');
  const [status, setStatus] = useState('');
  const [tag, setTag] = useState('');
  const [sortBy, setSortBy] = useState('created_at');
  const [sortOrder, setSortOrder] = useState('desc');
  const [page, setPage] = useState(1);
  const [pageSize] = useState(9);
  const [total, setTotal] = useState(0);

  const { error } = useToast();

  const handleSearch = async (e) => {
    if (e) e.preventDefault();
    try {
      setLoading(true);
      const res = await decisionService.searchDecisions({
        q: searchQuery.trim() || undefined,
        category: category.trim() || undefined,
        status: status || undefined,
        tag: tag.trim() || undefined,
        sort: sortBy,
        order: sortOrder,
        page,
        page_size: pageSize,
      });

      setResults(res.items || res.results || []);
      setTotal(res.total || 0);
    } catch (err) {
      error(err.message || 'Search query failed');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    handleSearch();
  }, [page, category, status, tag, sortBy, sortOrder]);

  return (
    <div>
      {/* Search Header Banner */}
      <div
        style={{
          textAlign: 'center',
          maxWidth: '750px',
          margin: '0 auto 2.5rem',
          paddingTop: '1rem',
        }}
      >
        <div
          style={{
            width: '52px',
            height: '52px',
            borderRadius: '50%',
            background: 'linear-gradient(135deg, var(--accent-blue), var(--accent-cyan))',
            display: 'inline-flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#ffffff',
            boxShadow: 'var(--shadow-glow-cyan)',
            marginBottom: '1rem',
          }}
        >
          <BookOpen size={26} />
        </div>
        <h2 style={{ fontSize: '2rem', fontWeight: 800, color: '#ffffff', letterSpacing: '-0.02em' }}>
          Knowledge Repository & Search
        </h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: '1rem', marginTop: '0.5rem' }}>
          Discover prior architectural deliberations, evaluated trade-offs, and precedent decisions across your organization.
        </p>
      </div>

      {/* Advanced Filter Box */}
      <Card style={{ marginBottom: '2rem' }}>
        <form onSubmit={(e) => { setPage(1); handleSearch(e); }}>
          <div style={{ display: 'flex', gap: '0.75rem', marginBottom: '1.25rem' }}>
            <div style={{ flex: 1 }}>
              <Input
                placeholder="Search by keywords, architectural patterns, technologies, or rationale..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
            <Button type="submit" variant="primary" icon={Search} style={{ minWidth: '120px' }}>
              Search
            </Button>
          </div>

          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
              gap: '1rem',
            }}
          >
            <Select
              label="Status"
              value={status}
              onChange={(e) => { setStatus(e.target.value); setPage(1); }}
              placeholder="All Statuses"
              options={[
                { value: 'Approved', label: 'Approved (Precedents)' },
                { value: 'Under Review', label: 'Under Review' },
                { value: 'Draft', label: 'Draft' },
                { value: 'Rejected', label: 'Rejected' },
                { value: 'Archived', label: 'Archived' },
              ]}
            />

            <Input
              label="Category"
              placeholder="e.g. Architecture, Database"
              value={category}
              onChange={(e) => { setCategory(e.target.value); setPage(1); }}
            />

            <Input
              label="Tag"
              placeholder="e.g. Kafka, Security"
              value={tag}
              onChange={(e) => { setTag(e.target.value); setPage(1); }}
            />

            <Select
              label="Sort By"
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              options={[
                { value: 'created_at', label: 'Creation Date' },
                { value: 'updated_at', label: 'Last Updated' },
                { value: 'title', label: 'Title (Alphabetical)' },
              ]}
            />

            <Select
              label="Order"
              value={sortOrder}
              onChange={(e) => setSortOrder(e.target.value)}
              options={[
                { value: 'desc', label: 'Descending' },
                { value: 'asc', label: 'Ascending' },
              ]}
            />
          </div>
        </form>
      </Card>

      {/* Results Grid */}
      {loading ? (
        <LoadingSpinner message="Searching organizational knowledge repository..." />
      ) : results.length === 0 ? (
        <EmptyState
          icon={Search}
          title="No repository records found"
          description="Try broadening your search keywords or removing specific filters."
        />
      ) : (
        <div>
          <div style={{ marginBottom: '1rem', color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
            Found <strong style={{ color: '#ffffff' }}>{total}</strong> documented decisions matching your criteria:
          </div>

          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fill, minmax(340px, 1fr))',
              gap: '1.25rem',
            }}
          >
            {results.map((item) => (
              <Card
                key={item.id}
                onClick={() => onNavigate('decision-detail', { id: item.id })}
                style={{
                  display: 'flex',
                  flexDirection: 'column',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.75rem' }}>
                  <span
                    style={{
                      fontSize: '0.75rem',
                      fontWeight: 700,
                      color: 'var(--accent-cyan)',
                      textTransform: 'uppercase',
                      letterSpacing: '0.04em',
                    }}
                  >
                    {item.category}
                  </span>
                  <StatusBadge status={item.status} />
                </div>

                <h4 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#ffffff', marginBottom: '0.75rem', lineHeight: 1.3 }}>
                  {item.title}
                </h4>

                <p
                  style={{
                    color: 'var(--text-secondary)',
                    fontSize: '0.875rem',
                    lineHeight: 1.5,
                    marginBottom: '1rem',
                    flex: 1,
                    display: '-webkit-box',
                    WebkitLineClamp: 3,
                    WebkitBoxOrient: 'vertical',
                    overflow: 'hidden',
                  }}
                >
                  {item.problem_statement || 'No detailed problem statement provided.'}
                </p>

                {/* Tags preview */}
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.35rem', marginBottom: '1rem' }}>
                  {item.tags && item.tags.length > 0 ? (
                    item.tags.slice(0, 3).map((t, idx) => (
                      <span
                        key={idx}
                        style={{
                          fontSize: '0.725rem',
                          background: 'rgba(255, 255, 255, 0.05)',
                          padding: '0.15rem 0.5rem',
                          borderRadius: 'var(--radius-sm)',
                          color: '#a5b4fc',
                        }}
                      >
                        #{typeof t === 'string' ? t : t.name}
                      </span>
                    ))
                  ) : null}
                </div>

                {/* Card footer */}
                <div
                  style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    paddingTop: '0.75rem',
                    borderTop: '1px solid var(--border-subtle)',
                    fontSize: '0.8rem',
                    color: 'var(--text-muted)',
                  }}
                >
                  <span>{item.created_at ? new Date(item.created_at).toLocaleDateString() : ''}</span>
                  <span style={{ display: 'flex', alignItems: 'center', gap: '4px', color: '#60a5fa', fontWeight: 600 }}>
                    Replay Record <ArrowUpRight size={14} />
                  </span>
                </div>
              </Card>
            ))}
          </div>

          <Pagination
            page={page}
            pageSize={pageSize}
            totalItems={total}
            totalPages={Math.ceil(total / pageSize) || 1}
            onPageChange={(p) => setPage(p)}
          />
        </div>
      )}
    </div>
  );
};
