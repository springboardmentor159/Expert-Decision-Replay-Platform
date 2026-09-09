// Role-Specific Dashboard Views (Employee, Reviewer, Manager, Admin)
import { auth } from '../auth.js';
import { dashboardApi, approvalsApi, decisionsApi } from '../api.js';
import { statCard, statusBadge, formatDate, escapeHtml, loadingState, errorState } from '../components/ui.js';

export async function renderDashboardView() {
  const role = auth.getRole();

  if (role === 'employee') {
    return renderEmployeeDashboard();
  } else if (role === 'reviewer') {
    return renderReviewerDashboard();
  } else if (role === 'manager') {
    return renderManagerDashboard();
  } else {
    return renderAdminDashboard();
  }
}

// 1. Employee Dashboard
async function renderEmployeeDashboard() {
  try {
    const [metrics, decisions, activities] = await Promise.all([
      dashboardApi.getEmployee().catch(() => ({})),
      dashboardApi.getEmployeeDecisions().catch(() => []),
      dashboardApi.getEmployeeRecentActivities().catch(() => []),
    ]);

    const total = metrics.total_decisions || 0;
    const drafts = metrics.draft_decisions || 0;
    const underReview = metrics.under_review || 0;
    const approved = metrics.approved_decisions || 0;

    return `
      <div class="page-header">
        <div class="page-header-text">
          <h1>Employee Dashboard</h1>
          <p>Welcome back, ${escapeHtml(auth.currentUser?.full_name)}. Here is the current pulse of your active proposals.</p>
        </div>
        <div class="page-header-actions">
          <a href="#decisions/create" class="btn btn-primary">+ Create Decision</a>
        </div>
      </div>

      <!-- Stat Cards Grid -->
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 24px;">
        ${statCard({ label: 'My Decisions', value: total, meta: 'All created proposals', accent: true })}
        ${statCard({ label: 'Draft Proposals', value: drafts, meta: 'In progress' })}
        ${statCard({ label: 'Under Review', value: underReview, meta: 'Awaiting feedback' })}
        ${statCard({ label: 'Approved Decisions', value: approved, meta: 'Finalized and active' })}
      </div>

      <!-- Two-column Workbench -->
      <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 24px;">
        <!-- Recent Decisions -->
        <div class="panel">
          <div class="panel-header">
            <div>
              <h2 class="panel-title">My Recent Decisions</h2>
              <p class="panel-subtitle">Proposals you authored in this workspace</p>
            </div>
            <a href="#decisions" class="btn btn-sm btn-outline">View All</a>
          </div>

          ${decisions.length ? `
            <div class="table-container">
              <table class="data-table">
                <thead>
                  <tr>
                    <th>Title & Category</th>
                    <th>Status</th>
                    <th>Last Updated</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  ${decisions.slice(0, 8).map(d => `
                    <tr>
                      <td>
                        <strong>${escapeHtml(d.title)}</strong><br>
                        <small style="color: var(--text-secondary);">${escapeHtml(d.category)}</small>
                      </td>
                      <td>${statusBadge(d.status)}</td>
                      <td>${formatDate(d.updated_at || d.created_at)}</td>
                      <td>
                        <a href="#decisions/${d.id}" class="btn btn-sm btn-outline">View</a>
                      </td>
                    </tr>
                  `).join('')}
                </tbody>
              </table>
            </div>
          ` : `
            <div class="state-container" style="padding: 24px;">
              <div class="state-title">No decisions authored yet</div>
              <p class="state-desc">Capture your first proposal with alternatives and criteria.</p>
              <a href="#decisions/create" class="btn btn-primary btn-sm" style="margin-top: 10px;">Create Decision</a>
            </div>
          `}
        </div>

        <!-- Recent Activity Feed -->
        <div class="panel">
          <div class="panel-header">
            <h2 class="panel-title">Recent Activity</h2>
          </div>
          ${activities.length ? `
            <div class="timeline-list">
              ${activities.slice(0, 10).map(act => `
                <div class="timeline-node">
                  <div class="timeline-header">
                    <span class="timeline-action">${escapeHtml(act.description || act.action)}</span>
                  </div>
                  <div class="timeline-time">${formatDate(act.created_at)}</div>
                </div>
              `).join('')}
            </div>
          ` : `
            <div class="state-container" style="padding: 24px;">
              <div class="state-desc">No recent activity recorded yet.</div>
            </div>
          `}
        </div>
      </div>
    `;
  } catch (err) {
    return errorState(err.message);
  }
}

