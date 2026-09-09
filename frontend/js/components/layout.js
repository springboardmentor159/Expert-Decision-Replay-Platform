// Role-Based Layout Shell & Navigation Component
import { auth } from '../auth.js';
import { escapeHtml } from './ui.js';

export function renderLayout(contentHtml, pageTitle = 'Dashboard', pageSubtitle = '') {
  const user = auth.currentUser;
  const role = auth.getRole();
  const currentHash = window.location.hash || '#dashboard';

  // Define navigation items based on role specifications in Part 3
  let navItems = [];

  if (role === 'employee') {
    navItems = [
      { hash: '#dashboard', label: 'Dashboard', icon: '📊' },
      { hash: '#decisions', label: 'My Decisions', icon: '📝' },
      { hash: '#decisions/create', label: 'Create Decision', icon: '➕' },
      { hash: '#repository', label: 'Knowledge Repository', icon: '🔍' },
      { hash: '#reports', label: 'Reports', icon: '📈' },
    ];
  } else if (role === 'reviewer') {
    navItems = [
      { hash: '#dashboard', label: 'Reviewer Dashboard', icon: '🛡️' },
      { hash: '#decisions', label: 'Assigned Reviews', icon: '📋' },
      { hash: '#repository', label: 'Knowledge Repository', icon: '🔍' },
      { hash: '#reports', label: 'Reports', icon: '📈' },
    ];
  } else if (role === 'manager') {
    navItems = [
      { hash: '#dashboard', label: 'Manager Dashboard', icon: '📊' },
      { hash: '#decisions', label: 'Team Decisions', icon: '👥' },
      { hash: '#decisions/create', label: 'Create Decision', icon: '➕' },
      { hash: '#repository', label: 'Knowledge Repository', icon: '🔍' },
      { hash: '#reports', label: 'Decision Analytics & Reports', icon: '📈' },
      { hash: '#audit', label: 'Audit Activity', icon: '📜' },
    ];
  } else {
    // Administrator / default
    navItems = [
      { hash: '#dashboard', label: 'Admin Dashboard', icon: '⚡' },
      { hash: '#decisions', label: 'All Decisions', icon: '📋' },
      { hash: '#decisions/create', label: 'Create Decision', icon: '➕' },
      { hash: '#repository', label: 'Knowledge Repository', icon: '🔍' },
      { hash: '#audit', label: 'Audit & Security Logs', icon: '🛡️' },
      { hash: '#reports', label: 'System Reports', icon: '📈' },
    ];
  }

  const roleTitle = user?.role ? escapeHtml(user.role) : 'User';
  const department = user?.department ? escapeHtml(user.department) : 'Workspace';

  return `
    <div class="app-container">
      <!-- Collapsible Sidebar -->
      <aside class="app-sidebar" id="app-sidebar">
        <div class="sidebar-brand">
          <div class="brand-icon">⚡</div>
          <div class="brand-info">
            <span class="brand-title">Decision Replay</span>
            <span class="brand-tagline">Intelligence Platform</span>
          </div>
        </div>

        <nav class="sidebar-nav">
          <div class="nav-section-title">Navigation (${roleTitle})</div>
          ${navItems.map(item => {
            const isActive = currentHash === item.hash || (item.hash !== '#dashboard' && currentHash.startsWith(item.hash));
            return `
              <a href="${item.hash}" class="nav-link ${isActive ? 'active' : ''}">
                <span class="nav-icon">${item.icon}</span>
                <span>${escapeHtml(item.label)}</span>
              </a>
            `;
          }).join('')}
        </nav>

        <div class="sidebar-footer">
          <div class="user-profile-pill">
            <div class="user-avatar">${escapeHtml((user?.full_name || 'U').charAt(0).toUpperCase())}</div>
            <div class="user-details">
              <span class="user-name" title="${escapeHtml(user?.full_name || '')}">${escapeHtml(user?.full_name || 'Anonymous')}</span>
              <span class="user-role-badge">${roleTitle} • ${department}</span>
            </div>
          </div>
          <button class="btn btn-sm btn-outline" id="btn-logout" style="width: 100%; justify-content: center;">
            Sign Out
          </button>
        </div>
      </aside>

      <!-- Main Shell -->
      <div class="app-main">
        <header class="app-topbar">
          <div class="topbar-breadcrumbs">
            <button class="btn btn-sm btn-outline responsive-only" id="mobile-menu-toggle" style="margin-right: 8px;">☰ Menu</button>
            <span>Workspace</span>
            <span>/</span>
            <span class="breadcrumb-current">${escapeHtml(pageTitle)}</span>
          </div>
          <div class="topbar-actions">
            <span class="role-tag">${roleTitle} Access</span>
            <a href="#decisions/create" class="btn btn-sm btn-primary">+ New Decision</a>
          </div>
        </header>

        <main class="view-container">
          ${contentHtml}
        </main>
      </div>
    </div>
  `;
}

export function bindLayoutEvents() {
  const logoutBtn = document.getElementById('btn-logout');
  if (logoutBtn) {
    logoutBtn.onclick = () => auth.logout(true);
  }

  const toggleBtn = document.getElementById('mobile-menu-toggle');
  const sidebar = document.getElementById('app-sidebar');
  if (toggleBtn && sidebar) {
    toggleBtn.onclick = () => {
      sidebar.classList.toggle('mobile-open');
    };
  }
}
