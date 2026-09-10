import api from './api';

// Helper to download binary files from backend
const downloadBlob = async (endpoint, filename, params = {}) => {
  const response = await api.get(endpoint, {
    params,
    responseType: 'blob',
  });

  const url = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', filename);
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
};

export const reportService = {
  // --- Data Reports ---
  getDecisionReport: async (params = {}) => {
    const response = await api.get('/reports/decisions', { params });
    return response.data;
  },

  getApprovalReport: async (params = {}) => {
    const response = await api.get('/reports/approvals', { params });
    return response.data;
  },

  getTeamReport: async (params = {}) => {
    const response = await api.get('/reports/teams', { params });
    return response.data;
  },

  getAuditReport: async (params = {}) => {
    const response = await api.get('/reports/audit', { params });
    return response.data;
  },

  // --- PDF & Excel Exports ---
  exportDecisionPdf: async (params = {}) => {
    const timestamp = new Date().toISOString().split('T')[0];
    await downloadBlob('/reports/decisions/pdf', `decision_report_${timestamp}.pdf`, params);
  },

  exportDecisionExcel: async (params = {}) => {
    const timestamp = new Date().toISOString().split('T')[0];
    await downloadBlob('/reports/decisions/excel', `decision_report_${timestamp}.xlsx`, params);
  },

  exportApprovalPdf: async (params = {}) => {
    const timestamp = new Date().toISOString().split('T')[0];
    await downloadBlob('/reports/approvals/pdf', `approval_report_${timestamp}.pdf`, params);
  },

  exportApprovalExcel: async (params = {}) => {
    const timestamp = new Date().toISOString().split('T')[0];
    await downloadBlob('/reports/approvals/excel', `approval_report_${timestamp}.xlsx`, params);
  },

  exportTeamPdf: async (params = {}) => {
    const timestamp = new Date().toISOString().split('T')[0];
    await downloadBlob('/reports/teams/pdf', `team_report_${timestamp}.pdf`, params);
  },

  exportTeamExcel: async (params = {}) => {
    const timestamp = new Date().toISOString().split('T')[0];
    await downloadBlob('/reports/teams/excel', `team_report_${timestamp}.xlsx`, params);
  },

  exportAuditPdf: async (params = {}) => {
    const timestamp = new Date().toISOString().split('T')[0];
    await downloadBlob('/reports/audit/pdf', `audit_report_${timestamp}.pdf`, params);
  },

  exportAuditExcel: async (params = {}) => {
    const timestamp = new Date().toISOString().split('T')[0];
    await downloadBlob('/reports/audit/excel', `audit_report_${timestamp}.xlsx`, params);
  },
};