// 2. Reviewer Dashboard
async function renderReviewerDashboard() {
  try {
    const [allApprovals, pendingApprovals] = await Promise.all([
      approvalsApi.list().catch(() => []),
      approvalsApi.listPending().catch(() => []),
    ]);

    const completed = allApprovals.filter(a => a.status === 'Approved' || a.status === 'Rejected');

    return `
      <div class="page-header">
        <div class="page-header-text">
          <h1>Reviewer Workspace</h1>
          <p>Assigned review queue and governance responsibilities for ${escapeHtml(auth.currentUser?.full_name)}.</p>
        </div>
      </div>

      <!-- Stat Cards -->
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 24px;">
        ${statCard({ label: 'Pending Reviews', value: pendingApprovals.length, meta: 'Requires your evaluation', accent: true })}
        ${statCard({ label: 'Completed Reviews', value: completed.length, meta: 'Decided by you' })}
        ${statCard({ label: 'Total Assigned', value: allApprovals.length, meta: 'Lifetime assignments' })}
      </div>

      <!-- Pending Reviews Queue -->
      <div class="panel" style="margin-bottom: 24px;">
        <div class="panel-header">
          <div>
            <h2 class="panel-title">Pending Decision Reviews</h2>
            <p class="panel-subtitle">Decisions awaiting your review and recommendation</p>
          </div>
        </div>

        ${pendingApprovals.length ? `
          <div class="table-container">
            <table class="data-table">
              <thead>
                <tr>
                  <th>Approval #</th>
                  <th>Decision ID</th>
                  <th>Assigned Date</th>
                  <th>Status</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                ${pendingApprovals.map(app => `
                  <tr>
                    <td><strong>Approval #${app.id}</strong></td>
                    <td>Decision #${app.decision_id}</td>
                    <td>${formatDate(app.created_at)}</td>
                    <td>${statusBadge(app.status)}</td>
                    <td>
                      <a href="#decisions/${app.decision_id}" class="btn btn-sm btn-primary">Review Details & Act</a>
                    </td>
                  </tr>
                `).join('')}
              </tbody>
            </table>
          </div>
        ` : `
          <div class="state-container" style="padding: 32px;">
            <div class="state-icon">🎉</div>
            <div class="state-title">Your review queue is clear!</div>
            <p class="state-desc">You have no pending decision reviews at this time.</p>
          </div>
        `}
      </div>

      <!-- Recently Completed Reviews -->
      <div class="panel">
        <div class="panel-header">
          <h2 class="panel-title">Recently Reviewed Decisions</h2>
        </div>
        ${completed.length ? `
          <div class="table-container">
            <table class="data-table">
              <thead>
                <tr>
                  <th>Approval #</th>
                  <th>Decision ID</th>
                  <th>Outcome</th>
                  <th>Comments</th>
                  <th>Completed At</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                ${completed.slice(0, 8).map(app => `
                  <tr>
                    <td>Approval #${app.id}</td>
                    <td>Decision #${app.decision_id}</td>
                    <td>${statusBadge(app.status)}</td>
                    <td>${escapeHtml(app.comments || '—')}</td>
                    <td>${formatDate(app.completed_at)}</td>
                    <td>
                      <a href="#decisions/${app.decision_id}" class="btn btn-sm btn-outline">View</a>
                    </td>
                  </tr>
                `).join('')}
              </tbody>
            </table>
          </div>
        ` : `
          <div class="state-container" style="padding: 24px;">
            <div class="state-desc">No past reviews found.</div>
          </div>
        `}
      </div>
    `;
  } catch (err) {
    return errorState(err.message);
  }
}

