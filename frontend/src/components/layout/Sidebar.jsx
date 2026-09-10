import React from 'react';
import { useAuth } from '../../context/AuthContext';
import {
  LayoutDashboard,
  FileText,
  PlusCircle,
  Search,
  CheckSquare,
  BarChart3,
  ShieldAlert,
  Users,
  MessageSquare,
  Sliders,
  Layers,
  Sparkles,
} from 'lucide-react';

export const Sidebar = ({ currentRoute, onRouteChange, isOpen }) => {
  const { role } = useAuth();

  // Define navigation items per role
  const getNavItems = () => {
    switch (role) {
      case 'Administrator':
        return [
          { id: 'dashboard', label: 'Admin Dashboard', icon: LayoutDashboard },
          { id: 'decisions', label: 'All Decisions', icon: FileText },
          { id: 'create-decision', label: 'Create Decision', icon: PlusCircle },
          { id: 'repository', label: 'Knowledge Repository', icon: Search },
          { id: 'users', label: 'User Management', icon: Users },
          { id: 'audit', label: 'Audit & Activity Logs', icon: ShieldAlert },
          { id: 'reports', label: 'System Reports', icon: BarChart3 },
        ];

      case 'Manager':
        return [
          { id: 'dashboard', label: 'Manager Dashboard', icon: LayoutDashboard },
          { id: 'decisions', label: 'Team Decisions', icon: FileText },
          { id: 'create-decision', label: 'Create Decision', icon: PlusCircle },
          { id: 'pending-approvals', label: 'Pending Approvals', icon: CheckSquare },
          { id: 'repository', label: 'Knowledge Repository', icon: Search },
          { id: 'reports', label: 'Decision Reports', icon: BarChart3 },
        ];

      case 'Reviewer':
        return [
          { id: 'dashboard', label: 'Reviewer Dashboard', icon: LayoutDashboard },
          { id: 'pending-approvals', label: 'Assigned Reviews', icon: CheckSquare },
          { id: 'decisions', label: 'Decisions & Alternatives', icon: FileText },
          { id: 'repository', label: 'Knowledge Repository', icon: Search },
        ];

      case 'Employee':
      default:
        return [
          { id: 'dashboard', label: 'My Dashboard', icon: LayoutDashboard },
          { id: 'decisions', label: 'My Decisions', icon: FileText },
          { id: 'create-decision', label: 'Create Decision', icon: PlusCircle },
          { id: 'repository', label: 'Knowledge Repository', icon: Search },
        ];
    }
  };

  const navItems = getNavItems();

  return (
    <aside className={`sidebar ${isOpen ? 'open' : ''}`}>
      {/* Brand Header */}
      <div
        style={{
          padding: '1.5rem 1.25rem',
          borderBottom: '1px solid var(--border-subtle)',
          display: 'flex',
          alignItems: 'center',
          gap: '0.75rem',
        }}
      >
        <div
          style={{
            width: '38px',
            height: '38px',
            borderRadius: 'var(--radius-md)',
            background: 'linear-gradient(135deg, #3b82f6, #8b5cf6)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#ffffff',
            boxShadow: 'var(--shadow-glow-blue)',
          }}
        >
          <Sparkles size={22} />
        </div>
        <div>
          <h1 style={{ fontSize: '1.05rem', fontWeight: 800, color: '#ffffff', lineHeight: 1.1 }}>
            Expert Replay
          </h1>
          <span style={{ fontSize: '0.72rem', color: 'var(--accent-cyan)', fontWeight: 600, letterSpacing: '0.04em' }}>
            ENTERPRISE PLATFORM
          </span>
        </div>
      </div>

      {/* Role Badge Indicator */}
      <div style={{ padding: '0.85rem 1.25rem 0.25rem' }}>
        <span style={{ fontSize: '0.7rem', textTransform: 'uppercase', color: 'var(--text-muted)', fontWeight: 700, letterSpacing: '0.06em' }}>
          Role: {role || 'Guest'}
        </span>
      </div>

      {/* Navigation List */}
      <nav style={{ flex: 1, padding: '0.75rem', display: 'flex', flexDirection: 'column', gap: '0.35rem' }}>
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentRoute === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onRouteChange(item.id)}
              className={`nav-link ${isActive ? 'active' : ''}`}
              style={{
                width: '100%',
                textAlign: 'left',
                border: 'none',
                background: isActive ? undefined : 'transparent',
              }}
            >
              <Icon size={18} color={isActive ? '#60a5fa' : 'currentColor'} />
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>

      {/* Footer Info */}
      <div
        style={{
          padding: '1.25rem',
          borderTop: '1px solid var(--border-subtle)',
          fontSize: '0.75rem',
          color: 'var(--text-muted)',
          display: 'flex',
          flexDirection: 'column',
          gap: '0.25rem',
        }}
      >
        <span style={{ fontWeight: 600, color: 'var(--text-secondary)' }}>Sprint 14 UI Release</span>
        <span>Connected to FastAPI v1.0.0</span>
      </div>
    </aside>
  );
};
