// Decision Management: Decision List View
import { auth } from '../auth.js';
import { decisionsApi, tagsApi } from '../api.js';
import { statusBadge, formatDate, escapeHtml, showToast, showModal, errorState } from '../components/ui.js';

export async function renderDecisionListView(state = {}) {
  const categories = [
    'Technology', 'Finance', 'Operations', 'Human Resources',
    'Security', 'Product', 'Infrastructure', 'Strategy',
  ];
  const statuses = ['Draft', 'Under Review', 'Approved', 'Rejected', 'Archived'];

  // Current filter state from URL or passed in
  const urlParams = new URLSearchParams(window.location.hash.split('?')[1] || '');
  const filterStatus = urlParams.get('status') || state.status || '';
  const filterCategory = urlParams.get('category') || state.category || '';
  const filterTag = urlParams.get('tag') || state.tag || '';
  const filterSearch = urlParams.get('q') || state.q || '';
  const page = parseInt(urlParams.get('page') || state.page || '1', 10);

  let decisions = [];
  let total = 0;
  let availableTags = [];

  try {
    const [decisionsResult, tagsResult] = await Promise.all([
      filterSearch
        ? decisionsApi.search(filterSearch, { status: filterStatus, category: filterCategory, tag: filterTag, page, page_size: 20 })
        : decisionsApi.list({ status: filterStatus, category: filterCategory, tag: filterTag, page, page_size: 20 }),
      tagsApi.list().catch(() => []),
    ]);

    availableTags = tagsResult || [];

    if (Array.isArray(decisionsResult)) {
      decisions = decisionsResult;
      total = decisionsResult.length;
    } else if (decisionsResult && decisionsResult.items) {
      decisions = decisionsResult.items;
      total = decisionsResult.total || decisions.length;
    } else if (decisionsResult && decisionsResult.results) {
      decisions = decisionsResult.results;
      total = decisionsResult.total || decisions.length;
    }
  } catch (err) {
    return errorState(err.message);
  }

  const user = auth.currentUser;
  const isPrivileged = auth.canManageTeam();

  return `
    <div class="page-header">
      <div class="page-header-text">
        <h1>Decision Management</h1>
        <p>Review, track, and manage decisions moving through organizational evaluation.</p>
      </div>
      <div class="page-header-actions">
        <a href="#decisions/create" class="btn btn-primary">+ Create Decision</a>
      </div>
    </div>

    <!-- Filter & Search Toolbar -->
    <div class="panel" style="margin-bottom: 24px;">
      <div class="filter-toolbar">
        <div class="filter-input-wrap">
          <input type="text" id="filter-search-input" class="form-control" placeholder="Search decisions..." value="${escapeHtml(filterSearch)}">
        </div>

        <select id="filter-status-select" class="form-select filter-select">
          <option value="">All Statuses</option>
          ${statuses.map(s => `<option value="${s}" ${filterStatus === s ? 'selected' : ''}>${s}</option>`).join('')}
        </select>

        <select id="filter-category-select" class="form-select filter-select">
          <option value="">All Categories</option>
          ${categories.map(c => `<option value="${c}" ${filterCategory === c ? 'selected' : ''}>${c}</option>`).join('')}
        </select>

        <select id="filter-tag-select" class="form-select filter-select">
          <option value="">All Tags</option>
          ${availableTags.map(t => `<option value="${t.name}" ${filterTag === t.name ? 'selected' : ''}>${escapeHtml(t.name)}</option>`).join('')}
        </select>

        <button id="btn-apply-filters" class="btn btn-primary">Filter</button>
        <button id="btn-reset-filters" class="btn btn-outline">Reset</button>
      </div>

      <!-- Decision Data Table -->
      ${decisions.length ? `
        <div class="table-container">
          <table class="data-table">
            <thead>
              <tr>
                <th>Decision Title & Problem</th>
                <th>Category</th>
                <th>Status</th>
                <th>Created</th>
                <th>Last Updated</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              ${decisions.map(d => {
                const canModify = d.created_by === user?.id || isPrivileged;
                const isArchived = d.status === 'Archived';
                const isDraft = d.status === 'Draft';

                return `
                  <tr>
                    <td style="max-width: 340px;">
                      <strong>${escapeHtml(d.title)}</strong>
                      <p style="font-size: 12px; color: var(--text-secondary); margin-top: 3px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;">
                        ${escapeHtml(d.problem_statement || 'No description provided')}
                      </p>
                    </td>
                    <td>
                      <span class="badge badge-category">${escapeHtml(d.category)}</span>
                    </td>
                    <td>${statusBadge(d.status)}</td>
                    <td>${formatDate(d.created_at)}</td>
                    <td>${formatDate(d.updated_at || d.created_at)}</td>
                    <td>
                      <div style="display: flex; gap: 6px; align-items: center; flex-wrap: wrap;">
                        <a href="#decisions/${d.id}" class="btn btn-sm btn-outline">View</a>
                        
                        ${canModify && !isArchived ? `
                          <button class="btn btn-sm btn-outline btn-edit-decision" data-id="${d.id}">Edit</button>
                        ` : ''}

                        ${canModify && isDraft ? `
                          <button class="btn btn-sm btn-success btn-submit-decision" data-id="${d.id}" title="Submit for Review">Submit</button>
                        ` : ''}

                        ${canModify && !isArchived ? `
                          <button class="btn btn-sm btn-danger btn-delete-decision" data-id="${d.id}" title="Archive Decision">Archive</button>
                        ` : ''}
                      </div>
                    </td>
                  </tr>
                `;
              }).join('')}
            </tbody>
          </table>
        </div>
      ` : `
        <div class="state-container">
          <div class="state-icon">📄</div>
          <div class="state-title">No decisions found</div>
          <p class="state-desc">Try clearing your filters or create a new decision proposal.</p>
          <a href="#decisions/create" class="btn btn-primary" style="margin-top: 10px;">Create Decision</a>
        </div>
      `}
    </div>
  `;
}

