// Reports Module & PDF/Excel Export Views
import { auth } from '../auth.js';
import { reportsApi } from '../api.js';
import { statCard, statusBadge, formatDate, escapeHtml, showToast, errorState } from '../components/ui.js';

export async function renderReportsView(activeTab = 'decisions', filterParams = {}) {
  const isPrivileged = auth.canManageTeam();
  const isAdmin = auth.isAdmin();

  const categories = ['Technology', 'Finance', 'Operations', 'Human Resources', 'Security', 'Product', 'Infrastructure', 'Strategy'];
  const statuses = ['Draft', 'Under Review', 'Approved', 'Rejected', 'Archived'];

  let contentHtml = '';

  try {
    if (activeTab === 'decisions') {
      contentHtml = await renderDecisionsReport(filterParams, categories, statuses);
    } else if (activeTab === 'approvals') {
      contentHtml = await renderApprovalsReport(filterParams);
    } else if (activeTab === 'teams') {
      contentHtml = await renderTeamsReport(filterParams, categories, statuses);
    } else if (activeTab === 'audit') {
      contentHtml = await renderAuditReport(filterParams);
    }
  } catch (err) {
    contentHtml = errorState(err.message);
  }

  return `
    <div class="page-header">
      <div class="page-header-text">
        <h1>Reports & Governance Intelligence</h1>
        <p>Analyze organizational decision health, turnaround velocity, and export compliance audits.</p>
      </div>
    </div>

    <!-- Report Sub-Navigation Tabs -->
    <div class="tabs" id="reports-nav-tabs">
      <button class="tab-item ${activeTab === 'decisions' ? 'active' : ''}" data-tab="decisions">Decision Reports</button>
      <button class="tab-item ${activeTab === 'approvals' ? 'active' : ''}" data-tab="approvals">Approval Reports</button>
      ${isPrivileged ? `<button class="tab-item ${activeTab === 'teams' ? 'active' : ''}" data-tab="teams">Team Reports</button>` : ''}
      ${isAdmin ? `<button class="tab-item ${activeTab === 'audit' ? 'active' : ''}" data-tab="audit">Compliance Audit Reports</button>` : ''}
    </div>

    ${contentHtml}
  `;
}

