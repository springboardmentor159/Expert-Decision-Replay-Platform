import React from 'react';
import {
  LayoutDashboard,
  FilePlus2,
  ListFilter,
  CheckSquare,
  Users,
  Search,
  FileBarChart,
  ShieldAlert,
  GitPullRequest,
  BarChart3,
  Layers,
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

export function Sidebar({ currentView, setCurrentView }) {
  const { role, isEmployee, isReviewer, isManager, isAdmin } = useAuth();

  // Grouped Navigation Sections
  const sections = [];

  if (isAdmin) {
    sections.push({
      title: 'Admin Console',
      items: [
        { id: 'dashboard', label: 'Admin Dashboard', icon: LayoutDashboard },
        { id: 'user-management', label: 'User Directory', icon: Users },
        { id: 'audit-logs', label: 'Audit & Activity Logs', icon: ShieldAlert },
      ],
    });
    sections.push({
      title: 'Decisions Governance',
      items: [
        { id: 'all-decisions', label: 'Decision Management', icon: ListFilter },
        { id: 'create-decision', label: 'Create Decision', icon: FilePlus2 },
      ],
    });
    sections.push({
      title: 'Knowledge & Analytics',
      items: [
        { id: 'repository', label: 'Knowledge Repository', icon: Search },
        { id: 'reports', label: 'Reports & Exports', icon: FileBarChart },
      ],
    });
  } else if (isManager) {
    sections.push({
      title: 'Manager Workspace',
      items: [
        { id: 'dashboard', label: 'Manager Dashboard', icon: LayoutDashboard },
        { id: 'team-decisions', label: 'Team Decisions', icon: ListFilter },
        { id: 'pending-approvals', label: 'Pending Approvals', icon: GitPullRequest },
      ],
    });
    sections.push({
      title: 'Decisions & Deliberation',
      items: [
        { id: 'create-decision', label: 'Create Decision', icon: FilePlus2 },
        { id: 'repository', label: 'Knowledge Repository', icon: Search },
      ],
    });
    sections.push({
      title: 'Reports & Analytics',
      items: [
        { id: 'reports', label: 'Reports & Turnaround', icon: BarChart3 },
      ],
    });
  } else if (isReviewer) {
    sections.push({
      title: 'Reviewer Workspace',
      items: [
        { id: 'dashboard', label: 'Reviewer Dashboard', icon: LayoutDashboard },
        { id: 'assigned-reviews', label: 'Assigned Reviews', icon: CheckSquare },
      ],
    });
    sections.push({
      title: 'Decisions',
      items: [
        { id: 'all-decisions', label: 'All Decisions', icon: ListFilter },
        { id: 'repository', label: 'Knowledge Repository', icon: Search },
        { id: 'reports', label: 'Reports', icon: FileBarChart },
      ],
    });
  } else {
    // Employee
    sections.push({
      title: 'Employee Workspace',
      items: [
        { id: 'dashboard', label: 'Employee Dashboard', icon: LayoutDashboard },
        { id: 'create-decision', label: 'Create Decision', icon: FilePlus2 },
        { id: 'my-decisions', label: 'My Decisions', icon: ListFilter },
      ],
    });
    sections.push({
      title: 'Knowledge & Reporting',
      items: [
        { id: 'repository', label: 'Knowledge Repository', icon: Search },
        { id: 'reports', label: 'Reports', icon: FileBarChart },
      ],
    });
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
      gap: '1.25rem',
      overflowY: 'auto',
    }}>
      <div style={{
        padding: '0.25rem 0.5rem',
        fontSize: '0.72rem',
        fontWeight: 700,
        textTransform: 'uppercase',
        letterSpacing: '0.08em',
        color: 'var(--primary)',
        display: 'flex',
        alignItems: 'center',
        gap: '6px',
      }}>
        <Layers size={14} /> {role ? `${role} Portal` : 'Portal'}
      </div>

      <nav style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem', flex: 1 }}>
        {sections.map((sec, secIdx) => (
          <div key={secIdx} style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem' }}>
            <div style={{
              fontSize: '0.68rem',
              fontWeight: 700,
              textTransform: 'uppercase',
              letterSpacing: '0.08em',
              color: 'var(--text-muted)',
              padding: '0 0.5rem 0.2rem',
            }}>
              {sec.title}
            </div>

            {sec.items.map((item) => {
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
                    padding: '0.6rem 0.85rem',
                    borderRadius: '8px',
                    border: '1px solid',
                    borderColor: isActive ? 'var(--primary)' : 'transparent',
                    background: isActive ? 'var(--bg-active)' : 'transparent',
                    color: isActive ? 'var(--primary)' : 'var(--text-secondary)',
                    fontWeight: isActive ? 600 : 500,
                    fontSize: '0.85rem',
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
                  <Icon size={17} style={{ color: isActive ? 'var(--primary)' : 'var(--text-muted)' }} />
                  <span>{item.label}</span>
                </button>
              );
            })}
          </div>
        ))}
      </nav>

      {/* Role Footer */}
      <div style={{
        background: 'var(--bg-hover)',
        border: '1px solid var(--border-color)',
        borderRadius: '10px',
        padding: '0.75rem',
        fontSize: '0.75rem',
        color: 'var(--text-muted)',
        marginTop: 'auto',
      }}>
        <div style={{ fontWeight: 600, color: 'var(--text-primary)', marginBottom: '2px' }}>
          Active Persona: {role}
        </div>
        <div>Dedicated navigation sections scoped to your role.</div>
      </div>
    </aside>
  );
}
