import React, { useState, useEffect } from 'react';
import { reportService } from '../../api/reportService';
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
  BarChart3,
  FileSpreadsheet,
  FileText,
  Download,
  Filter,
  CheckCircle,
  Clock,
  ShieldAlert,
  Users,
} from 'lucide-react';

export const ReportsPage = () => {
  const [reportType, setReportType] = useState('decisions'); // 'decisions', 'approvals', 'team', 'audit'
  const [reportData, setReportData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [exportingPdf, setExportingPdf] = useState(false);
  const [exportingExcel, setExportingExcel] = useState(false);

  // Filters
  const [category, setCategory] = useState('');
  const [status, setStatus] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [department, setDepartment] = useState('');
  const [page, setPage] = useState(1);
  const [pageSize] = useState(15);

  const { success, error } = useToast();
  const { user } = useAuth();

  const fetchReport = async () => {
    try {
      setLoading(true);
      const params = {
        category: category.trim() || undefined,
        status: status || undefined,
        start_date: startDate || undefined,
        end_date: endDate || undefined,
        department: department.trim() || undefined,
        page,
        page_size: pageSize,
      };

      let res;
      if (reportType === 'decisions') {
        res = await reportService.getDecisionsReport(params);
      } else if (reportType === 'approvals') {
        res = await reportService.getApprovalsReport(params);
      } else if (reportType === 'team') {
        res = await reportService.getTeamReport(params);
      } else {
        res = await reportService.getAuditReport(params);
      }

      setReportData(res);
    } catch (err) {
      error(err.message || 'Failed to generate report');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    setPage(1);
    fetchReport();
  }, [reportType]);

  useEffect(() => {
    fetchReport();
  }, [page]);

  const handleExport = async (format) => {
    const params = {
      category: category.trim() || undefined,
      status: status || undefined,
      start_date: startDate || undefined,
      end_date: endDate || undefined,
      department: department.trim() || undefined,
    };

    try {
      if (format === 'pdf') {
        setExportingPdf(true);
        if (reportType === 'decisions') await reportService.exportDecisionsPdf(params);
        else if (reportType === 'approvals') await reportService.exportApprovalsPdf(params);
        else if (reportType === 'team') await reportService.exportTeamPdf(params);
        else await reportService.exportAuditPdf(params);
        success('PDF Report exported successfully!');
      } else {
        setExportingExcel(true);
        if (reportType === 'decisions') await reportService.exportDecisionsExcel(params);
        else if (reportType === 'approvals') await reportService.exportApprovalsExcel(params);
        else if (reportType === 'team') await reportService.exportTeamExcel(params);
        else await reportService.exportAuditExcel(params);
        success('Excel Spreadsheet exported successfully!');
      }
    } catch (err) {
      error(err.message || `Failed to export ${format.toUpperCase()}`);
    } finally {
      setExportingPdf(false);
      setExportingExcel(false);
    }
  };

  const summary = reportData?.summary || {};
  const items = reportData?.items || [];
  const total = reportData?.total || items.length;
  const totalPages = reportData?.total_pages || Math.ceil(total / pageSize) || 1;

  return (
    <div>
      {/* Header with Export Action Buttons */}
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
            Enterprise Decision Intelligence & Reports
          </h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.925rem' }}>
            Generate quantitative summaries, approval SLAs, and export boardroom-ready reports.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '0.75rem' }}>
          <Button
            variant="outline"
            icon={Download}
            loading={exportingPdf}
            onClick={() => handleExport('pdf')}
          >
            Export PDF
          </Button>
          <Button
            variant="primary"
            icon={FileSpreadsheet}
            loading={exportingExcel}
            onClick={() => handleExport('excel')}
          >
            Export Excel
          </Button>
        </div>
      </div>

      {/* Tabs */}
      <div className="tabs-header">
        <button
          className={`tab-btn ${reportType === 'decisions' ? 'active' : ''}`}
          onClick={() => setReportType('decisions')}
        >
          <FileText size={16} /> Decision Portfolio Report
        </button>
        <button
          className={`tab-btn ${reportType === 'approvals' ? 'active' : ''}`}
          onClick={() => setReportType('approvals')}
        >
          <CheckCircle size={16} /> Approval SLA & Velocity Report
        </button>
        <button
          className={`tab-btn ${reportType === 'team' ? 'active' : ''}`}
          onClick={() => setReportType('team')}
        >
          <Users size={16} /> Team Performance Report
        </button>
        {user?.role === 'Administrator' && (
          <button
            className={`tab-btn ${reportType === 'audit' ? 'active' : ''}`}
            onClick={() => setReportType('audit')}
          >
            <ShieldAlert size={16} /> Audit & Governance Report
          </button>
        )}
      </div>

      {/* Filter Controls */}
      <Card style={{ marginBottom: '1.5rem' }}>
        <form onSubmit={(e) => { e.preventDefault(); setPage(1); fetchReport(); }}>
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))',
              gap: '1rem',
              alignItems: 'flex-end',
            }}
          >
            {reportType === 'decisions' && (
              <div>
                <Input
                  label="Category"
                  placeholder="e.g. Architecture"
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                />
              </div>
            )}

            {(reportType === 'decisions' || reportType === 'approvals') && (
              <div>
                <Select
                  label="Status"
                  value={status}
                  onChange={(e) => setStatus(e.target.value)}
                  placeholder="All Statuses"
                  options={[
                    { value: 'Draft', label: 'Draft' },
                    { value: 'Under Review', label: 'Under Review' },
                    { value: 'Approved', label: 'Approved' },
                    { value: 'Rejected', label: 'Rejected' },
                  ]}
                />
              </div>
            )}

            {reportType === 'team' && (
              <div>
                <Input
                  label="Department"
                  placeholder="e.g. Engineering"
                  value={department}
                  onChange={(e) => setDepartment(e.target.value)}
                />
              </div>
            )}

            <div>
              <Input
                label="Start Date"
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
              />
            </div>

            <div>
              <Input
                label="End Date"
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
              />
            </div>

            <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.25rem' }}>
              <Button type="submit" variant="primary" icon={Filter} style={{ flex: 1 }}>
                Apply Filters
              </Button>
              <Button
                type="button"
                variant="outline"
                onClick={() => {
                  setCategory('');
                  setStatus('');
                  setStartDate('');
                  setEndDate('');
                  setDepartment('');
                  setPage(1);
                  fetchReport();
                }}
              >
                Reset
              </Button>
            </div>
          </div>
        </form>
      </Card>

      {/* Summary KPI Cards */}
      {summary && Object.keys(summary).length > 0 && (
        <div className="stat-grid" style={{ marginBottom: '1.5rem' }}>
          {Object.entries(summary).map(([key, val]) => (
            <Card key={key} className="stat-card">
              <span className="stat-title">{key.replace(/_/g, ' ')}</span>
              <span className="stat-value">{typeof val === 'number' ? val : String(val)}</span>
            </Card>
          ))}
        </div>
      )}

      {/* Report Data Table */}
      {loading ? (
        <LoadingSpinner message="Generating report metrics..." />
      ) : items.length === 0 ? (
        <EmptyState
          icon={BarChart3}
          title="No records in report"
          description="Try broadening the filter date range."
        />
      ) : (
        <Card>
          <div className="table-container">
            <table className="custom-table">
              <thead>
                <tr>
                  {reportType === 'decisions' && (
                    <>
                      <th>ID</th>
                      <th>Title</th>
                      <th>Category</th>
                      <th>Status</th>
                      <th>Created Date</th>
                      <th>Last Updated</th>
                    </>
                  )}
                  {reportType === 'approvals' && (
                    <>
                      <th>Approval ID</th>
                      <th>Decision ID</th>
                      <th>Reviewer ID</th>
                      <th>Level</th>
                      <th>Status</th>
                      <th>Created</th>
                      <th>Turnaround (Days)</th>
                    </>
                  )}
                  {reportType === 'team' && (
                    <>
                      <th>User</th>
                      <th>Department</th>
                      <th>Role</th>
                      <th>Total Created</th>
                      <th>Approved</th>
                      <th>Under Review</th>
                    </>
                  )}
                  {reportType === 'audit' && (
                    <>
                      <th>Timestamp</th>
                      <th>Action</th>
                      <th>User ID</th>
                      <th>Entity</th>
                      <th>IP</th>
                      <th>Details</th>
                    </>
                  )}
                </tr>
              </thead>
              <tbody>
                {items.map((row, idx) => (
                  <tr key={idx}>
                    {reportType === 'decisions' && (
                      <>
                        <td style={{ fontWeight: 600 }}>#{row.id}</td>
                        <td style={{ fontWeight: 600, color: '#ffffff' }}>{row.title}</td>
                        <td>{row.category}</td>
                        <td>
                          <StatusBadge status={row.status} />
                        </td>
                        <td style={{ color: 'var(--text-muted)' }}>
                          {new Date(row.created_at).toLocaleDateString()}
                        </td>
                        <td style={{ color: 'var(--text-muted)' }}>
                          {new Date(row.updated_at).toLocaleDateString()}
                        </td>
                      </>
                    )}
                    {reportType === 'approvals' && (
                      <>
                        <td>#{row.approval_id || row.id}</td>
                        <td style={{ fontWeight: 600, color: '#ffffff' }}>Decision #{row.decision_id}</td>
                        <td>Reviewer #{row.reviewer_id}</td>
                        <td>Level {row.approval_level}</td>
                        <td>
                          <StatusBadge status={row.status} />
                        </td>
                        <td style={{ color: 'var(--text-muted)' }}>
                          {new Date(row.created_at).toLocaleDateString()}
                        </td>
                        <td style={{ fontWeight: 700, color: '#60a5fa' }}>
                          {row.turnaround_days !== undefined ? `${row.turnaround_days} d` : '-'}
                        </td>
                      </>
                    )}
                    {reportType === 'team' && (
                      <>
                        <td style={{ fontWeight: 600, color: '#ffffff' }}>
                          {row.user_name || `User #${row.user_id}`}
                        </td>
                        <td>{row.department || 'General'}</td>
                        <td>
                          <span className="badge badge-role">{row.role || 'Employee'}</span>
                        </td>
                        <td style={{ fontWeight: 700, color: '#ffffff' }}>{row.total_decisions ?? row.created_count ?? 0}</td>
                        <td style={{ color: '#34d399', fontWeight: 600 }}>{row.approved_count ?? 0}</td>
                        <td style={{ color: '#fbbf24', fontWeight: 600 }}>{row.under_review_count ?? 0}</td>
                      </>
                    )}
                    {reportType === 'audit' && (
                      <>
                        <td style={{ color: 'var(--text-muted)' }}>
                          {new Date(row.created_at || row.timestamp).toLocaleString()}
                        </td>
                        <td>
                          <span className="badge" style={{ background: 'rgba(59, 130, 246, 0.15)', color: '#60a5fa' }}>
                            {row.action}
                          </span>
                        </td>
                        <td>User #{row.user_id}</td>
                        <td>{row.entity_type} #{row.entity_id}</td>
                        <td style={{ fontFamily: 'var(--font-mono)' }}>{row.ip_address || '127.0.0.1'}</td>
                        <td style={{ color: 'var(--text-secondary)' }}>{row.description || '-'}</td>
                      </>
                    )}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <Pagination
            page={page}
            pageSize={pageSize}
            totalItems={total}
            totalPages={totalPages}
            onPageChange={(p) => setPage(p)}
          />
        </Card>
      )}
    </div>
  );
};