// 1. Decision Report
async function renderDecisionsReport(filters, categories, statuses) {
  const report = await reportsApi.decisions(filters).catch(() => ({ items: [], summary: {} }));
  const summary = report.summary || {};
  const items = report.items || [];

  return `
    <!-- Filters & Export Header -->
    <div class="panel" style="margin-bottom: 24px;">
      <div class="panel-header" style="margin-bottom: 14px;">
        <h2 class="panel-title">Decision Health & Volume</h2>
        <div style="display: flex; gap: 8px;">
          <button class="btn btn-sm btn-outline btn-export-pdf" data-type="decisions">📄 Export PDF</button>
          <button class="btn btn-sm btn-primary btn-export-excel" data-type="decisions">📊 Export Excel</button>
        </div>
      </div>

      <div class="filter-toolbar" style="margin-bottom: 0;">
        <select id="rep-dec-category" class="form-select filter-select">
          <option value="">All Categories</option>
          ${categories.map(c => `<option value="${c}" ${filters.category === c ? 'selected' : ''}>${c}</option>`).join('')}
        </select>

        <select id="rep-dec-status" class="form-select filter-select">
          <option value="">All Statuses</option>
          ${statuses.map(s => `<option value="${s}" ${filters.status === s ? 'selected' : ''}>${s}</option>`).join('')}
        </select>

        <button id="btn-filter-decisions-report" class="btn btn-outline">Apply Filters</button>
        <button id="btn-reset-decisions-report" class="btn btn-outline">Reset</button>
      </div>
    </div>

    <!-- Summary Stats -->
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 14px; margin-bottom: 24px;">
      ${statCard({ label: 'Total Decisions', value: summary.total_decisions || 0, accent: true })}
      ${statCard({ label: 'Drafts', value: summary.draft_decisions || 0 })}
      ${statCard({ label: 'Under Review', value: summary.under_review || 0 })}
      ${statCard({ label: 'Approved', value: summary.approved_decisions || 0 })}
      ${statCard({ label: 'Rejected', value: summary.rejected_decisions || 0 })}
    </div>

    <!-- Report Table -->
    <div class="panel">
      ${items.length ? `
        <div class="table-container">
          <table class="data-table">
            <thead>
              <tr>
                <th>Decision Title</th>
                <th>Category</th>
                <th>Status</th>
                <th>Alternatives</th>
                <th>Approvals</th>
                <th>Created Date</th>
              </tr>
            </thead>
            <tbody>
              ${items.map(d => `
                <tr>
                  <td><strong>${escapeHtml(d.title)}</strong></td>
                  <td><span class="badge badge-category">${escapeHtml(d.category)}</span></td>
                  <td>${statusBadge(d.status)}</td>
                  <td>${d.alternatives}</td>
                  <td>${d.approvals}</td>
                  <td>${formatDate(d.created_date)}</td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>
      ` : `
        <div class="state-container">
          <div class="state-desc">No decisions match the selected report criteria.</div>
        </div>
      `}
    </div>
  `;
}

// 2. Approval Report
async function renderApprovalsReport(filters) {
  const report = await reportsApi.approvals(filters).catch(() => ({ items: [], summary: {} }));
  const summary = report.summary || {};
  const items = report.items || [];

  return `
    <div class="panel" style="margin-bottom: 24px;">
      <div class="panel-header" style="margin-bottom: 14px;">
        <h2 class="panel-title">Governance Turnaround & Velocity</h2>
        <div style="display: flex; gap: 8px;">
          <button class="btn btn-sm btn-outline btn-export-pdf" data-type="approvals">📄 Export PDF</button>
          <button class="btn btn-sm btn-primary btn-export-excel" data-type="approvals">📊 Export Excel</button>
        </div>
      </div>

      <div class="filter-toolbar" style="margin-bottom: 0;">
        <select id="rep-app-status" class="form-select filter-select">
          <option value="">All Review Statuses</option>
          <option value="Pending" ${filters.status === 'Pending' ? 'selected' : ''}>Pending</option>
          <option value="Approved" ${filters.status === 'Approved' ? 'selected' : ''}>Approved</option>
          <option value="Rejected" ${filters.status === 'Rejected' ? 'selected' : ''}>Rejected</option>
        </select>

        <button id="btn-filter-approvals-report" class="btn btn-outline">Apply Filters</button>
        <button id="btn-reset-approvals-report" class="btn btn-outline">Reset</button>
      </div>
    </div>

    <!-- Summary Stats -->
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 14px; margin-bottom: 24px;">
      ${statCard({ label: 'Total Assigned', value: summary.total_approvals || 0, accent: true })}
      ${statCard({ label: 'Pending Approvals', value: summary.pending_approvals || 0 })}
      ${statCard({ label: 'Approved Decisions', value: summary.approved_approvals || 0 })}
      ${statCard({ label: 'Rejected Decisions', value: summary.rejected_approvals || 0 })}
      ${statCard({ label: 'Completion Rate', value: summary.completion_rate ? `${summary.completion_rate}%` : '0%' })}
    </div>

    <!-- Report Table -->
    <div class="panel">
      ${items.length ? `
        <div class="table-container">
          <table class="data-table">
            <thead>
              <tr>
                <th>Decision</th>
                <th>Assigned Reviewer</th>
                <th>Outcome</th>
                <th>Assigned Date</th>
                <th>Completed Date</th>
                <th>Turnaround Time</th>
              </tr>
            </thead>
            <tbody>
              ${items.map(a => `
                <tr>
                  <td><strong>${escapeHtml(a.decision_title || `Decision #${a.decision_id}`)}</strong></td>
                  <td>${escapeHtml(a.reviewer || `User #${a.reviewer_id}`)}</td>
                  <td>${statusBadge(a.approval_status)}</td>
                  <td>${formatDate(a.assigned_date)}</td>
                  <td>${formatDate(a.completed_date)}</td>
                  <td>${a.turnaround_seconds ? `${Math.round(a.turnaround_seconds / 60)} mins` : 'Pending'}</td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>
      ` : `
        <div class="state-container">
          <div class="state-desc">No approval records found matching criteria.</div>
        </div>
      `}
    </div>
  `;
}

// 3. Team Report
async function renderTeamsReport(filters, categories, statuses) {
  const report = await reportsApi.teams(filters).catch(() => ({ items: [] }));
  const items = report.items || [];

  return `
    <div class="panel" style="margin-bottom: 24px;">
      <div class="panel-header" style="margin-bottom: 14px;">
        <h2 class="panel-title">Department & Team Analytics</h2>
        <div style="display: flex; gap: 8px;">
          <button class="btn btn-sm btn-outline btn-export-pdf" data-type="teams">📄 Export PDF</button>
          <button class="btn btn-sm btn-primary btn-export-excel" data-type="teams">📊 Export Excel</button>
        </div>
      </div>
    </div>

    <div class="panel">
      ${items.length ? `
        <div class="table-container">
          <table class="data-table">
            <thead>
              <tr>
                <th>Department / Team</th>
                <th>Team Members</th>
                <th>Total Decisions</th>
                <th>Approved</th>
                <th>Rejected</th>
                <th>Pending / In-Flight</th>
              </tr>
            </thead>
            <tbody>
              ${items.map(t => `
                <tr>
                  <td><strong>${escapeHtml(t.team || 'Unassigned')}</strong></td>
                  <td>${t.members} members</td>
                  <td><strong>${t.total_decisions}</strong></td>
                  <td style="color: var(--status-approved-text);">${t.approved_decisions}</td>
                  <td style="color: var(--status-rejected-text);">${t.rejected_decisions}</td>
                  <td>${t.pending_decisions}</td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>
      ` : `
        <div class="state-container">
          <div class="state-desc">No team records found.</div>
        </div>
      `}
    </div>
  `;
}

// 4. Audit Report
async function renderAuditReport(filters) {
  const report = await reportsApi.audit(filters).catch(() => ({ items: [], total: 0 }));
  const items = report.items || [];

  return `
    <div class="panel" style="margin-bottom: 24px;">
      <div class="panel-header" style="margin-bottom: 14px;">
        <h2 class="panel-title">Regulatory Compliance & Audit Log Export</h2>
        <div style="display: flex; gap: 8px;">
          <button class="btn btn-sm btn-outline btn-export-pdf" data-type="audit">📄 Export PDF</button>
          <button class="btn btn-sm btn-primary btn-export-excel" data-type="audit">📊 Export Excel</button>
        </div>
      </div>
    </div>

    <div class="panel">
      ${items.length ? `
        <div class="table-container">
          <table class="data-table">
            <thead>
              <tr>
                <th>Action</th>
                <th>Entity</th>
                <th>User ID</th>
                <th>Details</th>
                <th>Timestamp</th>
              </tr>
            </thead>
            <tbody>
              ${items.map(log => `
                <tr>
                  <td><strong>${escapeHtml(log.action)}</strong></td>
                  <td>${escapeHtml(log.entity_type)} #${log.entity_id || ''}</td>
                  <td>User #${log.user_id}</td>
                  <td>${escapeHtml(log.description || '—')}</td>
                  <td>${formatDate(log.created_at)}</td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>
      ` : `
        <div class="state-container">
          <div class="state-desc">No audit log records available.</div>
        </div>
      `}
    </div>
  `;
}

export function bindReportsEvents(activeTab = 'decisions') {
  // Tab Switching
  document.querySelectorAll('#reports-nav-tabs .tab-item').forEach(btn => {
    btn.onclick = () => {
      const tab = btn.dataset.tab;
      window.location.hash = `#reports?tab=${tab}`;
    };
  });

  // Decision Filter buttons
  const applyDecBtn = document.getElementById('btn-filter-decisions-report');
  if (applyDecBtn) {
    applyDecBtn.onclick = () => {
      const cat = document.getElementById('rep-dec-category')?.value;
      const stat = document.getElementById('rep-dec-status')?.value;
      const params = new URLSearchParams({ tab: 'decisions' });
      if (cat) params.set('category', cat);
      if (stat) params.set('status', stat);
      window.location.hash = `#reports?${params.toString()}`;
    };
  }

  const resetDecBtn = document.getElementById('btn-reset-decisions-report');
  if (resetDecBtn) {
    resetDecBtn.onclick = () => {
      window.location.hash = '#reports?tab=decisions';
    };
  }

  // Approval Filter buttons
  const applyAppBtn = document.getElementById('btn-filter-approvals-report');
  if (applyAppBtn) {
    applyAppBtn.onclick = () => {
      const stat = document.getElementById('rep-app-status')?.value;
      const params = new URLSearchParams({ tab: 'approvals' });
      if (stat) params.set('status', stat);
      window.location.hash = `#reports?${params.toString()}`;
    };
  }

  const resetAppBtn = document.getElementById('btn-reset-approvals-report');
  if (resetAppBtn) {
    resetAppBtn.onclick = () => {
      window.location.hash = '#reports?tab=approvals';
    };
  }

  // File Exports (PDF & Excel)
  const triggerDownload = async (type, format) => {
    showToast(`Generating ${format.toUpperCase()} report...`, 'info');
    try {
      const urlParams = new URLSearchParams(window.location.hash.split('?')[1] || '');
      const filters = Object.fromEntries(urlParams);
      delete filters.tab;

      let blob;
      if (type === 'decisions') {
        blob = await reportsApi.exportDecisions(format, filters);
      } else if (type === 'approvals') {
        blob = await reportsApi.exportApprovals(format, filters);
      } else if (type === 'teams') {
        blob = await reportsApi.exportTeams(format, filters);
      } else if (type === 'audit') {
        blob = await reportsApi.exportAudit(format, filters);
      }

      if (blob) {
        const downloadUrl = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = downloadUrl;
        link.download = `${type}_report.${format === 'excel' ? 'xlsx' : 'pdf'}`;
        document.body.appendChild(link);
        link.click();
        link.remove();
        URL.revokeObjectURL(downloadUrl);
        showToast(`${format.toUpperCase()} report downloaded!`, 'success');
      }
    } catch (err) {
      showToast(err.message || 'Export failed', 'error');
    }
  };

  document.querySelectorAll('.btn-export-pdf').forEach(btn => {
    btn.onclick = () => triggerDownload(btn.dataset.type, 'pdf');
  });

  document.querySelectorAll('.btn-export-excel').forEach(btn => {
    btn.onclick = () => triggerDownload(btn.dataset.type, 'excel');
  });
}
