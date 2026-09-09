// Decision Details, Alternative Analysis, Discussions, Approvals, & Version History
import { auth } from '../auth.js';
import {
  decisionsApi,
  alternativesApi,
  discussionsApi,
  approvalsApi,
  authApi,
} from '../api.js';
import {
  statusBadge,
  riskBadge,
  formatDate,
  escapeHtml,
  showToast,
  showModal,
  errorState,
  loadingState,
} from '../components/ui.js';

export async function renderDecisionDetailView(decisionId) {
  const user = auth.currentUser;
  const userRole = auth.getRole();
  const canApprove = auth.canApprove();
  const canManage = auth.canManageTeam();

  try {
    const [
      decision,
      alternatives,
      comparison,
      comments,
      threads,
      meetingNotes,
      approvals,
      timeline,
      versions,
      tags,
    ] = await Promise.all([
      decisionsApi.get(decisionId),
      alternativesApi.listForDecision(decisionId).catch(() => []),
      alternativesApi.compare(decisionId).catch(() => null),
      discussionsApi.getComments(decisionId).catch(() => []),
      discussionsApi.getThreads(decisionId).catch(() => []),
      discussionsApi.getMeetingNotes(decisionId).catch(() => []),
      approvalsApi.list().catch(() => []),
      decisionsApi.getTimeline(decisionId).catch(() => []),
      decisionsApi.getVersions(decisionId).catch(() => []),
      decisionsApi.getTags(decisionId).catch(() => []),
    ]);

    const isCreator = decision.created_by === user?.id;
    const canModify = isCreator || canManage;
    const isArchived = decision.status === 'Archived';
    const isDraft = decision.status === 'Draft';
    const isUnderReview = decision.status === 'Under Review';

    // Filter approvals specific to this decision
    const decisionApprovals = approvals.filter(a => a.decision_id === Number(decisionId));
    const pendingApproval = decisionApprovals.find(a => a.status === 'Pending');

    return `
      <!-- Detail Hero Header -->
      <div class="page-header" style="align-items: center;">
        <div class="page-header-text">
          <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
            <a href="#decisions" class="btn btn-sm btn-outline">← Back to Decisions</a>
            <span class="badge badge-category">${escapeHtml(decision.category)}</span>
            ${statusBadge(decision.status)}
            <span style="font-size: 13px; color: var(--text-muted);">Decision #${decision.id}</span>
          </div>
          <h1>${escapeHtml(decision.title)}</h1>
          <p>Created by User #${decision.created_by} on ${formatDate(decision.created_at)} • Updated ${formatDate(decision.updated_at || decision.created_at)}</p>
        </div>

        <!-- Workflow Top Actions -->
        <div class="page-header-actions">
          ${canModify && !isArchived ? `
            <button class="btn btn-outline" id="btn-edit-details">Edit Metadata</button>
          ` : ''}

          ${canModify && isDraft ? `
            <button class="btn btn-success" id="btn-submit-workflow">Submit for Review</button>
          ` : ''}

          ${canManage && isUnderReview && !pendingApproval ? `
            <button class="btn btn-primary" id="btn-assign-reviewer">Assign Reviewer</button>
          ` : ''}

          ${canApprove && pendingApproval && (pendingApproval.reviewer_id === user?.id || canManage) ? `
            <button class="btn btn-success" id="btn-approve-action" data-approval-id="${pendingApproval.id}">✓ Approve</button>
            <button class="btn btn-danger" id="btn-reject-action" data-approval-id="${pendingApproval.id}">✕ Reject</button>
          ` : ''}
        </div>
      </div>

      <!-- Navigation Tabs for Workbench -->
      <div class="tabs" id="decision-tabs">
        <button class="tab-item active" data-tab="overview">Overview & Rationale</button>
        <button class="tab-item" data-tab="alternatives">Alternatives (${alternatives.length})</button>
        <button class="tab-item" data-tab="comparison">Side-by-Side Comparison</button>
        <button class="tab-item" data-tab="discussions">Discussions & Notes (${comments.length + threads.length})</button>
        <button class="tab-item" data-tab="approvals">Approval Workflow (${decisionApprovals.length})</button>
        <button class="tab-item" data-tab="history">Version Timeline (${versions.length + timeline.length})</button>
      </div>

      <!-- TAB 1: Overview & Rationale -->
      <div class="tab-content" id="tab-overview">
        <div class="decision-workbench">
          <div style="display: flex; flex-direction: column; gap: 20px;">
            <div class="panel">
              <h3 class="panel-title">Problem Statement & Background</h3>
              <div style="margin-top: 12px; font-size: 14.5px; line-height: 1.6; color: var(--text-primary); white-space: pre-line;">
                ${escapeHtml(decision.problem_statement)}
              </div>
            </div>

            <div class="panel">
              <div class="panel-header">
                <h3 class="panel-title">Decision Rationale & Trade-off Record</h3>
                ${canModify && !isArchived ? `
                  <button class="btn btn-sm btn-outline" id="btn-update-rationale">Update Rationale</button>
                ` : ''}
              </div>
              <div style="font-size: 14.5px; line-height: 1.6; color: var(--text-primary); white-space: pre-line;">
                ${decision.rationale ? escapeHtml(decision.rationale) : '<span style="color: var(--text-muted); font-style: italic;">No final rationale documented yet. Update once alternatives have been evaluated.</span>'}
              </div>
            </div>
          </div>

          <!-- Right Sidebar Meta -->
          <div style="display: flex; flex-direction: column; gap: 20px;">
            <div class="panel">
              <h3 class="panel-title" style="font-size: 15px; margin-bottom: 12px;">Decision Metadata</h3>
              <div style="display: flex; flex-direction: column; gap: 10px; font-size: 13.5px;">
                <div>
                  <span style="color: var(--text-muted);">Status:</span>
                  <span style="float: right;">${statusBadge(decision.status)}</span>
                </div>
                <div>
                  <span style="color: var(--text-muted);">Category:</span>
                  <span style="float: right; font-weight: 600;">${escapeHtml(decision.category)}</span>
                </div>
                <div>
                  <span style="color: var(--text-muted);">Author:</span>
                  <span style="float: right;">User #${decision.created_by}</span>
                </div>
                <div>
                  <span style="color: var(--text-muted);">Created:</span>
                  <span style="float: right;">${formatDate(decision.created_at)}</span>
                </div>
                <div>
                  <span style="color: var(--text-muted);">Last Updated:</span>
                  <span style="float: right;">${formatDate(decision.updated_at || decision.created_at)}</span>
                </div>
              </div>

              <!-- Tags Section -->
              <div style="margin-top: 18px; padding-top: 14px; border-top: 1px solid var(--border-subtle);">
                <span style="font-size: 12px; font-weight: 600; text-transform: uppercase; color: var(--text-muted);">Tags</span>
                <div style="display: flex; flex-wrap: wrap; gap: 6px; margin-top: 8px;">
                  ${tags.length ? tags.map(t => `<span class="badge badge-category">${escapeHtml(t.name)}</span>`).join('') : '<span style="font-size: 12px; color: var(--text-muted);">No tags assigned</span>'}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- TAB 2: Alternatives -->
      <div class="tab-content" id="tab-alternatives" style="display: none;">
        <div class="panel">
          <div class="panel-header">
            <div>
              <h2 class="panel-title">Evaluated Alternatives</h2>
              <p class="panel-subtitle">Architectural options considered, pros/cons, feasibility scores, and estimated costs</p>
            </div>
            ${canModify && !isArchived ? `
              <button class="btn btn-primary" id="btn-add-alternative">+ Add Alternative</button>
            ` : ''}
          </div>

          ${alternatives.length ? `
            <div class="comparison-grid">
              ${alternatives.map(alt => `
                <div class="alternative-card">
                  <div class="alternative-header">
                    <div>
                      <div class="alternative-name">${escapeHtml(alt.name)}</div>
                      <div style="font-size: 12px; color: var(--text-secondary); margin-top: 2px;">${escapeHtml(alt.description)}</div>
                    </div>
                    ${riskBadge(alt.risk_level)}
                  </div>

                  <div class="alternative-metric-row">
                    <div>
                      <div class="alternative-metric-label">Cost</div>
                      <div class="alternative-metric-val">$${Number(alt.estimated_cost).toLocaleString()}</div>
                    </div>
                    <div>
                      <div class="alternative-metric-label">Feasibility</div>
                      <div class="alternative-metric-val">${alt.feasibility_score} / 5</div>
                    </div>
                    <div>
                      <div class="alternative-metric-label">Risk</div>
                      <div class="alternative-metric-val">${escapeHtml(alt.risk_level)}</div>
                    </div>
                  </div>

                  <div class="pro-con-list">
                    <div class="pro-item">
                      <span>✓</span>
                      <div><strong>Pros:</strong> ${escapeHtml(alt.pros || 'None listed')}</div>
                    </div>
                    <div class="con-item">
                      <span>✕</span>
                      <div><strong>Cons:</strong> ${escapeHtml(alt.cons || 'None listed')}</div>
                    </div>
                  </div>

                  ${canModify && !isArchived ? `
                    <div style="display: flex; justify-content: flex-end; gap: 8px; margin-top: auto; padding-top: 10px; border-top: 1px solid var(--border-subtle);">
                      <button class="btn btn-sm btn-outline btn-edit-alt" data-id="${alt.id}">Edit</button>
                      <button class="btn btn-sm btn-danger btn-delete-alt" data-id="${alt.id}">Delete</button>
                    </div>
                  ` : ''}
                </div>
              `).join('')}
            </div>
          ` : `
            <div class="state-container">
              <div class="state-icon">⚖️</div>
              <div class="state-title">No alternatives added yet</div>
              <p class="state-desc">Capture competing options, technologies, or approaches to build an evidence-based comparison.</p>
              ${canModify && !isArchived ? `
                <button class="btn btn-primary" id="btn-add-alt-empty" style="margin-top: 12px;">+ Add First Alternative</button>
              ` : ''}
            </div>
          `}
        </div>
      </div>

      <!-- TAB 3: Side-by-Side Comparison -->
      <div class="tab-content" id="tab-comparison" style="display: none;">
        <div class="panel">
          <div class="panel-header">
            <div>
              <h2 class="panel-title">Side-by-Side Comparison Matrix</h2>
              <p class="panel-subtitle">Evaluate trade-offs, feasibility scores, and cost impacts across all submitted options</p>
            </div>
          </div>

          ${alternatives.length > 1 ? `
            <div class="table-container">
              <table class="data-table">
                <thead>
                  <tr>
                    <th style="width: 200px;">Comparison Dimension</th>
                    ${alternatives.map(a => `<th style="text-align: center; font-size: 14px;">${escapeHtml(a.name)}</th>`).join('')}
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td><strong>Estimated Cost</strong></td>
                    ${alternatives.map(a => `<td style="text-align: center; font-weight: 700;">$${Number(a.estimated_cost).toLocaleString()}</td>`).join('')}
                  </tr>
                  <tr>
                    <td><strong>Feasibility Score (1-5)</strong></td>
                    ${alternatives.map(a => `<td style="text-align: center; font-weight: 700; color: var(--teal-300);">${a.feasibility_score} / 5</td>`).join('')}
                  </tr>
                  <tr>
                    <td><strong>Risk Assessment</strong></td>
                    ${alternatives.map(a => `<td style="text-align: center;">${riskBadge(a.risk_level)}</td>`).join('')}
                  </tr>
                  <tr>
                    <td><strong>Key Advantages (Pros)</strong></td>
                    ${alternatives.map(a => `<td style="vertical-align: top; font-size: 13px; line-height: 1.5; color: #4ade80;">${escapeHtml(a.pros)}</td>`).join('')}
                  </tr>
                  <tr>
                    <td><strong>Trade-offs & Risks (Cons)</strong></td>
                    ${alternatives.map(a => `<td style="vertical-align: top; font-size: 13px; line-height: 1.5; color: #f87171;">${escapeHtml(a.cons)}</td>`).join('')}
                  </tr>
                </tbody>
              </table>
            </div>
          ` : alternatives.length === 1 ? `
            <div class="state-container">
              <div class="state-title">Comparison requires at least 2 alternatives</div>
              <p class="state-desc">You currently have 1 alternative. Add another option to view side-by-side trade-offs.</p>
              ${canModify && !isArchived ? `
                <button class="btn btn-primary" id="btn-add-second-alt" style="margin-top: 10px;">+ Add Alternative</button>
              ` : ''}
            </div>
          ` : `
            <div class="state-container">
              <div class="state-desc">No alternatives added yet for comparison.</div>
            </div>
          `}
        </div>
      </div>

      <!-- TAB 4: Discussions & Meeting Notes -->
      <div class="tab-content" id="tab-discussions" style="display: none;">
        <div style="display: grid; grid-template-columns: 1.5fr 1fr; gap: 24px;">
          <!-- Comments & Discussion Threads -->
          <div class="panel">
            <div class="panel-header">
              <h3 class="panel-title">Decision Comments & Discussions</h3>
            </div>

            <!-- Post New Comment -->
            <form id="form-post-comment" style="margin-bottom: 24px;">
              <div class="form-group">
                <textarea id="comment-content" class="form-textarea" placeholder="Share your perspective, question an assumption, or provide evidence..." required rows="3"></textarea>
              </div>
              <div style="display: flex; justify-content: flex-end;">
                <button type="submit" class="btn btn-primary btn-sm">Post Comment</button>
              </div>
            </form>

            <!-- Comments Stream -->
            ${comments.length ? `
              <div style="display: flex; flex-direction: column; gap: 14px;">
                ${comments.map(c => `
                  <div style="background: var(--bg-surface-elevated); border: 1px solid var(--border-subtle); border-radius: var(--radius-sm); padding: 14px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                      <strong>User #${c.user_id}</strong>
                      <small style="color: var(--text-muted);">${formatDate(c.created_at)}</small>
                    </div>
                    <div style="font-size: 13.5px; color: var(--text-primary);">${escapeHtml(c.content)}</div>
                  </div>
                `).join('')}
              </div>
            ` : `
              <div class="state-container" style="padding: 16px;">
                <div class="state-desc">No comments posted yet. Start the conversation!</div>
              </div>
            `}
          </div>

          <!-- Meeting Notes -->
          <div class="panel">
            <div class="panel-header">
              <div>
                <h3 class="panel-title">Meeting Notes</h3>
                <p class="panel-subtitle">Review meetings & stakeholder syncs</p>
              </div>
              <button class="btn btn-sm btn-outline" id="btn-add-meeting-note">+ Note</button>
            </div>

            ${meetingNotes.length ? `
              <div style="display: flex; flex-direction: column; gap: 12px;">
                ${meetingNotes.map(n => `
                  <div class="thread-card">
                    <div class="thread-title">${escapeHtml(n.title)}</div>
                    <div style="font-size: 12px; color: var(--text-muted); margin-bottom: 8px;">Date: ${formatDate(n.meeting_date || n.created_at)}</div>
                    <div style="font-size: 13px; color: var(--text-secondary); line-height: 1.5;">${escapeHtml(n.content || '')}</div>
                  </div>
                `).join('')}
              </div>
            ` : `
              <div class="state-container" style="padding: 16px;">
                <div class="state-desc">No meeting notes linked to this decision.</div>
              </div>
            `}
          </div>
        </div>
      </div>

      <!-- TAB 5: Approval Workflow -->
      <div class="tab-content" id="tab-approvals" style="display: none;">
        <div class="panel">
          <div class="panel-header">
            <div>
              <h2 class="panel-title">Approval Governance Pipeline</h2>
              <p class="panel-subtitle">Current status, reviewer delegations, and signed decisions</p>
            </div>
            ${canManage && isUnderReview ? `
              <button class="btn btn-primary" id="btn-assign-approval-alt">+ Assign Reviewer</button>
            ` : ''}
          </div>

          <!-- Status Flow Indicator -->
          <div style="display: flex; align-items: center; justify-content: space-around; padding: 24px; background: var(--bg-surface-elevated); border-radius: 8px; margin-bottom: 24px;">
            <div style="text-align: center;">
              <div style="font-size: 20px;">📝</div>
              <div style="font-weight: 700; margin-top: 6px;">Draft</div>
              <div style="font-size: 12px; color: var(--text-muted);">Authoring proposal</div>
            </div>
            <div style="font-size: 20px; color: var(--text-muted);">➔</div>
            <div style="text-align: center;">
              <div style="font-size: 20px;">🛡️</div>
              <div style="font-weight: 700; margin-top: 6px;">Under Review</div>
              <div style="font-size: 12px; color: var(--text-muted);">Evaluation & debate</div>
            </div>
            <div style="font-size: 20px; color: var(--text-muted);">➔</div>
            <div style="text-align: center;">
              <div style="font-size: 20px;">🏁</div>
              <div style="font-weight: 700; margin-top: 6px;">Outcome</div>
              <div style="font-size: 12px; color: var(--text-muted);">${decision.status === 'Approved' ? '✓ Approved' : decision.status === 'Rejected' ? '✕ Rejected' : 'Pending'}</div>
            </div>
          </div>

          ${decisionApprovals.length ? `
            <div class="table-container">
              <table class="data-table">
                <thead>
                  <tr>
                    <th>Approval #</th>
                    <th>Assigned Reviewer</th>
                    <th>Status</th>
                    <th>Assigned Date</th>
                    <th>Completed Date</th>
                    <th>Comments / Rationale</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  ${decisionApprovals.map(app => {
                    const isAssignee = app.reviewer_id === user?.id;
                    const canAct = app.status === 'Pending' && (isAssignee || canManage);
                    return `
                      <tr>
                        <td>Approval #${app.id}</td>
                        <td><strong>Reviewer #${app.reviewer_id}</strong></td>
                        <td>${statusBadge(app.status)}</td>
                        <td>${formatDate(app.created_at)}</td>
                        <td>${formatDate(app.completed_at)}</td>
                        <td>${escapeHtml(app.comments || '—')}</td>
                        <td>
                          ${canAct ? `
                            <div style="display: flex; gap: 6px;">
                              <button class="btn btn-sm btn-success btn-app-approve" data-id="${app.id}">Approve</button>
                              <button class="btn btn-sm btn-danger btn-app-reject" data-id="${app.id}">Reject</button>
                            </div>
                          ` : '—'}
                        </td>
                      </tr>
                    `;
                  }).join('')}
                </tbody>
              </table>
            </div>
          ` : `
            <div class="state-container">
              <div class="state-icon">⏳</div>
              <div class="state-title">No reviewer assigned yet</div>
              <p class="state-desc">Once the proposal is submitted for review, managers can assign an authorized reviewer.</p>
            </div>
          `}
        </div>
      </div>

      <!-- TAB 6: Version History & Timeline -->
      <div class="tab-content" id="tab-history" style="display: none;">
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 24px;">
          <!-- Versions -->
          <div class="panel">
            <div class="panel-header">
              <h3 class="panel-title">Decision Version Snapshots</h3>
            </div>
            ${versions.length ? `
              <div class="timeline-list">
                ${versions.map(v => `
                  <div class="timeline-node">
                    <div class="timeline-header">
                      <span class="timeline-action">Version ${v.version_number}</span>
                      <span class="timeline-time">${formatDate(v.created_at)}</span>
                    </div>
                    <div class="timeline-desc">
                      <strong>Title:</strong> ${escapeHtml(v.title)}<br>
                      <strong>Status:</strong> ${statusBadge(v.status)}<br>
                      <strong>Category:</strong> ${escapeHtml(v.category)}
                    </div>
                  </div>
                `).join('')}
              </div>
            ` : `
              <div class="state-container" style="padding: 24px;">
                <div class="state-desc">No version snapshots recorded.</div>
              </div>
            `}
          </div>

          <!-- Timeline Events -->
          <div class="panel">
            <div class="panel-header">
              <h3 class="panel-title">Activity Timeline</h3>
            </div>
            ${timeline.length ? `
              <div class="timeline-list">
                ${timeline.map(e => `
                  <div class="timeline-node">
                    <div class="timeline-header">
                      <span class="timeline-action">${escapeHtml(e.event_type || e.action || 'Activity')}</span>
                      <span class="timeline-time">${formatDate(e.timestamp || e.created_at)}</span>
                    </div>
                    ${e.description ? `<div class="timeline-desc">${escapeHtml(e.description)}</div>` : ''}
                  </div>
                `).join('')}
              </div>
            ` : `
              <div class="state-container" style="padding: 24px;">
                <div class="state-desc">No activity timeline recorded.</div>
              </div>
            `}
          </div>
        </div>
      </div>
    `;
  } catch (err) {
    return errorState(err.message);
  }
}

