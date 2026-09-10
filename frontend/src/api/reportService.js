import client from './client';

export const reportService = {
  // Decision Reports
  async getDecisionsReport(params = {}) {
    const response = await client.get('/reports/decisions', { params });
    return response.data;
  },

  async exportDecisionsPdf(params = {}) {
    return this.downloadFile('/reports/decisions/export/pdf', params, 'decision_report.pdf');
  },

  async exportDecisionsExcel(params = {}) {
    return this.downloadFile('/reports/decisions/export/excel', params, 'decision_report.xlsx');
  },

  // Approval Reports
  async getApprovalsReport(params = {}) {
    const response = await client.get('/reports/approvals', { params });
    return response.data;
  },

  async exportApprovalsPdf(params = {}) {
    return this.downloadFile('/reports/approvals/export/pdf', params, 'approval_report.pdf');
  },

  async exportApprovalsExcel(params = {}) {
    return this.downloadFile('/reports/approvals/export/excel', params, 'approval_report.xlsx');
  },

  // Team Reports
  async getTeamReport(params = {}) {
    const response = await client.get('/reports/team', { params });
    return response.data;
  },

  async exportTeamPdf(params = {}) {
    return this.downloadFile('/reports/team/export/pdf', params, 'team_report.pdf');
  },

  async exportTeamExcel(params = {}) {
    return this.downloadFile('/reports/team/export/excel', params, 'team_report.xlsx');
  },

  // Audit Reports
  async getAuditReport(params = {}) {
    const response = await client.get('/reports/audit', { params });
    return response.data;
  },

  async exportAuditPdf(params = {}) {
    return this.downloadFile('/reports/audit/export/pdf', params, 'audit_report.pdf');
  },

  async exportAuditExcel(params = {}) {
    return this.downloadFile('/reports/audit/export/excel', params, 'audit_report.xlsx');
  },

  // Helper method for binary file download
  async downloadFile(url, params, defaultFilename) {
    const response = await client.get(url, {
      params,
      responseType: 'blob',
    });

    const blob = new Blob([response.data]);
    const downloadUrl = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = downloadUrl;

    // Check content-disposition header if available
    const disposition = response.headers['content-disposition'];
    let filename = defaultFilename;
    if (disposition && disposition.indexOf('filename=') !== -1) {
      const matches = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/.exec(disposition);
      if (matches != null && matches[1]) {
        filename = matches[1].replace(/['"]/g, '');
      }
    }

    link.setAttribute('download', filename);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(downloadUrl);
  },
};
