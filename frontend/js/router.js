// Hash-based Client-Side Router with Route Guards
import { auth } from './auth.js';
import { renderLayout, bindLayoutEvents } from './components/layout.js';
import { renderAuthView, bindAuthEvents } from './views/authView.js';
import { renderDashboardView } from './views/dashboardView.js';
import { renderDecisionListView, bindDecisionListEvents } from './views/decisionListView.js';
import { renderCreateDecisionView, bindCreateDecisionEvents } from './views/createDecisionView.js';
import { renderDecisionDetailView, bindDecisionDetailEvents } from './views/decisionDetailView.js';
import { renderRepositoryView, bindRepositoryEvents } from './views/repositoryView.js';
import { renderReportsView, bindReportsEvents } from './views/reportsView.js';
import { renderAuditView, bindAuditEvents } from './views/auditView.js';
import { loadingState, errorState } from './components/ui.js';

class Router {
  constructor() {
    this.appRoot = document.getElementById('app');
    window.addEventListener('hashchange', () => this.handleRoute());
  }

  async handleRoute() {
    const rawHash = window.location.hash || '#dashboard';
    const [pathPart, queryPart] = rawHash.split('?');
    const queryParams = Object.fromEntries(new URLSearchParams(queryPart || ''));

    // Route Guards
    const isAuthRoute = pathPart === '#login' || pathPart === '#register';

    if (!auth.isAuthenticated()) {
      if (!isAuthRoute) {
        window.location.hash = '#login';
        return;
      }
    } else {
      if (isAuthRoute) {
        window.location.hash = '#dashboard';
        return;
      }
    }

    // Render Auth View directly without layout shell
    if (isAuthRoute) {
      const isRegister = pathPart === '#register';
      this.appRoot.innerHTML = renderAuthView(isRegister);
      bindAuthEvents(isRegister);
      return;
    }

    // Render Loading indicator inside app
    this.appRoot.innerHTML = `
      <div style="min-height: 100vh; display: flex; align-items: center; justify-content: center; background: var(--bg-app);">
        ${loadingState('Loading workspace...')}
      </div>
    `;

    try {
      let viewHtml = '';
      let pageTitle = 'Dashboard';
      let bindEvents = () => {};

      if (pathPart === '#dashboard' || pathPart === '') {
        pageTitle = `${auth.currentUser?.role || 'User'} Dashboard`;
        viewHtml = await renderDashboardView();
      } else if (pathPart === '#decisions') {
        pageTitle = 'Decision Management';
        viewHtml = await renderDecisionListView(queryParams);
        bindEvents = () => bindDecisionListEvents();
      } else if (pathPart === '#decisions/create') {
        pageTitle = 'Create Decision';
        viewHtml = await renderCreateDecisionView();
        bindEvents = () => bindCreateDecisionEvents();
      } else if (pathPart.startsWith('#decisions/')) {
        const id = pathPart.replace('#decisions/', '');
        pageTitle = `Decision Details #${id}`;
        viewHtml = await renderDecisionDetailView(id);
        bindEvents = () => bindDecisionDetailEvents(id);
      } else if (pathPart === '#repository') {
        pageTitle = 'Knowledge Repository';
        viewHtml = await renderRepositoryView(queryParams);
        bindEvents = () => bindRepositoryEvents();
      } else if (pathPart === '#reports') {
        pageTitle = 'Decision Analytics & Reports';
        const activeTab = queryParams.tab || 'decisions';
        viewHtml = await renderReportsView(activeTab, queryParams);
        bindEvents = () => bindReportsEvents(activeTab);
      } else if (pathPart === '#audit') {
        pageTitle = 'Audit & Security Activity';
        const subtab = queryParams.subtab || 'audit';
        viewHtml = await renderAuditView(subtab, queryParams);
        bindEvents = () => bindAuditEvents();
      } else {
        pageTitle = 'Overview';
        viewHtml = await renderDashboardView();
      }

      // Wrap inside layout shell
      this.appRoot.innerHTML = renderLayout(viewHtml, pageTitle);
      bindLayoutEvents();
      bindEvents();
    } catch (err) {
      this.appRoot.innerHTML = renderLayout(errorState(err.message), 'Error');
      bindLayoutEvents();
    }
  }
}

export const router = new Router();
