import { useState } from 'react';
import { getDecisionReport, getApprovalReport, getTeamReport, exportPDF, exportExcel } from '../services/api';
import Layout from '../components/Layout';

export default function Reports() {
  const [activeReport, setActiveReport] = useState('decisions');
  const [reportData, setReportData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [filters, setFilters] = useState({
    status: '', category: '', start_date: '', end_date: '',
  });

  const handleFilterChange = (e) => {
    setFilters({ ...filters, [e.target.name]: e.target.value });
  };

  const handleGenerate = async () => {
    setLoading(true);
    setError('');
    try {
      const params = {};
      if (filters.status) params.status = filters.status;
      if (filters.category) params.category = filters.category;
      if (filters.start_date) params.start_date = filters.start_date;
      if (filters.end_date) params.end_date = filters.end_date;

      let response;
      if (activeReport === 'decisions') response = await getDecisionReport(params);
      else if (activeReport === 'approvals') response = await getApprovalReport(params);
      else if (activeReport === 'teams') response = await getTeamReport(params);

      setReportData(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to generate report');
    } finally {
      setLoading(false);
    }
  };

  const handleExportPDF = async () => {
    try {
      const response = await exportPDF(activeReport);
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${activeReport}_report.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      alert('PDF export failed');
    }
  };

  const handleExportExcel = async () => {
    try {
      const response = await exportExcel(activeReport);
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${activeReport}_report.xlsx`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      alert('Excel export failed');
    }
  };

  return (
    <Layout>
      <h2 style={styles.title}>Reports & Export</h2>

      {/* Report Type Tabs */}
      <div style={styles.reportTabs}>
        {['decisions', 'approvals', 'teams'].map(type => (
          <button
            key={type}
            style={{
              ...styles.reportTab,
              ...(activeReport === type ? styles.activeReportTab : {})
            }}
            onClick={() => { setActiveReport(type); setReportData(null); }}
          >
            {type === 'decisions' && '📋 '}
            {type === 'approvals' && '✅ '}
            {type === 'teams' && '👥 '}
            {type.charAt(0).toUpperCase() + type.slice(1)} Report
          </button>
        ))}
      </div>

      {/* Filters */}
      <div style={styles.filterCard}>
        <h3 style={styles.filterTitle}>🔍 Filters</h3>
        <div style={styles.filterGrid}>
          {activeReport === 'decisions' && (
            <>
              <div style={styles.filterField}>
                <label style={styles.label}>Status</label>
                <select name="status" value={filters.status}
                  onChange={handleFilterChange} style={styles.input}>
                  <option value="">All Status</option>
                  <option value="Draft">Draft</option>
                  <option value="Under Review">Under Review</option>
                  <option value="Approved">Approved</option>
                  <option value="Rejected">Rejected</option>
                  <option value="Archived">Archived</option>
                </select>
              </div>
              <div style={styles.filterField}>
                <label style={styles.label}>Category</label>
                <select name="category" value={filters.category}
                  onChange={handleFilterChange} style={styles.input}>
                  <option value="">All Categories</option>
                  <option value="Technology">Technology</option>
                  <option value="Finance">Finance</option>
                  <option value="Operations">Operations</option>
                  <option value="HR">HR</option>
                  <option value="Marketing">Marketing</option>
                  <option value="Strategy">Strategy</option>
                </select>
              </div>
            </>
          )}
          <div style={styles.filterField}>
            <label style={styles.label}>Start Date</label>
            <input type="date" name="start_date" value={filters.start_date}
              onChange={handleFilterChange} style={styles.input} />
          </div>
          <div style={styles.filterField}>
            <label style={styles.label}>End Date</label>
            <input type="date" name="end_date" value={filters.end_date}
              onChange={handleFilterChange} style={styles.input} />
          </div>
        </div>
        <div style={styles.filterActions}>
          <button style={styles.generateBtn} onClick={handleGenerate} disabled={loading}>
            {loading ? '⏳ Generating...' : '📊 Generate Report'}
          </button>
          {reportData && (
            <>
              <button style={styles.pdfBtn} onClick={handleExportPDF}>
                📄 Export PDF
              </button>
              <button style={styles.excelBtn} onClick={handleExportExcel}>
                📊 Export Excel
              </button>
            </>
          )}
        </div>
      </div>

      {error && <div style={styles.error}>{error}</div>}

      {/* Results */}
      {reportData && (
        <div style={styles.resultCard}>
          {/* Summary */}
          {reportData.summary && (
            <div style={styles.summary}>
              <h3 style={styles.sectionTitle}>Summary</h3>
              <div style={styles.summaryGrid}>
                {Object.entries(reportData.summary).map(([key, value]) => (
                  <div key={key} style={styles.summaryItem}>
                    <div style={styles.summaryValue}>{value}</div>
                    <div style={styles.summaryLabel}>
                      {key.replace(/_/g, ' ').toUpperCase()}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Table */}
          <h3 style={styles.sectionTitle}>
            Results ({reportData.total} records)
          </h3>
          {reportData.items?.length === 0 ? (
            <p style={styles.empty}>No records found.</p>
          ) : (
            <div style={styles.tableContainer}>
              <table style={styles.table}>
                <thead>
                  <tr style={styles.thead}>
                    {reportData.items?.[0] && Object.keys(reportData.items[0]).map(key => (
                      <th key={key} style={styles.th}>
                        {key.replace(/_/g, ' ').toUpperCase()}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {reportData.items?.map((item, index) => (
                    <tr key={index} style={styles.tr}>
                      {Object.values(item).map((val, i) => (
                        <td key={i} style={styles.td}>
                          {typeof val === 'object' ? JSON.stringify(val) : String(val ?? '')}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </Layout>
  );
}

const styles = {
  title: { color: '#2C3E50', fontSize: '24px', marginBottom: '24px' },
  reportTabs: { display: 'flex', gap: '8px', marginBottom: '20px' },
  reportTab: { padding: '10px 20px', border: 'none', borderRadius: '6px', cursor: 'pointer', backgroundColor: '#ecf0f1', color: '#7f8c8d', fontSize: '14px' },
  activeReportTab: { backgroundColor: '#2C3E50', color: 'white' },
  filterCard: { backgroundColor: 'white', padding: '24px', borderRadius: '10px', marginBottom: '20px', boxShadow: '0 2px 8px rgba(0,0,0,0.05)' },
  filterTitle: { color: '#2C3E50', marginBottom: '16px', fontSize: '16px' },
  filterGrid: { display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px', marginBottom: '16px' },
  filterField: {},
  label: { display: 'block', marginBottom: '6px', color: '#2C3E50', fontWeight: '600', fontSize: '13px' },
  input: { width: '100%', padding: '8px', borderRadius: '6px', border: '1px solid #ddd', fontSize: '13px', boxSizing: 'border-box' },
  filterActions: { display: 'flex', gap: '12px' },
  generateBtn: { padding: '10px 20px', backgroundColor: '#2C3E50', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer' },
  pdfBtn: { padding: '10px 20px', backgroundColor: '#e74c3c', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer' },
  excelBtn: { padding: '10px 20px', backgroundColor: '#27ae60', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer' },
  error: { backgroundColor: '#fde8e8', color: '#c0392b', padding: '12px', borderRadius: '6px', marginBottom: '16px' },
  resultCard: { backgroundColor: 'white', padding: '24px', borderRadius: '10px', boxShadow: '0 2px 8px rgba(0,0,0,0.05)' },
  summary: { marginBottom: '24px' },
  sectionTitle: { color: '#2C3E50', fontSize: '16px', marginBottom: '16px' },
  summaryGrid: { display: 'grid', gridTemplateColumns: 'repeat(6, 1fr)', gap: '12px' },
  summaryItem: { backgroundColor: '#f8f9fa', padding: '16px', borderRadius: '8px', textAlign: 'center' },
  summaryValue: { fontSize: '24px', fontWeight: 'bold', color: '#2C3E50' },
  summaryLabel: { fontSize: '11px', color: '#7f8c8d', marginTop: '4px' },
  tableContainer: { overflowX: 'auto' },
  table: { width: '100%', borderCollapse: 'collapse' },
  thead: { backgroundColor: '#f8f9fa' },
  th: { padding: '12px', textAlign: 'left', color: '#7f8c8d', fontSize: '11px', fontWeight: '600', whiteSpace: 'nowrap' },
  tr: { borderBottom: '1px solid #eee' },
  td: { padding: '12px', fontSize: '13px', color: '#2C3E50', whiteSpace: 'nowrap' },
  empty: { color: '#7f8c8d', textAlign: 'center', padding: '20px' },
};