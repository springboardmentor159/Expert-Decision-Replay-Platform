import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { searchDecisions } from '../services/api';
import Layout from '../components/Layout';

export default function KnowledgeRepository() {
  const navigate = useNavigate();
  const [decisions, setDecisions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [filters, setFilters] = useState({
    q: '', category: '', status: '',
    sort: 'created_at', order: 'desc',
  });

  useEffect(() => { fetchDecisions(); }, [page]);

  const fetchDecisions = async () => {
    setLoading(true);
    setError('');
    try {
      const params = { page, page_size: 10 };
      if (filters.q) params.q = filters.q;
      if (filters.category) params.category = filters.category;
      if (filters.status) params.status = filters.status;
      if (filters.sort) params.sort = filters.sort;
      if (filters.order) params.order = filters.order;

      const response = await searchDecisions(params);
      setDecisions(response.data.items || []);
      setTotal(response.data.total || 0);
    } catch (err) {
      setError('Failed to load decisions');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    setPage(1);
    fetchDecisions();
  };

  const handleFilterChange = (e) => {
    setFilters({ ...filters, [e.target.name]: e.target.value });
  };

  const getStatusColor = (status) => {
    const colors = {
      'Draft': '#f39c12', 'Under Review': '#3498db',
      'Approved': '#27ae60', 'Rejected': '#e74c3c', 'Archived': '#95a5a6',
    };
    return colors[status] || '#95a5a6';
  };

  const totalPages = Math.ceil(total / 10);

  return (
    <Layout>
      <h2 style={styles.title}>📚 Knowledge Repository</h2>
      <p style={styles.subtitle}>Search and explore previous decisions</p>

      {/* Search & Filters */}
      <div style={styles.filterCard}>
        <form onSubmit={handleSearch}>
          <div style={styles.searchRow}>
            <input
              name="q"
              value={filters.q}
              onChange={handleFilterChange}
              style={styles.searchInput}
              placeholder="🔍 Search decisions by title or description..."
            />
            <button type="submit" style={styles.searchBtn}>Search</button>
          </div>
          <div style={styles.filterGrid}>
            <div>
              <label style={styles.label}>Category</label>
              <select name="category" value={filters.category}
                onChange={handleFilterChange} style={styles.select}>
                <option value="">All Categories</option>
                <option value="Technology">Technology</option>
                <option value="Finance">Finance</option>
                <option value="Operations">Operations</option>
                <option value="HR">HR</option>
                <option value="Marketing">Marketing</option>
                <option value="Strategy">Strategy</option>
              </select>
            </div>
            <div>
              <label style={styles.label}>Status</label>
              <select name="status" value={filters.status}
                onChange={handleFilterChange} style={styles.select}>
                <option value="">All Status</option>
                <option value="Draft">Draft</option>
                <option value="Under Review">Under Review</option>
                <option value="Approved">Approved</option>
                <option value="Rejected">Rejected</option>
                <option value="Archived">Archived</option>
              </select>
            </div>
            <div>
              <label style={styles.label}>Sort By</label>
              <select name="sort" value={filters.sort}
                onChange={handleFilterChange} style={styles.select}>
                <option value="created_at">Created Date</option>
                <option value="updated_at">Updated Date</option>
                <option value="title">Title</option>
              </select>
            </div>
            <div>
              <label style={styles.label}>Order</label>
              <select name="order" value={filters.order}
                onChange={handleFilterChange} style={styles.select}>
                <option value="desc">Newest First</option>
                <option value="asc">Oldest First</option>
              </select>
            </div>
          </div>
        </form>
      </div>

      {/* Results count */}
      <div style={styles.resultsHeader}>
        <span style={styles.resultCount}>
          {loading ? 'Searching...' : `${total} decisions found`}
        </span>
        <button style={styles.clearBtn} onClick={() => {
          setFilters({ q: '', category: '', status: '', sort: 'created_at', order: 'desc' });
          setPage(1);
          setTimeout(fetchDecisions, 100);
        }}>
          Clear Filters
        </button>
      </div>

      {error && <div style={styles.error}>{error}</div>}

      {loading ? (
        <div style={styles.center}>Loading decisions...</div>
      ) : decisions.length === 0 ? (
        <div style={styles.empty}>
          <p>No decisions found matching your search.</p>
        </div>
      ) : (
        <>
          <div style={styles.decisionGrid}>
            {decisions.map(decision => (
              <div key={decision.id} style={styles.decisionCard}
                onClick={() => navigate(`/decisions/${decision.id}`)}>
                <div style={styles.cardTop}>
                  <h3 style={styles.decisionTitle}>{decision.title}</h3>
                  <span style={{
                    ...styles.statusBadge,
                    backgroundColor: getStatusColor(decision.status)
                  }}>
                    {decision.status}
                  </span>
                </div>
                <div style={styles.cardMeta}>
                  <span style={styles.metaItem}>📁 {decision.category}</span>
                  <span style={styles.metaItem}>
                    📅 {new Date(decision.created_at).toLocaleDateString()}
                  </span>
                </div>
                <div style={styles.cardFooter}>
                  <button style={styles.viewBtn}
                    onClick={(e) => {
                      e.stopPropagation();
                      navigate(`/decisions/${decision.id}`);
                    }}>
                    View Details →
                  </button>
                </div>
              </div>
            ))}
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div style={styles.pagination}>
              <button
                style={{...styles.pageBtn, opacity: page === 1 ? 0.5 : 1}}
                onClick={() => setPage(page - 1)}
                disabled={page === 1}>
                ← Previous
              </button>
              <span style={styles.pageInfo}>
                Page {page} of {totalPages}
              </span>
              <button
                style={{...styles.pageBtn, opacity: page === totalPages ? 0.5 : 1}}
                onClick={() => setPage(page + 1)}
                disabled={page === totalPages}>
                Next →
              </button>
            </div>
          )}
        </>
      )}
    </Layout>
  );
}

