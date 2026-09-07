import React, { useState, useEffect, useCallback } from 'react';
import {
  FileBarChart,
  FileSpreadsheet,
  Download,
  Filter,
  CheckCircle2,
  Clock,
  XCircle,
  Users,
  Shield,
  Layers,
} from 'lucide-react';
import { reportsApi, downloadBlob } from '../../api/reports';
import { useNotification } from '../../context/NotificationContext';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import { StatusBadge } from '../../components/common/StatusBadge';
import { Pagination } from '../../components/common/Pagination';

export function ReportsPage() {
  const { success, error } = useNotification();

  const [activeReport, setActiveReport] = useState('decisions'); // 'decisions' | 'approvals' | 'teams' | 'audit'
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [exportingPdf, setExportingPdf] = useState(false);
  const [exportingExcel, setExportingExcel] = useState(false);

  // Common Filters
  const [category, setCategory] = useState('');
  const [status, setStatus] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [page, setPage] = useState(1);

  const fetchReportData = useCallback(async () => {
    setLoading(true);
    try {
      const filterParams = {
        category: category || undefined,
        status: status || undefined,
        start_date: startDate || undefined,
        end_date: endDate || undefined,
        page,
        page_size: 15,
      };

      let res = null;
      if (activeReport === 'decisions') {
        res = await reportsApi.getDecisionsReport(filterParams);
      } else if (activeReport === 'approvals') {
        res = await reportsApi.getApprovalsReport(filterParams);
      } else if (activeReport === 'teams') {
        res = await reportsApi.getTeamsReport(filterParams);
      } else if (activeReport === 'audit') {
        res = await reportsApi.getAuditReport(filterParams);
      }

      setData(res);
    } catch (err) {
      error(err.message || `Failed to fetch ${activeReport} report data`);
    } finally {
      setLoading(false);
    }
  }, [activeReport, category, status, startDate, endDate, page, error]);

  useEffect(() => {
    fetchReportData();
  }, [fetchReportData]);

  // Export handlers
  const handleExportPdf = async () => {
    setExportingPdf(true);
    try {
      const filterParams = {
        category: category || undefined,
        status: status || undefined,
        start_date: startDate || undefined,
        end_date: endDate || undefined,
      };

      let blob = null;
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
      let filename = `${activeReport}_report_${timestamp}.pdf`;

      if (activeReport === 'decisions') {
        blob = await reportsApi.exportDecisionsPdf(filterParams);
      } else if (activeReport === 'approvals') {
        blob = await reportsApi.exportApprovalsPdf(filterParams);
      } else if (activeReport === 'teams') {
        blob = await reportsApi.exportTeamsPdf(filterParams);
      } else if (activeReport === 'audit') {
        blob = await reportsApi.exportAuditPdf(filterParams);
      }

      downloadBlob(blob, filename);
      success(`Downloaded ${filename} successfully`);
    } catch (err) {
      error(err.message || 'PDF export failed');
    } finally {
      setExportingPdf(false);
    }
  };

  const handleExportExcel = async () => {
    setExportingExcel(true);
    try {
      const filterParams = {
        category: category || undefined,
        status: status || undefined,
        start_date: startDate || undefined,
        end_date: endDate || undefined,
      };

      let blob = null;
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
      let filename = `${activeReport}_report_${timestamp}.xlsx`;

      if (activeReport === 'decisions') {
        blob = await reportsApi.exportDecisionsExcel(filterParams);
      } else if (activeReport === 'approvals') {
        blob = await reportsApi.exportApprovalsExcel(filterParams);
      } else if (activeReport === 'teams') {
        blob = await reportsApi.exportTeamsExcel(filterParams);
      } else if (activeReport === 'audit') {
        blob = await reportsApi.exportAuditExcel(filterParams);
      }

      downloadBlob(blob, filename);
      success(`Downloaded ${filename} successfully`);
    } catch (err) {
      error(err.message || 'Excel export failed');
    } finally {
      setExportingExcel(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.75rem' }}>
      {/* Header and Export Controls */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '1rem',
      }}>
        <div>
          <h1 style={{ fontSize: '1.75rem', marginBottom: '0.25rem', display: 'flex', alignItems: 'center', gap: '10px' }}>
            <FileBarChart size={28} style={{ color: 'var(--primary)' }} /> Governance & Audit Reports
          </h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
            Generate compliance audit reports, approval turnaround metrics, and export to PDF / Excel.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '0.75rem' }}>
          <button
            className="btn btn-secondary"
            onClick={handleExportPdf}
            disabled={exportingPdf || loading}
          >
            <Download size={16} />
            {exportingPdf ? 'Generating PDF...' : 'Export PDF'}
          </button>
          <button
            className="btn btn-primary"
            onClick={handleExportExcel}
            disabled={exportingExcel || loading}
          >
            <FileSpreadsheet size={16} />
            {exportingExcel ? 'Exporting Excel...' : 'Export Excel'}
          </button>
        </div>
      </div>

      {/* Report Module Navigation Tabs */}
      <div style={{
        display: 'flex',
        borderBottom: '1px solid var(--border-color)',
        gap: '0.5rem',
      }}>
        {[
          { id: 'decisions', label: 'Decision Reports', icon: Layers },
          { id: 'approvals', label: 'Approval Reports', icon: CheckCircle2 },
          { id: 'teams', label: 'Team Reports', icon: Users },
          { id: 'audit', label: 'Audit Reports', icon: Shield },
        ].map((tab) => {
          const Icon = tab.icon;
          const isActive = activeReport === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => {
                setActiveReport(tab.id);
                setPage(1);
              }}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                padding: '0.75rem 1.25rem',
                border: 'none',
                background: 'transparent',
                borderBottom: `2px solid ${isActive ? 'var(--primary)' : 'transparent'}`,
                color: isActive ? 'var(--primary)' : 'var(--text-secondary)',
                fontWeight: isActive ? 600 : 500,
                fontSize: '0.95rem',
                cursor: 'pointer',
              }}
            >
              <Icon size={17} />
              {tab.label}
            </button>
          );
        })}
      </div>

      {/* Filter Controls Card */}
      <div className="card" style={{ padding: '1.25rem' }}>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '1rem', alignItems: 'center' }}>
          {activeReport === 'decisions' && (
            <select
              className="form-select"
              style={{ width: 'auto', minWidth: '150px' }}
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
          )}

          <select
            className="form-select"
            style={{ width: 'auto', minWidth: '150px' }}
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

          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>From:</span>
            <input
              type="date"
              className="form-input"
              style={{ width: 'auto' }}
              value={startDate}
              onChange={(e) => { setStartDate(e.target.value); setPage(1); }}
            />
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>To:</span>
            <input
              type="date"
              className="form-input"
              style={{ width: 'auto' }}
              value={endDate}
              onChange={(e) => { setEndDate(e.target.value); setPage(1); }}
            />
          </div>

          {(category || status || startDate || endDate) && (
            <button
              className="btn btn-secondary btn-sm"
              onClick={() => {
                setCategory('');
                setStatus('');
                setStartDate('');
                setEndDate('');
                setPage(1);
              }}
            >
              Reset Filters
            </button>
          )}
        </div>
      </div>

      {/* Summary KPI Cards if available */}
      {data && data.summary && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '1rem' }}>
          {Object.entries(data.summary).map(([key, val]) => (
            <div key={key} className="card" style={{ padding: '1rem 1.25rem' }}>
              <div style={{ fontSize: '0.75rem', textTransform: 'uppercase', color: 'var(--text-muted)', fontWeight: 600 }}>
                {key.replace(/_/g, ' ')}
              </div>
              <div style={{ fontSize: '1.5rem', fontWeight: 700, fontFamily: 'Outfit', color: 'var(--text-primary)', marginTop: '4px' }}>
                {typeof val === 'number' ? (Number.isInteger(val) ? val : val.toFixed(1)) : val}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Report Table */}
      {loading ? (
        <LoadingSpinner message={`Generating ${activeReport} report dataset...`} />
      ) : !data || !data.items || data.items.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: '3rem 1.5rem' }}>
          <p style={{ color: 'var(--text-secondary)' }}>No report items found for the selected criteria.</p>
        </div>
      ) : (
        <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
          <div className="table-container" style={{ border: 'none', borderRadius: 0 }}>
            <table className="table">
              <thead>
                <tr>
                  {activeReport === 'decisions' && (
                    <>
                      <th>ID</th>
                      <th>Title</th>
                      <th>Category</th>
                      <th>Status</th>
                      <th>Created At</th>
                    </>
                  )}
                  {activeReport === 'approvals' && (
                    <>
                      <th>ID</th>
                      <th>Decision ID</th>
                      <th>Reviewer</th>
                      <th>Status</th>
                      <th>Requested At</th>
                      <th>Completed At</th>
                    </>
                  )}
                  {activeReport === 'teams' && (
                    <>
                      <th>Team / Dept</th>
                      <th>Total Decisions</th>
                      <th>Approved</th>
                      <th>Pending</th>
                    </>
                  )}
                  {activeReport === 'audit' && (
                    <>
                      <th>ID</th>
                      <th>Action</th>
                      <th>Entity</th>
                      <th>User ID</th>
                      <th>Timestamp</th>
                      <th>Summary</th>
                    </>
                  )}
                </tr>
              </thead>
              <tbody>
                {data.items.map((row, idx) => (
                  <tr key={idx}>
                    {activeReport === 'decisions' && (
                      <>
                        <td><strong>#{row.decision_id ?? row.id}</strong></td>
                        <td>
                          <div style={{ fontWeight: 600, color: 'var(--text-primary)' }}>
                            {row.decision_title || row.title || 'Untitled Decision'}
                          </div>
                          {row.creator_name && (
                            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                              Author: {row.creator_name}
                            </div>
                          )}
                        </td>
                        <td><span className="badge badge-role">{row.category || 'General'}</span></td>
                        <td><StatusBadge status={row.status} /></td>
                        <td>
                          {(row.created_date || row.created_at)
                            ? new Date(row.created_date || row.created_at).toLocaleDateString()
                            : '—'}
                        </td>
                      </>
                    )}
                    {activeReport === 'approvals' && (
                      <>
                        <td><strong>#{row.approval_id ?? row.id}</strong></td>
                        <td>
                          <div style={{ fontWeight: 600 }}>#{row.decision_id}</div>
                          {row.decision_title && (
                            <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                              {row.decision_title}
                            </div>
                          )}
                        </td>
                        <td>{row.reviewer_name || `Reviewer #${row.reviewer_id}`}</td>
                        <td><StatusBadge status={row.approval_status || row.status} /></td>
                        <td>
                          {(row.assigned_date || row.created_at)
                            ? new Date(row.assigned_date || row.created_at).toLocaleDateString()
                            : '—'}
                        </td>
                        <td>
                          {(row.completed_date || row.completed_at)
                            ? new Date(row.completed_date || row.completed_at).toLocaleDateString()
                            : '—'}
                        </td>
                      </>
                    )}
                    {activeReport === 'teams' && (
                      <>
                        <td><strong>{row.team_name || row.department || 'General'}</strong></td>
                        <td>{row.total_decisions || 0}</td>
                        <td><span style={{ color: 'var(--success)' }}>{row.approved_decisions || 0}</span></td>
                        <td><span style={{ color: 'var(--warning)' }}>{row.pending_decisions || 0}</span></td>
                      </>
                    )}
                    {activeReport === 'audit' && (
                      <>
                        <td>#{row.audit_id ?? row.id}</td>
                        <td><span className="badge badge-role">{row.action}</span></td>
                        <td>{row.entity_type} #{row.entity_id || ''}</td>
                        <td>{row.user_name || `User #${row.user_id}`}</td>
                        <td>
                          {(row.timestamp || row.created_at)
                            ? new Date(row.timestamp || row.created_at).toLocaleString()
                            : '—'}
                        </td>
                        <td style={{ maxWidth: '300px' }}>{row.description}</td>
                      </>
                    )}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <Pagination
            currentPage={page}
            totalPages={data.total_pages || 1}
            onPageChange={(p) => setPage(p)}
          />
        </div>
      )}
    </div>
  );
}
