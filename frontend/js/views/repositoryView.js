// Knowledge Repository & Search Portal View
import { decisionsApi, tagsApi } from '../api.js';
import { statusBadge, formatDate, escapeHtml, errorState, renderPagination } from '../components/ui.js';

export async function renderRepositoryView(state = {}) {
  const categories = [
    'Technology', 'Finance', 'Operations', 'Human Resources',
    'Security', 'Product', 'Infrastructure', 'Strategy',
  ];
  const statuses = ['Draft', 'Under Review', 'Approved', 'Rejected', 'Archived'];

  const urlParams = new URLSearchParams(window.location.hash.split('?')[1] || '');
  const filterSearch = urlParams.get('q') || state.q || '';
  const filterCategory = urlParams.get('category') || state.category || '';
  const filterStatus = urlParams.get('status') || state.status || '';
  const filterTag = urlParams.get('tag') || state.tag || '';
  const page = parseInt(urlParams.get('page') || state.page || '1', 10);
  const pageSize = 12;

  let results = [];
  let total = 0;
  let availableTags = [];

  try {
    const [searchRes, tagsRes] = await Promise.all([
      filterSearch
        ? decisionsApi.search(filterSearch, { category: filterCategory, status: filterStatus, tag: filterTag, page, page_size: pageSize })
        : decisionsApi.list({ category: filterCategory, status: filterStatus, tag: filterTag, page, page_size: pageSize }),
      tagsApi.list().catch(() => []),
    ]);

    availableTags = tagsRes || [];

    if (Array.isArray(searchRes)) {
      results = searchRes;
      total = searchRes.length;
    } else if (searchRes && (searchRes.results || searchRes.items)) {
      results = searchRes.results || searchRes.items;
      total = searchRes.total || results.length;
    }
  } catch (err) {
    return errorState(err.message);
  }

  return `
    <div class="page-header">
      <div class="page-header-text">
        <h1>Organizational Knowledge Repository</h1>
        <p>Explore past architectural decisions, strategic rationales, and institutional memory.</p>
      </div>
    </div>

    <!-- Search Hero & Filter Bar -->
    <div class="panel" style="margin-bottom: 28px; background: linear-gradient(135deg, var(--bg-surface) 0%, var(--bg-surface-elevated) 100%);">
      <div style="display: flex; gap: 12px; margin-bottom: 16px; flex-wrap: wrap;">
        <div style="flex: 1; min-width: 280px; position: relative;">
          <input type="text" id="repo-search-input" class="form-control" style="padding: 12px 16px; font-size: 15px;" placeholder="Search decisions by keyword, problem statement, or rationale..." value="${escapeHtml(filterSearch)}">
        </div>
        <button id="btn-repo-search" class="btn btn-primary" style="padding: 12px 24px;">Search Repository</button>
      </div>

      <!-- Filters Row -->
      <div style="display: flex; gap: 10px; flex-wrap: wrap; align-items: center;">
        <select id="repo-filter-category" class="form-select" style="width: auto; min-width: 160px;">
          <option value="">All Categories</option>
          ${categories.map(c => `<option value="${c}" ${filterCategory === c ? 'selected' : ''}>${c}</option>`).join('')}
        </select>

        <select id="repo-filter-status" class="form-select" style="width: auto; min-width: 150px;">
          <option value="">All Statuses</option>
          ${statuses.map(s => `<option value="${s}" ${filterStatus === s ? 'selected' : ''}>${s}</option>`).join('')}
        </select>

        <select id="repo-filter-tag" class="form-select" style="width: auto; min-width: 140px;">
          <option value="">All Tags</option>
          ${availableTags.map(t => `<option value="${t.name}" ${filterTag === t.name ? 'selected' : ''}>${escapeHtml(t.name)}</option>`).join('')}
        </select>

        <button id="btn-repo-reset" class="btn btn-outline">Clear Filters</button>
      </div>
    </div>

    <!-- Search Results Grid -->
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
      <h2 class="panel-title">Found ${total} decisions</h2>
      <span style="font-size: 13px; color: var(--text-muted);">Page ${page}</span>
    </div>

    ${results.length ? `
      <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr)); gap: 18px;">
        ${results.map(d => `
          <div class="panel" style="display: flex; flex-direction: column; justify-content: space-between; transition: border-color var(--transition-fast); border-left: 3px solid var(--teal-400);">
            <div>
              <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 8px; margin-bottom: 10px;">
                <span class="badge badge-category">${escapeHtml(d.category)}</span>
                ${statusBadge(d.status)}
              </div>

              <h3 style="font-family: var(--font-display); font-size: 17px; font-weight: 700; margin-bottom: 8px; line-height: 1.3;">
                <a href="#decisions/${d.id}" style="color: var(--text-primary); text-decoration: none;">${escapeHtml(d.title)}</a>
              </h3>

              <p style="font-size: 13px; color: var(--text-secondary); line-height: 1.5; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; margin-bottom: 12px;">
                ${escapeHtml(d.problem_statement || 'No description available.')}
              </p>

              ${d.rationale ? `
                <div style="background: var(--bg-surface-elevated); padding: 8px 12px; border-radius: 6px; font-size: 12px; color: var(--teal-300); margin-bottom: 12px;">
                  <strong>Rationale:</strong> ${escapeHtml(d.rationale.substring(0, 100))}${d.rationale.length > 100 ? '...' : ''}
                </div>
              ` : ''}
            </div>

            <div style="display: flex; justify-content: space-between; align-items: center; padding-top: 12px; border-top: 1px solid var(--border-subtle); margin-top: 8px; font-size: 12px; color: var(--text-muted);">
              <span>User #${d.created_by} • ${formatDate(d.created_at)}</span>
              <a href="#decisions/${d.id}" class="btn btn-sm btn-outline">Read Full Replay →</a>
            </div>
          </div>
        `).join('')}
      </div>

      ${renderPagination({ page, pageSize, total })}
    ` : `
      <div class="panel">
        <div class="state-container">
          <div class="state-icon">🔍</div>
          <div class="state-title">No matching decisions found</div>
          <p class="state-desc">Try modifying your query or selecting different categories/statuses.</p>
        </div>
      </div>
    `}
  `;
}

