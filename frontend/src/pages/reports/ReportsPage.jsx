import React, { useState, useEffect } from 'react';
import { reportService } from '../../services/reportService';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import { StatusBadge } from '../../components/common/StatusBadge';
import { useToast } from '../../components/common/Toast';
import {
  FileSpreadsheet,
  FileDown,
  FileText,
  CheckCircle2,
  Clock,
  Filter,
  Download,
  BarChart2,
  Users,
} from 'lucide-react';

const REPORT_TABS = [
  { id: 'decisions', label: 'Decision Reports' },
  { id: 'approvals', label: 'Approval Reports' },
  { id: 'teams', label: 'Team Reports' },
  { id: 'audit', label: 'Audit Reports' },
];

export const ReportsPage = () => {
  const { addToast } = useToast();
  const [activeTab, setActiveTab] = useState('decisions');

  // Filter controls
  const [category, setCategory] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');

  // Report Data
  const [reportData, setReportData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isExporting, setIsExporting] = useState(false);
  const [error, setError] = useState('');

  const fetchActiveReport = async () => {
    setIsLoading(true);
    setError('');
    try {
      const params = {};
      if (category) params.category = category;
      if (statusFilter) params.status = statusFilter;
      if (startDate) params.start_date = startDate;
      if (endDate) params.end_date = endDate;

      let data;
      if (activeTab === 'decisions') {
        data = await reportService.getDecisionReport(params);
      } else if (activeTab === 'approvals') {
        data = await reportService.getApprovalReport(params);
      } else if (activeTab === 'teams') {
        data = await reportService.getTeamReport(params);
      } else if (activeTab === 'audit') {
        data = await reportService.getAuditReport(params);
      }
      setReportData(data);
    } catch (err) {
      setError(err.userMessage || 'Failed to load report data');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchActiveReport();
  }, [activeTab, category, statusFilter]);

  // Export handlers
  const handleExport = async (format) => {
    setIsExporting(true);
    try {
      const params = {};
      if (category) params.category = category;
      if (statusFilter) params.status = statusFilter;
      if (startDate) params.start_date = startDate;
      if (endDate) params.end_date = endDate;

      if (activeTab === 'decisions') {
        if (format === 'pdf') await reportService.exportDecisionPdf(params);
        else await reportService.exportDecisionExcel(params);
      } else if (activeTab === 'approvals') {
        if (format === 'pdf') await reportService.exportApprovalPdf(params);
        else await reportService.exportApprovalExcel(params);
      } else if (activeTab === 'teams') {
        if (format === 'pdf') await reportService.exportTeamPdf(params);
        else await reportService.exportTeamExcel(params);
      } else if (activeTab === 'audit') {
        if (format === 'pdf') await reportService.exportAuditPdf(params);
        else await reportService.exportAuditExcel(params);
      }

      addToast(`Successfully downloaded ${format.toUpperCase()} report`, 'success');
    } catch (err) {
      addToast(err.userMessage || `Failed to export ${format.toUpperCase()}`, 'error');
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.75rem' }}>
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
            <FileSpreadsheet size={28} />
            Analytics & Executive Reports
          </h1>
          <p className="page-description">
            Generate quantitative compliance metrics, review turnaround statistics, and download PDF & Excel summaries.
          </p>
        </div>

        {/* Download Buttons */}
        <div style={{ display: 'flex', gap: '0.75rem' }}>
          <button
            className="btn btn-secondary"
            onClick={() => handleExport('excel')}
            disabled={isExporting}
          >
            <Download size={16} color="#34d399" />
            <span>Export Excel</span>
          </button>
          <button
            className="btn btn-primary"
            onClick={() => handleExport('pdf')}
            disabled={isExporting}
          >
            <FileDown size={16} />
            <span>Export PDF</span>
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="tabs-container">
        {REPORT_TABS.map((t) => (
          <button
            key={t.id}
            className={`tab-btn ${activeTab === t.id ? 'active' : ''}`}
            onClick={() => setActiveTab(t.id)}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* Filter Options */}
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
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
          <Filter size={16} /> Filters:
        </div>

        {activeTab === 'decisions' && (
          <>
            <select
              className="form-select"
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              style={{ width: '180px' }}
            >
              <option value="">All Categories</option>
              <option value="Technology">Technology</option>
              <option value="Architecture">Architecture</option>
              <option value="Operations">Operations</option>
              <option value="Security">Security</option>
              <option value="Finance">Finance</option>
            </select>

            <select
              className="form-select"
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              style={{ width: '160px' }}
            >
              <option value="">All Statuses</option>
              <option value="Approved">Approved</option>
              <option value="Under Review">Under Review</option>
              <option value="Draft">Draft</option>
              <option value="Rejected">Rejected</option>
            </select>
          </>
        )}

        <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
          <input
            type="date"
            className="form-input"
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
            style={{ width: '150px' }}
          />
          <span className="text-dim">to</span>
          <input
            type="date"
            className="form-input"
            value={endDate}
            onChange={(e) => setEndDate(e.target.value)}
            style={{ width: '150px' }}
          />
          <button className="btn btn-secondary btn-sm" onClick={fetchActiveReport}>
            Apply
          </button>
        </div>
      </div>

      {/* Report Content */}
      {isLoading ? (
        <LoadingSpinner message="Generating report data..." />
      ) : error ? (
        <div className="alert alert-error">
          <span>{error}</span>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          {/* Summary Metrics Cards */}
          {reportData?.summary && (
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                gap: '1rem',
              }}
            >
              {Object.entries(reportData.summary).map(([key, val]) => (
                <div key={key} className="card" style={{ padding: '1rem 1.25rem' }}>
                  <span className="text-dim" style={{ fontSize: '0.78rem', textTransform: 'capitalize' }}>
                    {key.replace(/_/g, ' ')}
                  </span>
                  <div style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--text-primary)', marginTop: '4px' }}>
                    {typeof val === 'number' && key.includes('rate') ? `${val}%` : String(val)}
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Data Table */}
          <div className="card">
            <div className="card-header">
              <h3 className="card-title">Detailed Report Records</h3>
              <span className="text-dim" style={{ fontSize: '0.85rem' }}>
                Total Records: <strong style={{ color: 'var(--text-primary)' }}>{reportData?.total || (reportData?.items || []).length}</strong>
              </span>
            </div>

            <div className="table-container" style={{ border: 'none' }}>
              <table className="table">
                <thead>
                  {activeTab === 'decisions' && (
                    <tr>
                      <th>ID</th>
                      <th>Decision Title</th>
                      <th>Category</th>
                      <th>Status</th>
                      <th>Created</th>
                      <th>Updated</th>
                    </tr>
                  )}
                  {activeTab === 'approvals' && (
                    <tr>
                      <th>ID</th>
                      <th>Decision</th>
                      <th>Reviewer</th>
                      <th>Status</th>
                      <th>Created</th>
                      <th>Turnaround</th>
                    </tr>
                  )}
                  {activeTab === 'teams' && (
                    <tr>
                      <th>Department / Team</th>
                      <th>Total Decisions</th>
                      <th>Approved</th>
                      <th>Pending</th>
                      <th>Members</th>
                    </tr>
                  )}
                  {activeTab === 'audit' && (
                    <tr>
                      <th>Timestamp</th>
                      <th>User</th>
                      <th>Action</th>
                      <th>Entity</th>
                      <th>IP</th>
                      <th>Description</th>
                    </tr>
                  )}
                </thead>
                <tbody>
                  {(reportData?.items || []).map((item, idx) => (
                    <tr key={item.id || idx}>
                      {activeTab === 'decisions' && (
                        <>
                          <td className="font-mono">#{item.id}</td>
                          <td>
                            <div className="table-cell-title">{item.title}</div>
                          </td>
                          <td>
                            <span className="badge badge-category">{item.category}</span>
                          </td>
                          <td>
                            <StatusBadge status={item.status} />
                          </td>
                          <td style={{ fontSize: '0.82rem', color: 'var(--text-dim)' }}>
                            {new Date(item.created_at).toLocaleDateString()}
                          </td>
                          <td style={{ fontSize: '0.82rem', color: 'var(--text-dim)' }}>
                            {item.updated_at ? new Date(item.updated_at).toLocaleDateString() : '—'}
                          </td>
                        </>
                      )}

                      {activeTab === 'approvals' && (
                        <>
                          <td className="font-mono">#{item.id}</td>
                          <td>
                            <div className="table-cell-title">{item.decision_title || `Decision #${item.decision_id}`}</div>
                          </td>
                          <td>{item.reviewer_name || `Reviewer #${item.reviewer_id}`}</td>
                          <td>
                            <StatusBadge status={item.status} />
                          </td>
                          <td style={{ fontSize: '0.82rem', color: 'var(--text-dim)' }}>
                            {new Date(item.created_at).toLocaleDateString()}
                          </td>
                          <td style={{ fontSize: '0.82rem', color: 'var(--accent-cyan)' }}>
                            {item.completed_at ? 'Completed' : 'Pending'}
                          </td>
                        </>
                      )}

                      {activeTab === 'teams' && (
                        <>
                          <td style={{ fontWeight: 700, color: 'var(--text-primary)' }}>{item.department || 'Platform'}</td>
                          <td style={{ fontWeight: 600 }}>{item.total_decisions || 0}</td>
                          <td style={{ color: '#047857', fontWeight: 600 }}>{item.approved_count || 0}</td>
                          <td style={{ color: '#b45309', fontWeight: 600 }}>{item.pending_count || 0}</td>
                          <td>{item.members_count || 1}</td>
                        </>
                      )}

                      {activeTab === 'audit' && (
                        <>
                          <td style={{ fontSize: '0.8rem', color: 'var(--text-dim)' }}>
                            {new Date(item.created_at).toLocaleDateString()}
                          </td>
                          <td style={{ fontWeight: 600 }}>{item.user_name || `User #${item.user_id}`}</td>
                          <td style={{ fontWeight: 700, color: 'var(--primary-light)' }}>{item.action}</td>
                          <td>{item.entity_type}</td>
                          <td className="font-mono" style={{ fontSize: '0.8rem' }}>{item.ip_address || '127.0.0.1'}</td>
                          <td style={{ fontSize: '0.85rem' }}>{item.description}</td>
                        </>
                      )}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