export function bindDecisionListEvents() {
  const searchInput = document.getElementById('filter-search-input');
  const statusSelect = document.getElementById('filter-status-select');
  const categorySelect = document.getElementById('filter-category-select');
  const tagSelect = document.getElementById('filter-tag-select');
  const applyBtn = document.getElementById('btn-apply-filters');
  const resetBtn = document.getElementById('btn-reset-filters');

  const updateFilters = () => {
    const params = new URLSearchParams();
    if (searchInput?.value.trim()) params.set('q', searchInput.value.trim());
    if (statusSelect?.value) params.set('status', statusSelect.value);
    if (categorySelect?.value) params.set('category', categorySelect.value);
    if (tagSelect?.value) params.set('tag', tagSelect.value);
    
    const query = params.toString();
    window.location.hash = `#decisions${query ? `?${query}` : ''}`;
  };

  if (applyBtn) applyBtn.onclick = updateFilters;
  if (searchInput) {
    searchInput.onkeydown = (e) => {
      if (e.key === 'Enter') updateFilters();
    };
  }

  if (resetBtn) {
    resetBtn.onclick = () => {
      window.location.hash = '#decisions';
    };
  }

  // Submit for Review action
  document.querySelectorAll('.btn-submit-decision').forEach(btn => {
    btn.onclick = async (e) => {
      e.stopPropagation();
      const id = btn.dataset.id;
      showModal({
        title: 'Submit Decision for Review',
        content: '<p>Submitting this decision transitions its status to <strong>Under Review</strong>, allowing assigned reviewers and managers to evaluate alternatives and cast approvals. Continue?</p>',
        confirmText: 'Submit for Review',
        confirmClass: 'btn-success',
        onConfirm: async () => {
          await decisionsApi.updateStatus(id, 'Under Review');
          showToast('Decision submitted for review!', 'success');
          window.location.reload();
        },
      });
    };
  });

  // Archive / Delete action
  document.querySelectorAll('.btn-delete-decision').forEach(btn => {
    btn.onclick = async (e) => {
      e.stopPropagation();
      const id = btn.dataset.id;
      showModal({
        title: 'Archive Decision',
        content: '<p>Are you sure you want to archive this decision? It will be marked as archived and cannot be further modified.</p>',
        confirmText: 'Archive Decision',
        confirmClass: 'btn-danger',
        onConfirm: async () => {
          await decisionsApi.delete(id);
          showToast('Decision archived successfully.', 'info');
          window.location.reload();
        },
      });
    };
  });

  // Edit action
  document.querySelectorAll('.btn-edit-decision').forEach(btn => {
    btn.onclick = async (e) => {
      e.stopPropagation();
      const id = btn.dataset.id;
      try {
        const d = await decisionsApi.get(id);
        const categories = ['Technology', 'Finance', 'Operations', 'Human Resources', 'Security', 'Product', 'Infrastructure', 'Strategy'];
        
        showModal({
          title: `Edit Decision #${id}`,
          content: `
            <form id="edit-decision-modal-form">
              <div class="form-group">
                <label>Decision Title</label>
                <input type="text" name="title" class="form-control" value="${escapeHtml(d.title)}" required minlength="3">
              </div>
              <div class="form-group">
                <label>Category</label>
                <select name="category" class="form-select" required>
                  ${categories.map(c => `<option value="${c}" ${c === d.category ? 'selected' : ''}>${c}</option>`).join('')}
                </select>
              </div>
              <div class="form-group">
                <label>Problem Statement</label>
                <textarea name="problem_statement" class="form-textarea" required minlength="10">${escapeHtml(d.problem_statement)}</textarea>
              </div>
            </form>
          `,
          confirmText: 'Save Changes',
          onConfirm: async () => {
            const form = document.getElementById('edit-decision-modal-form');
            const data = Object.fromEntries(new FormData(form));
            await decisionsApi.update(id, data);
            showToast('Decision updated successfully.', 'success');
            window.location.reload();
          }
        });
      } catch (err) {
        showToast(err.message, 'error');
      }
    };
  });
}