export function bindRepositoryEvents() {
  const searchInput = document.getElementById('repo-search-input');
  const searchBtn = document.getElementById('btn-repo-search');
  const categorySelect = document.getElementById('repo-filter-category');
  const statusSelect = document.getElementById('repo-filter-status');
  const tagSelect = document.getElementById('repo-filter-tag');
  const resetBtn = document.getElementById('btn-repo-reset');

  const executeSearch = (page = 1) => {
    const params = new URLSearchParams();
    if (searchInput?.value.trim()) params.set('q', searchInput.value.trim());
    if (categorySelect?.value) params.set('category', categorySelect.value);
    if (statusSelect?.value) params.set('status', statusSelect.value);
    if (tagSelect?.value) params.set('tag', tagSelect.value);
    if (page > 1) params.set('page', page);

    const q = params.toString();
    window.location.hash = `#repository${q ? `?${q}` : ''}`;
  };

  if (searchBtn) searchBtn.onclick = () => executeSearch(1);
  if (searchInput) {
    searchInput.onkeydown = (e) => {
      if (e.key === 'Enter') executeSearch(1);
    };
  }

  if (categorySelect) categorySelect.onchange = () => executeSearch(1);
  if (statusSelect) statusSelect.onchange = () => executeSearch(1);
  if (tagSelect) tagSelect.onchange = () => executeSearch(1);

  if (resetBtn) {
    resetBtn.onclick = () => {
      window.location.hash = '#repository';
    };
  }

  // Pagination clicks
  const prevBtn = document.querySelector('.prev-page-btn');
  const nextBtn = document.querySelector('.next-page-btn');
  const urlParams = new URLSearchParams(window.location.hash.split('?')[1] || '');
  const currentPage = parseInt(urlParams.get('page') || '1', 10);

  if (prevBtn) {
    prevBtn.onclick = () => executeSearch(Math.max(1, currentPage - 1));
  }
  if (nextBtn) {
    nextBtn.onclick = () => executeSearch(currentPage + 1);
  }
}