// 3. Manager Dashboard
async function renderManagerDashboard() {
  try {
    const [managerMetrics, teamDecisions, pendingApprovals] = await Promise.all([
      dashboardApi.getManager().catch(() => ({})),
      dashboardApi.getManagerTeamDecisions().catch(() => []),
      dashboardApi.getManagerPendingApprovals().catch(() => []),
    ]);

    const teamTotal = managerMetrics.team_decisions || 0;
    const pendingCount = managerMetrics.pending_approvals || pendingApprovals.length;
    const approvedCount = managerMetrics.approved_decisions || 0;
    const rejectedCount = managerMetrics.rejected_decisions || 0;

    return `
      <div class="page-header">
        <div class="page-header-text">
          <h1>Manager Dashboard</h1>
          <p>Department leadership overview for <strong>${escapeHtml(auth.currentUser?.department || 'Team')}</strong>.</p>
        </div>
        <div class="page-header-actions">
          <a href="#reports" class="btn btn-outline">Decision Analytics</a>
          <a href="#decisions/create" class="btn btn-primary">+ New Decision</a>
        </div>
      </div>

      <!-- Stat Cards -->
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 24px;">
        ${statCard({ label: 'Team Decisions', value: teamTotal, meta: `${auth.currentUser?.department} Department`, accent: true })}
        ${statCard({ label: 'Pending Approvals', value: pendingCount, meta: 'Action required' })}
        ${statCard({ label: 'Approved Decisions', value: approvedCount, meta: 'Completed' })}
        ${statCard({ label: 'Rejected Decisions', value: rejectedCount, meta: 'Declined' })}
      </div>

      <!-- Pending Approvals Box -->
      <div class="panel" style="margin-bottom: 24px;">
        <div class="panel-header">
          <div>
            <h2 class="panel-title">Pending Team Approvals</h2>
            <p class="panel-subtitle">Decisions requiring managerial sign-off or reviewer allocation</p>
          </div>
        </div>

        ${pendingApprovals.length ? `
          <div class="table-container">
            <table class="data-table">
              <thead>
                <tr>
                  <th>Approval #</th>
                  <th>Decision ID</th>
                  <th>Assigned Date</th>
                  <th>Status</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                ${pendingApprovals.map(app => `
                  <tr>
                    <td><strong>Approval #${app.id}</strong></td>
                    <td>Decision #${app.decision_id}</td>
                    <td>${formatDate(app.created_at)}</td>
                    <td>${statusBadge(app.status)}</td>
                    <td>
                      <a href="#decisions/${app.decision_id}" class="btn btn-sm btn-primary">Review & Decide</a>
                    </td>
                  </tr>
                `).join('')}
              </tbody>
            </table>
          </div>
        ` : `
          <div class="state-container" style="padding: 24px;">
            <div class="state-desc">No pending approvals for your team.</div>
          </div>
        `}
      </div>

      <!-- Team Decisions -->
      <div class="panel">
        <div class="panel-header">
          <div>
            <h2 class="panel-title">Recent Team Proposals</h2>
            <p class="panel-subtitle">Decisions generated across your department</p>
          </div>
          <a href="#decisions" class="btn btn-sm btn-outline">All Decisions</a>
        </div>

        ${teamDecisions.length ? `
          <div class="table-container">
            <table class="data-table">
              <thead>
                <tr>
                  <th>Title</th>
                  <th>Category</th>
                  <th>Status</th>
                  <th>Created</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                ${teamDecisions.slice(0, 8).map(d => `
                  <tr>
                    <td><strong>${escapeHtml(d.title)}</strong></td>
                    <td><span class="badge badge-category">${escapeHtml(d.category)}</span></td>
                    <td>${statusBadge(d.status)}</td>
                    <td>${formatDate(d.created_at)}</td>
                    <td><a href="#decisions/${d.id}" class="btn btn-sm btn-outline">Inspect</a></td>
                  </tr>
                `).join('')}
              </tbody>
            </table>
          </div>
        ` : `
          <div class="state-container" style="padding: 24px;">
            <div class="state-desc">No team decisions recorded yet.</div>
          </div>
        `}
      </div>
    `;
  } catch (err) {
    return errorState(err.message);
  }
}

