import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  FileText,
  Users,
  ShieldAlert,
  BarChart3,
  History,
  FileCheck2,
  Lock,
  Activity,
  Layers,
} from 'lucide-react';
import { useAuth, UserRole } from '../../context/AuthContext';

export const Sidebar = ({ isOpen, onClose }) => {
  const { user, hasRole } = useAuth();

  const navSections = [
    {
      title: 'Workspace',
      items: [
        {
          label: 'Dashboard',
          path: '/dashboard',
          icon: LayoutDashboard,
          roles: null, // all roles
        },
        {
          label: 'Decisions',
          path: '/decisions',
          icon: FileText,
          roles: null,
        },
      ],
    },
    {
      title: 'Management',
      roles: [UserRole.MANAGER, UserRole.ADMINISTRATOR],
      items: [
        {
          label: 'Manager Stats',
          path: '/manager/stats',
          icon: BarChart3,
          roles: [UserRole.MANAGER, UserRole.ADMINISTRATOR],
        },
        {
          label: 'Reports & Exports',
          path: '/reports',
          icon: FileCheck2,
          roles: [UserRole.MANAGER, UserRole.ADMINISTRATOR],
        },
      ],
    },
    {
      title: 'Administration & Security',
      roles: [UserRole.ADMINISTRATOR],
      items: [
        {
          label: 'User Management',
          path: '/admin/users',
          icon: Users,
          roles: [UserRole.ADMINISTRATOR],
        },
        {
          label: 'Audit Trail',
          path: '/admin/audit',
          icon: History,
          roles: [UserRole.ADMINISTRATOR],
        },
        {
          label: 'Security & Access Logs',
          path: '/admin/security-logs',
          icon: ShieldAlert,
          roles: [UserRole.ADMINISTRATOR],
        },
      ],
    },
  ];

  return (
    <>
      {/* Mobile Backdrop */}
      {isOpen && (
        <div
          onClick={onClose}
          style={{
            position: 'fixed',
            inset: 0,
            backgroundColor: 'rgba(0,0,0,0.3)',
            zIndex: 90,
            backdropFilter: 'blur(4px)',
            display: window.innerWidth <= 768 ? 'block' : 'none',
          }}
        />
      )}

      <aside
        style={{
          width: isOpen ? '260px' : '0px',
          minWidth: isOpen ? '260px' : '0px',
          height: 'calc(100vh - 44px)',
          position: 'sticky',
          top: '44px',
          backgroundColor: 'var(--color-canvas)',
          borderRight: isOpen ? '1px solid var(--color-hairline)' : 'none',
          transition: 'width 0.2s ease, min-width 0.2s ease, opacity 0.2s ease',
          overflow: 'hidden',
          zIndex: 95,
          display: 'flex',
          flexDirection: 'column',
          boxShadow: isOpen ? 'var(--shadow-subtle)' : 'none',
        }}
      >
        <div
          style={{
            padding: '24px 16px',
            overflowY: 'auto',
            display: 'flex',
            flexDirection: 'column',
            gap: '24px',
            width: '260px',
          }}
        >
          {navSections.map((section) => {
            if (section.roles && !hasRole(section.roles)) return null;

            const visibleItems = section.items.filter(
              (item) => !item.roles || hasRole(item.roles)
            );

            if (visibleItems.length === 0) return null;

            return (
              <div key={section.title}>
                <div
                  style={{
                    fontSize: '11px',
                    fontWeight: 700,
                    textTransform: 'uppercase',
                    letterSpacing: '0.05em',
                    color: 'var(--color-ink-muted-48)',
                    padding: '0 12px 8px 12px',
                  }}
                >
                  {section.title}
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
                  {visibleItems.map((item) => {
                    const Icon = item.icon;
                    return (
                      <NavLink
                        key={item.path}
                        to={item.path}
                        style={({ isActive }) => ({
                          display: 'flex',
                          alignItems: 'center',
                          gap: '10px',
                          padding: '8px 12px',
                          borderRadius: 'var(--radius-sm)',
                          fontSize: '14px',
                          fontWeight: isActive ? 600 : 400,
                          color: isActive ? 'var(--color-primary)' : 'var(--color-ink)',
                          backgroundColor: isActive ? 'var(--color-canvas-parchment)' : 'transparent',
                          textDecoration: 'none',
                          transition: 'background-color 0.1s ease, color 0.1s ease',
                        })}
                      >
                        <Icon size={16} />
                        <span>{item.label}</span>
                      </NavLink>
                    );
                  })}
                </div>
              </div>
            );
          })}

          {/* User Role Card at bottom */}
          <div
            style={{
              marginTop: 'auto',
              padding: '14px',
              backgroundColor: 'var(--color-surface-pearl)',
              borderRadius: 'var(--radius-md)',
              border: '1px solid var(--color-divider-soft)',
              fontSize: '12px',
            }}
          >
            <div style={{ fontWeight: 600, color: 'var(--color-ink)', marginBottom: '2px' }}>
              Current Permission
            </div>
            <div style={{ color: 'var(--color-ink-muted-48)' }}>
              Active role: <strong style={{ color: 'var(--color-primary)' }}>{user?.role || 'Guest'}</strong>
            </div>
          </div>
        </div>
      </aside>
    </>
  );
};

export default Sidebar;