const styles = {
  title: { color: '#2C3E50', fontSize: '24px', margin: '0 0 4px' },
  subtitle: { color: '#7f8c8d', fontSize: '14px', marginBottom: '24px' },
  filterCard: { backgroundColor: 'white', padding: '24px', borderRadius: '12px', boxShadow: '0 2px 8px rgba(0,0,0,0.05)', marginBottom: '20px' },
  searchRow: { display: 'flex', gap: '12px', marginBottom: '16px' },
  searchInput: { flex: 1, padding: '12px', borderRadius: '8px', border: '1px solid #ddd', fontSize: '14px' },
  searchBtn: { padding: '12px 24px', backgroundColor: '#2C3E50', color: 'white', border: 'none', borderRadius: '8px', cursor: 'pointer', fontSize: '14px' },
  filterGrid: { display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px' },
  label: { display: 'block', marginBottom: '4px', color: '#2C3E50', fontWeight: '600', fontSize: '13px' },
  select: { width: '100%', padding: '8px', borderRadius: '6px', border: '1px solid #ddd', fontSize: '13px' },
  resultsHeader: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' },
  resultCount: { color: '#7f8c8d', fontSize: '14px' },
  clearBtn: { padding: '6px 14px', backgroundColor: '#ecf0f1', border: 'none', borderRadius: '6px', cursor: 'pointer', fontSize: '13px' },
  error: { backgroundColor: '#fde8e8', color: '#c0392b', padding: '12px', borderRadius: '6px', marginBottom: '16px' },
  decisionGrid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '16px', marginBottom: '24px' },
  decisionCard: { backgroundColor: 'white', borderRadius: '12px', padding: '20px', boxShadow: '0 2px 8px rgba(0,0,0,0.05)', cursor: 'pointer', border: '1px solid #eee' },
  cardTop: { display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '12px' },
  decisionTitle: { color: '#2C3E50', fontSize: '16px', margin: 0, flex: 1, marginRight: '8px' },
  statusBadge: { padding: '4px 10px', borderRadius: '20px', color: 'white', fontSize: '11px', fontWeight: '600', whiteSpace: 'nowrap' },
  cardMeta: { display: 'flex', gap: '16px', marginBottom: '16px' },
  metaItem: { color: '#7f8c8d', fontSize: '13px' },
  cardFooter: { borderTop: '1px solid #eee', paddingTop: '12px' },
  viewBtn: { padding: '6px 14px', backgroundColor: '#2C3E50', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', fontSize: '13px' },
  pagination: { display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '16px', marginTop: '24px' },
  pageBtn: { padding: '8px 20px', backgroundColor: '#2C3E50', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', fontSize: '14px' },
  pageInfo: { color: '#7f8c8d', fontSize: '14px' },
  empty: { textAlign: 'center', padding: '60px', backgroundColor: 'white', borderRadius: '12px', color: '#7f8c8d' },
  center: { textAlign: 'center', padding: '60px', color: '#7f8c8d' },
};