// 4. Admin Dashboard
async function renderAdminDashboard() {
  try {
    const [adminSummary, analytics, approvalStats] = await Promise.all([
      dashboardApi.getAdmin().catch(() => ({})),
      dashboardApi.getAdminAnalytics().catch(() => ({})),
      dashboardApi.getAdminApprovalStats().catch(() => ({})),
    ]);

    const totalUsers = adminSummary.users || analytics.total_users || 0;
    const totalDecisions = adminSummary.decisions?.total_decisions || 0;
    const activeUsers = analytics.active_users || 0;
    const totalApprovals = approvalStats.total_approvals || 0;
    const completionRate = approvalStats.completion_rate !== undefined ? `${approvalStats.completion_rate}%` : '0%';
    const activities = adminSummary.recent_system_activities || [];

    return `
      <div class="page-header">
        <div class="page-header-text">
          <h1>System Administration Dashboard</h1>
          <p>Global oversight of platform users, decision activity, compliance audit, and governance throughput.</p>
        </div>
        <div class="page-header-actions">
          <a href="#audit" class="btn btn-outline">Audit Logs</a>
          <a href="#reports" class="btn btn-primary">System Reports</a>
        </div>
      </div>

      <!-- KPI Stat Grid -->
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 24px;">
        ${statCard({ label: 'Total Users', value: totalUsers, meta: 'Registered accounts', accent: true })}
        ${statCard({ label: 'Active Users', value: activeUsers, meta: 'Participating members' })}
        ${statCard({ label: 'Total Decisions', value: totalDecisions, meta: 'Proposals captured' })}
        ${statCard({ label: 'Approvals Processed', value: totalApprovals, meta: `Completion rate: ${completionRate}` })}
      </div>

      <!-- Admin Panels Grid -->
      <div style="display: grid; grid-template-columns: 1.6fr 1fr; gap: 24px;">
        <!-- System Activity -->
        <div class="panel">
          <div class="panel-header">
            <div>
              <h2 class="panel-title">System-Wide Activity Log</h2>
              <p class="panel-subtitle">Live stream of actions and state changes across the organization</p>
            </div>
            <a href="#audit" class="btn btn-sm btn-outline">All Logs</a>
          </div>

          ${activities.length ? `
            <div class="table-container">
              <table class="data-table">
                <thead>
                  <tr>
                    <th>Action</th>
                    <th>Entity</th>
                    <th>User ID</th>
                    <th>Timestamp</th>
                  </tr>
                </thead>
                <tbody>
                  ${activities.slice(0, 10).map(act => `
                    <tr>
                      <td><strong>${escapeHtml(act.action)}</strong></td>
                      <td>${escapeHtml(act.entity_type)} #${act.entity_id || '—'}</td>
                      <td>User #${act.user_id}</td>
                      <td>${formatDate(act.created_at)}</td>
                    </tr>
                  `).join('')}
                </tbody>
              </table>
            </div>
          ` : `
            <div class="state-container" style="padding: 24px;">
              <div class="state-desc">No recent system activities found.</div>
            </div>
          `}
        </div>

        <!-- Governance Stats Box -->
        <div class="panel">
          <div class="panel-header">
            <h2 class="panel-title">Governance Metrics</h2>
          </div>

          <div style="display: flex; flex-direction: column; gap: 14px;">
            <div style="padding: 14px; background: var(--bg-surface-elevated); border-radius: 8px;">
              <div style="font-size: 12px; color: var(--text-muted); text-transform: uppercase;">Average Approval Turnaround</div>
              <div style="font-size: 24px; font-weight: 700; color: var(--teal-300); margin-top: 4px;">
                ${approvalStats.average_approval_time ? `${Math.round(approvalStats.average_approval_time / 60)} minutes` : 'Instant / Fast'}
              </div>
            </div>

            <div style="padding: 14px; background: var(--bg-surface-elevated); border-radius: 8px;">
              <div style="font-size: 12px; color: var(--text-muted); text-transform: uppercase;">Pending Approval Backlog</div>
              <div style="font-size: 24px; font-weight: 700; color: var(--status-review-text); margin-top: 4px;">
                ${approvalStats.pending_approvals || 0}
              </div>
            </div>

            <div style="padding: 14px; background: var(--bg-surface-elevated); border-radius: 8px;">
              <div style="font-size: 12px; color: var(--text-muted); text-transform: uppercase;">Completed Approvals</div>
              <div style="font-size: 24px; font-weight: 700; color: var(--status-approved-text); margin-top: 4px;">
                ${approvalStats.completed_approvals || 0}
              </div>
            </div>
          </div>
        </div>
      </div>
    `;
  } catch (err) {
    return errorState(err.message);
  }
}
