import { request } from './client';

function buildQuery(params = {}) {
  const q = new URLSearchParams();
  Object.entries(params).forEach(([k, v]) => {
    if (v !== undefined && v !== null && v !== '') {
      q.append(k, v);
    }
  });
  const str = q.toString();
  return str ? `?${str}` : '';
}

export const reportsApi = {
  getDecisionsReport: async (params = {}) => {
    return await request(`/reports/decisions${buildQuery(params)}`);
  },

  exportDecisionsPdf: async (params = {}) => {
    return await request(`/reports/decisions/export/pdf${buildQuery(params)}`, {
      responseType: 'blob',
    });
  },

  exportDecisionsExcel: async (params = {}) => {
    return await request(`/reports/decisions/export/excel${buildQuery(params)}`, {
      responseType: 'blob',
    });
  },

  getApprovalsReport: async (params = {}) => {
    return await request(`/reports/approvals${buildQuery(params)}`);
  },

  exportApprovalsPdf: async (params = {}) => {
    return await request(`/reports/approvals/export/pdf${buildQuery(params)}`, {
      responseType: 'blob',
    });
  },

  exportApprovalsExcel: async (params = {}) => {
    return await request(`/reports/approvals/export/excel${buildQuery(params)}`, {
      responseType: 'blob',
    });
  },

  getTeamsReport: async (params = {}) => {
    return await request(`/reports/teams${buildQuery(params)}`);
  },

  exportTeamsPdf: async (params = {}) => {
    return await request(`/reports/teams/export/pdf${buildQuery(params)}`, {
      responseType: 'blob',
    });
  },

  exportTeamsExcel: async (params = {}) => {
    return await request(`/reports/teams/export/excel${buildQuery(params)}`, {
      responseType: 'blob',
    });
  },

  getAuditReport: async (params = {}) => {
    return await request(`/reports/audit${buildQuery(params)}`);
  },

  exportAuditPdf: async (params = {}) => {
    return await request(`/reports/audit/export/pdf${buildQuery(params)}`, {
      responseType: 'blob',
    });
  },

  exportAuditExcel: async (params = {}) => {
    return await request(`/reports/audit/export/excel${buildQuery(params)}`, {
      responseType: 'blob',
    });
  },
};

export function downloadBlob(blob, filename) {
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.style.display = 'none';
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  window.URL.revokeObjectURL(url);
  document.body.removeChild(a);
}
