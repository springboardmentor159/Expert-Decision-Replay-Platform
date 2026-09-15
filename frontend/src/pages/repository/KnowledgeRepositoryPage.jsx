import React, { useState, useEffect, useCallback } from 'react';
import { Search, BookOpen, Filter, ArrowRight, Tag, Calendar, Layers, Paperclip, Download, FileText } from 'lucide-react';
import { decisionsApi } from '../../api/decisions';
import { attachmentsApi } from '../../api/attachments';
import { useNotification } from '../../context/NotificationContext';
import { StatusBadge } from '../../components/common/StatusBadge';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import { EmptyState } from '../../components/common/EmptyState';
import { Pagination } from '../../components/common/Pagination';

export function KnowledgeRepositoryPage({ onSelectDecision }) {
  const { error } = useNotification();
  const [activeTab, setActiveTab] = useState('decisions'); // 'decisions' | 'documents'

  // Decisions state
  const [results, setResults] = useState([]);
  const [total, setTotal] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [page, setPage] = useState(1);
  const [loadingDecisions, setLoadingDecisions] = useState(true);

  // Decision filters
  const [query, setQuery] = useState('');
  const [category, setCategory] = useState('');
  const [status, setStatus] = useState('');
  const [tag, setTag] = useState('');

  // Documents archive state
  const [documents, setDocuments] = useState([]);
  const [docSearch, setDocSearch] = useState('');
  const [loadingDocs, setLoadingDocs] = useState(false);

  const executeSearch = useCallback(async () => {
    setLoadingDecisions(true);
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
      setLoadingDecisions(false);
    }
  }, [query, category, status, tag, page, error]);

  const loadDocuments = useCallback(async () => {
    setLoadingDocs(true);
    try {
      const docs = await attachmentsApi.getArchive(100);
      setDocuments(docs || []);
    } catch (err) {
      error(err.message || 'Failed to load document archive');
    } finally {
      setLoadingDocs(false);
    }
  }, [error]);

  useEffect(() => {
    if (activeTab === 'decisions') {
      executeSearch();
    } else {
      loadDocuments();
    }
  }, [activeTab, executeSearch, loadDocuments]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    setPage(1);
    executeSearch();
  };

  const handleDownloadDoc = async (att) => {
    try {
      const blob = await attachmentsApi.downloadAttachmentBlob(att.id);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = att.filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch {
      error('Failed to download document');
    }
  };

  const formatBytes = (bytes) => {
    if (!bytes) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  };

  const filteredDocs = documents.filter((d) => {
    if (!docSearch.trim()) return true;
    return d.filename.toLowerCase().includes(docSearch.toLowerCase().trim());
  });

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
          Explore previous architectural deliberations, trade-off matrices, specification archives, and lessons learned.
        </p>

        {/* Tab Selection */}
        <div style={{ display: 'inline-flex', background: 'var(--bg-hover)', padding: '4px', borderRadius: '10px', border: '1px solid var(--border-color)' }}>
          <button
            onClick={() => setActiveTab('decisions')}
            className={`btn btn-sm ${activeTab === 'decisions' ? 'btn-primary' : 'btn-secondary'}`}
            style={{ borderRadius: '6px' }}
          >
            <BookOpen size={15} /> Decisions Archive
          </button>
          <button
            onClick={() => setActiveTab('documents')}
            className={`btn btn-sm ${activeTab === 'documents' ? 'btn-primary' : 'btn-secondary'}`}
            style={{ borderRadius: '6px' }}
          >
            <Paperclip size={15} /> Document Archive
          </button>
        </div>
      </div>

      {/* TAB 1: DECISIONS REPOSITORY */}
      {activeTab === 'decisions' && (
        <>
          {/* Global Search Bar */}
          <form onSubmit={handleSearchSubmit} style={{ maxWidth: '680px', margin: '0 auto', display: 'flex', gap: '0.5rem', width: '100%' }}>
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
            <button type="submit" className="btn btn-primary" style={{ padding: '0 1.5rem', height: '48px' }}>
              Search
            </button>
          </form>

          {/* Filters Bar */}
          <div className="card" style={{ padding: '1rem 1.25rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', flexWrap: 'wrap' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
                <Filter size={16} /> Filters:
              </div>

              <select
                className="form-select"
                value={category}
                onChange={(e) => {
                  setCategory(e.target.value);
                  setPage(1);
                }}
                style={{ minWidth: '150px', height: '36px', fontSize: '0.85rem' }}
              >
                <option value="">All Categories</option>
                <option value="Architecture">Architecture</option>
                <option value="Infrastructure">Infrastructure</option>
                <option value="Security">Security</option>
                <option value="Database">Database</option>
                <option value="Framework">Framework</option>
                <option value="DevOps">DevOps</option>
              </select>

              <select
                className="form-select"
                value={status}
                onChange={(e) => {
                  setStatus(e.target.value);
                  setPage(1);
                }}
                style={{ minWidth: '140px', height: '36px', fontSize: '0.85rem' }}
              >
                <option value="">All Statuses</option>
                <option value="Draft">Draft</option>
                <option value="Under Review">Under Review</option>
                <option value="Approved">Approved</option>
                <option value="Rejected">Rejected</option>
                <option value="Archived">Archived</option>
              </select>

              <div style={{ position: 'relative', flex: 1, minWidth: '160px' }}>
                <Tag size={15} style={{ position: 'absolute', left: '10px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
                <input
                  type="text"
                  className="form-input"
                  style={{ paddingLeft: '2rem', height: '36px', fontSize: '0.85rem' }}
                  placeholder="Filter by tag (e.g. redis, microservices)..."
                  value={tag}
                  onChange={(e) => setTag(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && (setPage(1), executeSearch())}
                />
              </div>

              {(query || category || status || tag) && (
                <button
                  className="btn btn-secondary btn-sm"
                  onClick={() => {
                    setQuery('');
                    setCategory('');
                    setStatus('');
                    setTag('');
                    setPage(1);
                  }}
                >
                  Clear All
                </button>
              )}
            </div>
          </div>

          {/* Results Info */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
            <span>Found <strong>{total}</strong> historical organizational decision{total === 1 ? '' : 's'}</span>
            <span>Page {page} of {totalPages}</span>
          </div>

          {/* Results Grid */}
          {loadingDecisions ? (
            <LoadingSpinner message="Searching organizational repository..." />
          ) : results.length === 0 ? (
            <EmptyState
              title="No historical decisions found"
              description="Try adjusting your keywords, tags, or status filters."
              action={
                <button className="btn btn-primary btn-sm" onClick={() => { setQuery(''); setCategory(''); setStatus(''); setTag(''); }}>
                  Reset Filters
                </button>
              }
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
                        Explore & Replay <ArrowRight size={14} />
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
        </>
      )}

      {/* TAB 2: DOCUMENT ARCHIVE */}
      {activeTab === 'documents' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
            <div style={{ position: 'relative', minWidth: '300px', flex: 1, maxWidth: '500px' }}>
              <Search size={16} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
              <input
                type="text"
                className="form-input"
                style={{ paddingLeft: '2.25rem', height: '40px', fontSize: '0.9rem' }}
                placeholder="Search attached documents by filename..."
                value={docSearch}
                onChange={(e) => setDocSearch(e.target.value)}
              />
            </div>
            <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
              Showing {filteredDocs.length} of {documents.length} documents
            </div>
          </div>

          {loadingDocs ? (
            <LoadingSpinner message="Loading document archive..." />
          ) : filteredDocs.length === 0 ? (
            <EmptyState
              icon={Paperclip}
              title="No Documents Found"
              description="No architectural specifications or documents have been uploaded to decisions yet."
            />
          ) : (
            <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
              <div className="table-container" style={{ border: 'none', borderRadius: 0 }}>
                <table className="table">
                  <thead>
                    <tr>
                      <th>Document Name</th>
                      <th>Decision</th>
                      <th>File Size</th>
                      <th>Uploaded By</th>
                      <th>Upload Date</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredDocs.map((doc) => (
                      <tr key={doc.id}>
                        <td>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontWeight: 600 }}>
                            <FileText size={18} style={{ color: 'var(--primary)', flexShrink: 0 }} />
                            <span>{doc.filename}</span>
                          </div>
                        </td>
                        <td>
                          <button
                            onClick={() => onSelectDecision(doc.decision_id)}
                            className="btn btn-secondary btn-sm"
                            style={{ padding: '2px 8px', fontSize: '0.75rem' }}
                          >
                            Decision #{doc.decision_id}
                          </button>
                        </td>
                        <td>{formatBytes(doc.file_size)}</td>
                        <td>{doc.uploader?.full_name || `User #${doc.uploaded_by || '—'}`}</td>
                        <td>{new Date(doc.created_at).toLocaleDateString()}</td>
                        <td>
                          <button
                            className="btn btn-secondary btn-sm"
                            onClick={() => handleDownloadDoc(doc)}
                            style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', padding: '4px 10px' }}
                          >
                            <Download size={14} /> Download
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
