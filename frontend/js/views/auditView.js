// Audit, Security & Activity Logs View (Admin / Manager)
import { auth } from '../auth.js';
import { auditApi } from '../api.js';
import { formatDate, escapeHtml, errorState, showToast } from '../components/ui.js';

export async function renderAuditView(subtab = 'audit', filters = {}) {
  const isAdmin = auth.isAdmin();
  const isManager = auth.isManager();

  if (!isAdmin && !isManager) {
    return `
      <div class="panel">
        <div class="state-container">
          <div class="state-icon">🚫</div>
          <div class="state-title">Access Restricted (403 Forbidden)</div>
          <p class="state-desc">You do not have administrative privileges to view regulatory audit logs.</p>
          <a href="#dashboard" class="btn btn-primary" style="margin-top: 12px;">Return to Dashboard</a>
        </div>
      </div>
    `;
  }

  let tableContent = '';
  try {
    if (subtab === 'audit') {
      const logsRes = await auditApi.getLogs(filters).catch(() => ({ items: [] }));
      const items = logsRes.items || [];

      tableContent = `
        <div class="table-container">
          <table class="data-table">
            <thead>
              <tr>
                <th>Action</th>
                <th>Entity Type</th>
                <th>Entity ID</th>
                <th>User ID</th>
                <th>Details / Changes</th>
                <th>IP Address</th>
                <th>Timestamp</th>
              </tr>
            </thead>
            <tbody>
              ${items.length ? items.map(l => `
                <tr>
                  <td><span class="badge badge-role">${escapeHtml(l.action)}</span></td>
                  <td><strong>${escapeHtml(l.entity_type)}</strong></td>
                  <td>#${l.entity_id || '—'}</td>
                  <td>User #${l.user_id}</td>
                  <td>${escapeHtml(l.description || '—')}</td>
                  <td><code>${escapeHtml(l.ip_address || '127.0.0.1')}</code></td>
                  <td>${formatDate(l.created_at)}</td>
                </tr>
              `).join('') : `
                <tr><td colspan="7" class="state-desc" style="text-align:center; padding: 24px;">No audit logs recorded.</td></tr>
              `}
            </tbody>
          </table>
        </div>
      `;
    } else if (subtab === 'security') {
      const secLogs = await auditApi.getSecurityLogs().catch(() => []);
      tableContent = `
        <div class="table-container">
          <table class="data-table">
            <thead>
              <tr>
                <th>Event Type</th>
                <th>User ID</th>
                <th>Description</th>
                <th>IP Address</th>
                <th>Timestamp</th>
              </tr>
            </thead>
            <tbody>
              ${secLogs.length ? secLogs.map(s => `
                <tr>
                  <td><span class="badge ${s.event_type.includes('SUCCESS') ? 'badge-approved' : 'badge-rejected'}">${escapeHtml(s.event_type)}</span></td>
                  <td>User #${s.user_id || 'Unknown'}</td>
                  <td>${escapeHtml(s.description || '—')}</td>
                  <td><code>${escapeHtml(s.ip_address || '127.0.0.1')}</code></td>
                  <td>${formatDate(s.created_at)}</td>
                </tr>
              `).join('') : `
                <tr><td colspan="5" class="state-desc" style="text-align:center; padding: 24px;">No security logs found.</td></tr>
              `}
            </tbody>
          </table>
        </div>
      `;
    } else if (subtab === 'access') {
      const accLogs = await auditApi.getAccessLogs().catch(() => []);
      tableContent = `
        <div class="table-container">
          <table class="data-table">
            <thead>
              <tr>
                <th>Action</th>
                <th>Resource Type</th>
                <th>Resource ID</th>
                <th>User ID</th>
                <th>Timestamp</th>
              </tr>
            </thead>
            <tbody>
              ${accLogs.length ? accLogs.map(a => `
                <tr>
                  <td><strong>${escapeHtml(a.action)}</strong></td>
                  <td>${escapeHtml(a.resource_type)}</td>
                  <td>#${a.resource_id}</td>
                  <td>User #${a.user_id}</td>
                  <td>${formatDate(a.created_at)}</td>
                </tr>
              `).join('') : `
                <tr><td colspan="5" class="state-desc" style="text-align:center; padding: 24px;">No access logs recorded.</td></tr>
              `}
            </tbody>
          </table>
        </div>
      `;
    } else {
      // Activities
      const activities = await auditApi.getActivities().catch(() => []);
      tableContent = `
        <div class="table-container">
          <table class="data-table">
            <thead>
              <tr>
                <th>Action</th>
                <th>Entity Type</th>
                <th>Entity ID</th>
                <th>User ID</th>
                <th>Description</th>
                <th>Timestamp</th>
              </tr>
            </thead>
            <tbody>
              ${activities.length ? activities.map(act => `
                <tr>
                  <td><strong>${escapeHtml(act.action)}</strong></td>
                  <td>${escapeHtml(act.entity_type)}</td>
                  <td>#${act.entity_id || '—'}</td>
                  <td>User #${act.user_id}</td>
                  <td>${escapeHtml(act.description || '—')}</td>
                  <td>${formatDate(act.created_at)}</td>
                </tr>
              `).join('') : `
                <tr><td colspan="6" class="state-desc" style="text-align:center; padding: 24px;">No activities recorded.</td></tr>
              `}
            </tbody>
          </table>
        </div>
      `;
    }
  } catch (err) {
    tableContent = errorState(err.message);
  }

  return `
    <div class="page-header">
      <div class="page-header-text">
        <h1>Audit & Compliance Activity</h1>
        <p>Immutable traceability and security events across all decision artifacts.</p>
      </div>
    </div>

    <!-- Sub-tabs -->
    <div class="tabs" id="audit-tabs">
      <button class="tab-item ${subtab === 'audit' ? 'active' : ''}" data-subtab="audit">Audit Trail</button>
      <button class="tab-item ${subtab === 'security' ? 'active' : ''}" data-subtab="security">Security & Logins</button>
      <button class="tab-item ${subtab === 'access' ? 'active' : ''}" data-subtab="access">Access Logs</button>
      <button class="tab-item ${subtab === 'activity' ? 'active' : ''}" data-subtab="activity">User Activities</button>
    </div>

    <div class="panel">
      ${tableContent}
    </div>
  `;
}

export function bindAuditEvents() {
  document.querySelectorAll('#audit-tabs .tab-item').forEach(btn => {
    btn.onclick = () => {
      const subtab = btn.dataset.subtab;
      window.location.hash = `#audit?subtab=${subtab}`;
    };
  });
}