export function bindDecisionDetailEvents(decisionId) {
  // Tab Switching
  const tabs = document.querySelectorAll('#decision-tabs .tab-item');
  const contents = document.querySelectorAll('.tab-content');

  tabs.forEach(tab => {
    tab.onclick = () => {
      tabs.forEach(t => t.classList.remove('active'));
      contents.forEach(c => c.style.display = 'none');
      tab.classList.add('active');
      const target = document.getElementById(`tab-${tab.dataset.tab}`);
      if (target) target.style.display = 'block';
    };
  });

  // Submit for Review
  const submitWorkflowBtn = document.getElementById('btn-submit-workflow');
  if (submitWorkflowBtn) {
    submitWorkflowBtn.onclick = () => {
      showModal({
        title: 'Submit Decision for Review',
        content: '<p>Submit this proposal for formal evaluation? Its status will transition to <strong>Under Review</strong>.</p>',
        confirmText: 'Submit for Review',
        confirmClass: 'btn-success',
        onConfirm: async () => {
          await decisionsApi.updateStatus(decisionId, 'Under Review');
          showToast('Decision submitted for review!', 'success');
          window.location.reload();
        },
      });
    };
  }

  // Update Rationale
  const updateRationaleBtn = document.getElementById('btn-update-rationale');
  if (updateRationaleBtn) {
    updateRationaleBtn.onclick = () => {
      showModal({
        title: 'Update Decision Rationale',
        content: `
          <div class="form-group">
            <label>Detailed Rationale & Evidence</label>
            <textarea id="modal-rationale-input" class="form-textarea" rows="5" placeholder="Explain why the chosen alternative is preferred over other options..."></textarea>
          </div>
        `,
        confirmText: 'Save Rationale',
        onConfirm: async () => {
          const rationale = document.getElementById('modal-rationale-input').value.trim();
          if (rationale) {
            await decisionsApi.updateRationale(decisionId, rationale);
            showToast('Rationale updated successfully.', 'success');
            window.location.reload();
          }
        },
      });
    };
  }

  // Add Alternative Handler
  const handleAddAlternative = () => {
    showModal({
      title: 'Add New Alternative',
      content: `
        <form id="form-modal-add-alt">
          <div class="form-group">
            <label>Alternative Name *</label>
            <input type="text" name="name" class="form-control" placeholder="e.g. Option B: Hybrid Cloud Architecture" required>
          </div>
          <div class="form-group">
            <label>Description</label>
            <textarea name="description" class="form-textarea" placeholder="Architectural approach, implementation scope..." required rows="2"></textarea>
          </div>
          <div class="form-grid-2">
            <div class="form-group">
              <label>Estimated Cost ($) *</label>
              <input type="number" name="estimated_cost" class="form-control" placeholder="45000" min="0" required>
            </div>
            <div class="form-group">
              <label>Feasibility Score (1-5) *</label>
              <input type="number" name="feasibility_score" class="form-control" placeholder="4" min="1" max="5" required>
            </div>
          </div>
          <div class="form-group">
            <label>Risk Level *</label>
            <select name="risk_level" class="form-select" required>
              <option value="Low">Low</option>
              <option value="Medium">Medium</option>
              <option value="High">High</option>
              <option value="Critical">Critical</option>
            </select>
          </div>
          <div class="form-grid-2">
            <div class="form-group">
              <label>Pros (Advantages) *</label>
              <textarea name="pros" class="form-textarea" placeholder="Lower operational latency, active redundancy..." required rows="2"></textarea>
            </div>
            <div class="form-group">
              <label>Cons (Trade-offs) *</label>
              <textarea name="cons" class="form-textarea" placeholder="Higher initial migration effort..." required rows="2"></textarea>
            </div>
          </div>
        </form>
      `,
      confirmText: 'Add Alternative',
      onConfirm: async () => {
        const form = document.getElementById('form-modal-add-alt');
        const fd = new FormData(form);
        const name = fd.get('name')?.trim();
        const description = fd.get('description')?.trim();
        const estimated_cost = parseFloat(fd.get('estimated_cost'));
        const feasibility_score = parseInt(fd.get('feasibility_score'), 10);
        const risk_level = fd.get('risk_level');
        const pros = fd.get('pros')?.trim();
        const cons = fd.get('cons')?.trim();

        if (!name || !description || isNaN(estimated_cost) || isNaN(feasibility_score) || !pros || !cons) {
          throw new Error('Please fill in all required alternative fields.');
        }

        if (feasibility_score < 1 || feasibility_score > 5) {
          throw new Error('Feasibility score must be between 1 and 5.');
        }

        await alternativesApi.createForDecision(decisionId, {
          name,
          description,
          estimated_cost,
          feasibility_score,
          risk_level,
          pros,
          cons,
        });

        showToast('Alternative added successfully!', 'success');
        window.location.reload();
      },
    });
  };

  const addAltBtn = document.getElementById('btn-add-alternative');
  if (addAltBtn) addAltBtn.onclick = handleAddAlternative;
  const addAltEmptyBtn = document.getElementById('btn-add-alt-empty');
  if (addAltEmptyBtn) addAltEmptyBtn.onclick = handleAddAlternative;
  const addAltSecondBtn = document.getElementById('btn-add-second-alt');
  if (addAltSecondBtn) addAltSecondBtn.onclick = handleAddAlternative;

  // Delete Alternative
  document.querySelectorAll('.btn-delete-alt').forEach(btn => {
    btn.onclick = (e) => {
      e.stopPropagation();
      const altId = btn.dataset.id;
      showModal({
        title: 'Delete Alternative',
        content: '<p>Are you sure you want to delete this alternative option? This cannot be undone.</p>',
        confirmText: 'Delete',
        confirmClass: 'btn-danger',
        onConfirm: async () => {
          await alternativesApi.delete(altId);
          showToast('Alternative deleted.', 'info');
          window.location.reload();
        },
      });
    };
  });

  // Edit Alternative
  document.querySelectorAll('.btn-edit-alt').forEach(btn => {
    btn.onclick = async (e) => {
      e.stopPropagation();
      const altId = btn.dataset.id;
      try {
        const alt = await alternativesApi.get(altId);
        showModal({
          title: `Edit Alternative: ${escapeHtml(alt.name)}`,
          content: `
            <form id="form-edit-alt">
              <div class="form-group">
                <label>Name</label>
                <input type="text" name="name" class="form-control" value="${escapeHtml(alt.name)}" required>
              </div>
              <div class="form-group">
                <label>Description</label>
                <textarea name="description" class="form-textarea" required rows="2">${escapeHtml(alt.description)}</textarea>
              </div>
              <div class="form-grid-2">
                <div class="form-group">
                  <label>Cost</label>
                  <input type="number" name="estimated_cost" class="form-control" value="${alt.estimated_cost}" required>
                </div>
                <div class="form-group">
                  <label>Feasibility Score (1-5)</label>
                  <input type="number" name="feasibility_score" class="form-control" value="${alt.feasibility_score}" min="1" max="5" required>
                </div>
              </div>
              <div class="form-group">
                <label>Risk Level</label>
                <select name="risk_level" class="form-select" required>
                  ${['Low', 'Medium', 'High', 'Critical'].map(r => `<option value="${r}" ${r === alt.risk_level ? 'selected' : ''}>${r}</option>`).join('')}
                </select>
              </div>
              <div class="form-grid-2">
                <div class="form-group">
                  <label>Pros</label>
                  <textarea name="pros" class="form-textarea" required rows="2">${escapeHtml(alt.pros)}</textarea>
                </div>
                <div class="form-group">
                  <label>Cons</label>
                  <textarea name="cons" class="form-textarea" required rows="2">${escapeHtml(alt.cons)}</textarea>
                </div>
              </div>
            </form>
          `,
          confirmText: 'Update Alternative',
          onConfirm: async () => {
            const form = document.getElementById('form-edit-alt');
            const fd = new FormData(form);
            await alternativesApi.update(altId, {
              name: fd.get('name'),
              description: fd.get('description'),
              estimated_cost: parseFloat(fd.get('estimated_cost')),
              feasibility_score: parseInt(fd.get('feasibility_score'), 10),
              risk_level: fd.get('risk_level'),
              pros: fd.get('pros'),
              cons: fd.get('cons'),
            });
            showToast('Alternative updated.', 'success');
            window.location.reload();
          },
        });
      } catch (err) {
        showToast(err.message, 'error');
      }
    };
  });

  // Assign Reviewer
  const assignBtn = document.getElementById('btn-assign-reviewer');
  const assignAltBtn = document.getElementById('btn-assign-approval-alt');
  const handleAssign = async () => {
    try {
      const users = await authApi.listUsers();
      showModal({
        title: 'Assign Reviewer for Approval',
        content: `
          <div class="form-group">
            <label>Select Workspace Reviewer</label>
            <select id="modal-reviewer-select" class="form-select">
              ${users.map(u => `<option value="${u.id}">${escapeHtml(u.full_name)} (${escapeHtml(u.role)} - ${escapeHtml(u.department || 'N/A')})</option>`).join('')}
            </select>
            <span class="form-hint">The assigned reviewer will evaluate the decision and cast the final approval/rejection.</span>
          </div>
        `,
        confirmText: 'Assign Reviewer',
        onConfirm: async () => {
          const reviewerId = parseInt(document.getElementById('modal-reviewer-select').value, 10);
          await approvalsApi.assign(decisionId, reviewerId);
          showToast('Reviewer assigned successfully!', 'success');
          window.location.reload();
        },
      });
    } catch (err) {
      showToast(err.message, 'error');
    }
  };

  if (assignBtn) assignBtn.onclick = handleAssign;
  if (assignAltBtn) assignAltBtn.onclick = handleAssign;

  // Approve / Reject Actions
  const handleApprovalAction = (approvalId, status) => {
    showModal({
      title: `${status} Decision`,
      content: `
        <div class="form-group">
          <label>${status} Comments / Rationale</label>
          <textarea id="modal-approval-comments" class="form-textarea" placeholder="Document the reason for ${status.toLowerCase()} this proposal..." rows="3"></textarea>
        </div>
      `,
      confirmText: status,
      confirmClass: status === 'Approved' ? 'btn-success' : 'btn-danger',
      onConfirm: async () => {
        const comments = document.getElementById('modal-approval-comments').value.trim();
        await approvalsApi.action(approvalId, status, comments);
        showToast(`Decision has been ${status.toLowerCase()}!`, 'success');
        window.location.reload();
      },
    });
  };

  const approveTopBtn = document.getElementById('btn-approve-action');
  if (approveTopBtn) {
    approveTopBtn.onclick = () => handleApprovalAction(approveTopBtn.dataset.approvalId, 'Approved');
  }
  const rejectTopBtn = document.getElementById('btn-reject-action');
  if (rejectTopBtn) {
    rejectTopBtn.onclick = () => handleApprovalAction(rejectTopBtn.dataset.approvalId, 'Rejected');
  }

  document.querySelectorAll('.btn-app-approve').forEach(b => {
    b.onclick = () => handleApprovalAction(b.dataset.id, 'Approved');
  });
  document.querySelectorAll('.btn-app-reject').forEach(b => {
    b.onclick = () => handleApprovalAction(b.dataset.id, 'Rejected');
  });

  // Post Comment
  const commentForm = document.getElementById('form-post-comment');
  if (commentForm) {
    commentForm.onsubmit = async (e) => {
      e.preventDefault();
      const content = document.getElementById('comment-content').value.trim();
      if (!content) return;
      try {
        await discussionsApi.addComment(decisionId, content);
        showToast('Comment posted.', 'success');
        window.location.reload();
      } catch (err) {
        showToast(err.message, 'error');
      }
    };
  }

  // Add Meeting Note
  const addMeetingNoteBtn = document.getElementById('btn-add-meeting-note');
  if (addMeetingNoteBtn) {
    addMeetingNoteBtn.onclick = () => {
      showModal({
        title: 'Add Meeting Note',
        content: `
          <form id="form-meeting-note">
            <div class="form-group">
              <label>Meeting Title *</label>
              <input type="text" name="title" class="form-control" placeholder="Architecture Sync" required>
            </div>
            <div class="form-group">
              <label>Meeting Date *</label>
              <input type="datetime-local" name="meeting_date" class="form-control" value="${new Date().toISOString().slice(0, 16)}" required>
            </div>
            <div class="form-group">
              <label>Meeting Notes & Conclusions *</label>
              <textarea name="content" class="form-textarea" rows="4" placeholder="Document discussion points, attendees, consensus reached..." required></textarea>
            </div>
          </form>
        `,
        confirmText: 'Save Note',
        onConfirm: async () => {
          const form = document.getElementById('form-meeting-note');
          const fd = new FormData(form);
          const meetingDateVal = fd.get('meeting_date') ? new Date(fd.get('meeting_date')).toISOString() : new Date().toISOString();
          await discussionsApi.createMeetingNote(decisionId, {
            title: fd.get('title'),
            content: fd.get('content'),
            meeting_date: meetingDateVal,
          });
          showToast('Meeting note added.', 'success');
          window.location.reload();
        },
      });
    };
  }
}
