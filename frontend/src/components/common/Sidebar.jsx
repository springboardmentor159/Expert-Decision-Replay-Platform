import React from 'react';
import { NavLink } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import {
  LayoutDashboard,
  FileText,
  PlusCircle,
  MessagesSquare,
  Search,
  CheckSquare,
  BarChart3,
  Users,
  ShieldAlert,
  FileSpreadsheet,
  Layers,
  Sparkles,
  Award,
} from 'lucide-react';
import { RoleBadge } from './StatusBadge';

export const Sidebar = () => {
  const { user } = useAuth();
  const role = user?.role || 'Employee';

  // Define navigation items according to user role
  const getNavSections = () => {
    switch (role) {
      case 'Reviewer':
        return [
          {
            title: 'Reviewer Workspace',
            items: [
              { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
              { to: '/reviewer/reviews', label: 'Assigned Reviews', icon: CheckSquare },
              { to: '/decisions', label: 'All Decisions', icon: FileText },
              { to: '/repository', label: 'Knowledge Base', icon: Search },
            ],
          },
        ];

      case 'Manager':
        return [
          {
            title: 'Manager Operations',
            items: [
              { to: '/dashboard', label: 'Manager Dashboard', icon: LayoutDashboard },
              { to: '/decisions', label: 'Team Decisions', icon: FileText },
              { to: '/manager/approvals', label: 'Pending Approvals', icon: CheckSquare },
              { to: '/decisions/create', label: 'Create Decision', icon: PlusCircle },
              { to: '/reports', label: 'Decision Reports', icon: FileSpreadsheet },
              { to: '/repository', label: 'Knowledge Base', icon: Search },
            ],
          },
        ];

      case 'Administrator':
        return [
          {
            title: 'Administration',
            items: [
              { to: '/dashboard', label: 'Admin Dashboard', icon: LayoutDashboard },
              { to: '/admin/users', label: 'User Management', icon: Users },
              { to: '/audit-logs', label: 'Audit & Compliance', icon: ShieldAlert },
              { to: '/reports', label: 'Reports & Export', icon: FileSpreadsheet },
            ],
          },
          {
            title: 'Decision Intelligence',
            items: [
              { to: '/decisions', label: 'All Decisions', icon: FileText },
              { to: '/decisions/create', label: 'Create Decision', icon: PlusCircle },
              { to: '/repository', label: 'Knowledge Base', icon: Search },
            ],
          },
        ];

      case 'Employee':
      default:
        return [
          {
            title: 'My Workspace',
            items: [
              { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
              { to: '/decisions', label: 'My Decisions', icon: FileText },
              { to: '/decisions/create', label: 'Create Decision', icon: PlusCircle },
              { to: '/repository', label: 'Knowledge Base', icon: Search },
            ],
          },
        ];
    }
  };

  const navSections = getNavSections();

  return (
    <aside className="app-sidebar">
      <div className="sidebar-header">
        <div className="app-brand-logo">
          <Layers size={22} />
        </div>
        <div className="app-brand-text">
          <span className="app-brand-title">Decision Replay</span>
          <span className="app-brand-subtitle">Enterprise Suite</span>
        </div>
      </div>

      <nav className="sidebar-nav">
        {navSections.map((section, idx) => (
          <div key={idx} style={{ marginBottom: '0.75rem' }}>
            <div className="nav-section-label">{section.title}</div>
            {section.items.map((item) => {
              const Icon = item.icon;
              return (
                <NavLink
                  key={item.to}
                  to={item.to}
                  className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
                  end={item.to === '/dashboard'}
                >
                  <Icon size={18} />
                  <span>{item.label}</span>
                </NavLink>
              );
            })}
          </div>
        ))}
      </nav>

      <div className="sidebar-footer">
        <div className="user-snippet">
          <div className="user-avatar">
            {user?.full_name ? user.full_name.charAt(0).toUpperCase() : 'U'}
          </div>
          <div className="user-meta">
            <span className="user-name">{user?.full_name || 'User'}</span>
            <span className="user-role-text">{user?.department || role}</span>
          </div>
        </div>
      </div>
    </aside>
  );
};
