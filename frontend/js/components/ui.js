// UI Component Helpers & Renderers

export function escapeHtml(str = '') {
  if (str === null || str === undefined) return '';
  return String(str).replace(/[&<>'"]/g, tag => ({
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    "'": '&#39;',
    '"': '&quot;',
  }[tag] || tag));
}

export function formatDate(val) {
  if (!val) return '—';
  try {
    const d = new Date(val);
    if (isNaN(d.getTime())) return String(val);
    return d.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  } catch {
    return String(val);
  }
}

export function statusBadge(status = 'Draft') {
  const s = String(status || 'Draft');
  const slug = s.toLowerCase().replace(/\s+/g, '-');
  return `<span class="badge badge-${slug}">${escapeHtml(s)}</span>`;
}

export function riskBadge(risk = 'Low') {
  const r = String(risk || 'Low');
  const slug = r.toLowerCase();
  return `<span class="badge badge-risk-${slug}">Risk: ${escapeHtml(r)}</span>`;
}

export function statCard({ label, value, meta, accent = false }) {
  return `
    <div class="stat-card ${accent ? 'stat-card-accent' : ''}">
      <div class="stat-card-label">${escapeHtml(label)}</div>
      <div class="stat-card-value">${value !== undefined && value !== null ? escapeHtml(value) : '0'}</div>
      ${meta ? `<div class="stat-card-meta">${escapeHtml(meta)}</div>` : ''}
    </div>
  `;
}

export function loadingState(msg = 'Loading workspace data...') {
  return `
    <div class="state-container">
      <div class="spinner"></div>
      <div class="state-title">${escapeHtml(msg)}</div>
    </div>
  `;
}

export function emptyState(title = 'No items found', desc = '', actionHtml = '') {
  return `
    <div class="state-container">
      <div class="state-icon">📂</div>
      <div class="state-title">${escapeHtml(title)}</div>
      ${desc ? `<p class="state-desc">${escapeHtml(desc)}</p>` : ''}
      ${actionHtml ? `<div style="margin-top: 14px;">${actionHtml}</div>` : ''}
    </div>
  `;
}

export function errorState(msg = 'Unable to complete request.', retryBtnText = 'Try Again') {
  return `
    <div class="state-container">
      <div class="state-icon" style="color: var(--status-rejected-text);">⚠️</div>
      <div class="state-title">Something went wrong</div>
      <p class="state-desc" style="color: var(--status-rejected-text);">${escapeHtml(msg)}</p>
      ${retryBtnText ? `<button class="btn btn-outline" style="margin-top: 12px;" onclick="window.location.reload()">${escapeHtml(retryBtnText)}</button>` : ''}
    </div>
  `;
}

// Global Toast System
export function showToast(message, type = 'info') {
  const root = document.getElementById('toast-root') || document.body;
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  
  const icon = type === 'success' ? '✓' : type === 'error' ? '✕' : type === 'warning' ? '⚠' : 'ℹ';
  toast.innerHTML = `
    <span style="font-weight: 700; font-size: 16px;">${icon}</span>
    <div style="flex: 1; word-break: break-word;">${escapeHtml(message)}</div>
  `;
  
  root.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(10px)';
    toast.style.transition = 'all 0.2s ease-out';
    setTimeout(() => toast.remove(), 250);
  }, 3800);
}

// Attach listener for custom toast events
window.addEventListener('edr:toast', (e) => {
  if (e.detail?.message) {
    showToast(e.detail.message, e.detail.type || 'info');
  }
});

// Modal System
export function showModal({ title, content, confirmText = 'Confirm', cancelText = 'Cancel', confirmClass = 'btn-primary', onConfirm, onCancel }) {
  const root = document.getElementById('modal-root') || document.body;
  const overlay = document.createElement('div');
  overlay.className = 'modal-overlay';
  
  overlay.innerHTML = `
    <div class="modal-dialog">
      <div class="modal-header">
        <h3 class="modal-title">${escapeHtml(title)}</h3>
        <button class="modal-close" aria-label="Close">&times;</button>
      </div>
      <div class="modal-body">${content}</div>
      <div class="modal-footer">
        <button class="btn btn-outline modal-cancel-btn">${escapeHtml(cancelText)}</button>
        <button class="btn ${confirmClass} modal-confirm-btn">${escapeHtml(confirmText)}</button>
      </div>
    </div>
  `;

  const close = () => {
    overlay.classList.remove('open');
    setTimeout(() => overlay.remove(), 200);
  };

  overlay.querySelector('.modal-close').onclick = () => {
    if (onCancel) onCancel();
    close();
  };
  overlay.querySelector('.modal-cancel-btn').onclick = () => {
    if (onCancel) onCancel();
    close();
  };
  overlay.querySelector('.modal-confirm-btn').onclick = async (e) => {
    if (onConfirm) {
      e.target.disabled = true;
      try {
        await onConfirm();
        close();
      } catch (err) {
        showToast(err.message || 'Action failed', 'error');
        e.target.disabled = false;
      }
    } else {
      close();
    }
  };

  root.appendChild(overlay);
  requestAnimationFrame(() => overlay.classList.add('open'));
}

export function renderPagination({ page = 1, pageSize = 20, total = 0, onPageChange }) {
  const totalPages = Math.ceil(total / pageSize) || 1;
  const startItem = total > 0 ? (page - 1) * pageSize + 1 : 0;
  const endItem = Math.min(page * pageSize, total);

  return `
    <div class="pagination">
      <div class="pagination-info">Showing ${startItem}–${endItem} of ${total} results</div>
      <div class="pagination-controls">
        <button class="btn btn-sm btn-outline prev-page-btn" ${page <= 1 ? 'disabled' : ''}>Previous</button>
        <span style="font-size: 13px; font-weight: 600; padding: 4px 10px;">Page ${page} of ${totalPages}</span>
        <button class="btn btn-sm btn-outline next-page-btn" ${page >= totalPages ? 'disabled' : ''}>Next</button>
      </div>
    </div>
  `;
}
