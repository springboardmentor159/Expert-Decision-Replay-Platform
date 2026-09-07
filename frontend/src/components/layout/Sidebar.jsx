import React from 'react';
import {
  LayoutDashboard,
  FilePlus2,
  ListFilter,
  CheckSquare,
  Users,
  Search,
  History,
  FileBarChart,
  ShieldAlert,
  GitPullRequest,
  BarChart3,
  Bookmark,
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

export function Sidebar({ currentView, setCurrentView }) {
  const { role, isEmployee, isReviewer, isManager, isAdmin } = useAuth();

  const navItems = [];

  // Common or Role-Specific Dashboard
  navItems.push({
    id: 'dashboard',
    label: isAdmin ? 'Admin Dashboard' : 'Dashboard',
    icon: LayoutDashboard,
  });

  // Employee Navigation
  if (isEmployee) {
    navItems.push(
      { id: 'create-decision', label: 'Create Decision', icon: FilePlus2 },
      { id: 'my-decisions', label: 'My Decisions', icon: ListFilter },
      { id: 'repository', label: 'Knowledge Repository', icon: Search },
      { id: 'reports', label: 'Reports', icon: FileBarChart }
    );
  }

  // Reviewer Navigation
  if (isReviewer) {
    navItems.push(
      { id: 'assigned-reviews', label: 'Assigned Reviews', icon: CheckSquare },
      { id: 'all-decisions', label: 'All Decisions', icon: ListFilter },
      { id: 'repository', label: 'Knowledge Repository', icon: Search },
      { id: 'reports', label: 'Reports', icon: FileBarChart }
    );
  }

  // Manager Navigation
  if (isManager) {
    navItems.push(
      { id: 'team-decisions', label: 'Team Decisions', icon: ListFilter },
      { id: 'pending-approvals', label: 'Pending Approvals', icon: GitPullRequest },
      { id: 'create-decision', label: 'Create Decision', icon: FilePlus2 },
      { id: 'repository', label: 'Knowledge Repository', icon: Search },
      { id: 'reports', label: 'Reports & Analytics', icon: BarChart3 }
    );
  }

  // Administrator Navigation
  if (isAdmin) {
    navItems.push(
      { id: 'all-decisions', label: 'Decision Management', icon: ListFilter },
      { id: 'create-decision', label: 'Create Decision', icon: FilePlus2 },
      { id: 'user-management', label: 'User Management', icon: Users },
      { id: 'audit-logs', label: 'Audit & Activity Logs', icon: ShieldAlert },
      { id: 'repository', label: 'Knowledge Repository', icon: Search },
      { id: 'reports', label: 'Reports & Export', icon: FileBarChart }
    );
  }

  return (
    <aside style={{
      width: '260px',
      background: 'var(--bg-sidebar)',
      borderRight: '1px solid var(--border-color)',
      display: 'flex',
      flexDirection: 'column',
      flexShrink: 0,
      padding: '1.25rem 0.85rem',
      gap: '0.4rem',
    }}>
      <div style={{
        padding: '0.5rem 0.75rem 1rem',
        fontSize: '0.72rem',
        fontWeight: 700,
        textTransform: 'uppercase',
        letterSpacing: '0.08em',
        color: 'var(--text-muted)',
      }}>
        {role ? `${role} Workspace` : 'Workspace'}
      </div>

      <nav style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem', flex: 1 }}>
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentView === item.id;

          return (
            <button
              key={item.id}
              onClick={() => setCurrentView(item.id)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.75rem',
                width: '100%',
                padding: '0.65rem 0.9rem',
                borderRadius: '8px',
                border: '1px solid',
                borderColor: isActive ? 'var(--primary)' : 'transparent',
                background: isActive ? 'var(--bg-active)' : 'transparent',
                color: isActive ? 'var(--primary)' : 'var(--text-secondary)',
                fontWeight: isActive ? 600 : 500,
                fontSize: '0.875rem',
                cursor: 'pointer',
                textAlign: 'left',
                transition: 'all 0.15s ease',
              }}
              onMouseEnter={(e) => {
                if (!isActive) {
                  e.currentTarget.style.background = 'var(--bg-hover)';
                  e.currentTarget.style.color = 'var(--text-primary)';
                }
              }}
              onMouseLeave={(e) => {
                if (!isActive) {
                  e.currentTarget.style.background = 'transparent';
                  e.currentTarget.style.color = 'var(--text-secondary)';
                }
              }}
            >
              <Icon size={18} style={{ color: isActive ? 'var(--primary)' : 'var(--text-muted)' }} />
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>

      {/* Role Footer Card */}
      <div style={{
        background: 'var(--bg-hover)',
        border: '1px solid var(--border-color)',
        borderRadius: '10px',
        padding: '0.85rem',
        fontSize: '0.775rem',
        color: 'var(--text-muted)',
        marginTop: 'auto',
      }}>
        <div style={{ fontWeight: 600, color: 'var(--text-primary)', marginBottom: '2px' }}>
          Role: {role}
        </div>
        <div>Access privileges scoped to organization governance policies.</div>
      </div>
    </aside>
  );
}
