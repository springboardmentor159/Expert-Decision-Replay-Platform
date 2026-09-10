import React from 'react';
import { useAuth } from '../../context/AuthContext';
import { RoleBadge } from '../common/Badge';
import { LogOut, User, ShieldCheck, Menu } from 'lucide-react';

export const Navbar = ({ onToggleSidebar, activePageTitle = 'Dashboard' }) => {
  const { user, logout } = useAuth();

  return (
    <header className="top-navbar">
      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
        <button
          onClick={onToggleSidebar}
          style={{
            display: 'none',
            background: 'transparent',
            border: 'none',
            color: 'var(--text-primary)',
            cursor: 'pointer',
          }}
          className="mobile-menu-btn"
        >
          <Menu size={22} />
        </button>
        <h2 style={{ fontSize: '1.25rem', fontWeight: 700, color: '#ffffff', letterSpacing: '-0.02em' }}>
          {activePageTitle}
        </h2>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '1.25rem' }}>
        {user && (
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.85rem',
              background: 'rgba(255, 255, 255, 0.04)',
              padding: '0.4rem 0.85rem',
              borderRadius: 'var(--radius-full)',
              border: '1px solid var(--border-subtle)',
            }}
          >
            <div
              style={{
                width: '32px',
                height: '32px',
                borderRadius: '50%',
                background: 'linear-gradient(135deg, var(--accent-blue), var(--accent-cyan))',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#ffffff',
                fontWeight: 700,
                fontSize: '0.85rem',
              }}
            >
              {user.full_name?.charAt(0) || 'U'}
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', lineHeight: 1.2 }}>
              <span style={{ fontSize: '0.875rem', fontWeight: 600, color: '#ffffff' }}>
                {user.full_name}
              </span>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                {user.department || user.role}
              </span>
            </div>
            <RoleBadge role={user.role} />
          </div>
        )}

        <button
          onClick={logout}
          title="Sign out"
          style={{
            background: 'rgba(244, 63, 94, 0.1)',
            border: '1px solid rgba(244, 63, 94, 0.25)',
            color: 'var(--accent-rose)',
            padding: '0.5rem',
            borderRadius: 'var(--radius-md)',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '0.4rem',
            fontSize: '0.85rem',
            fontWeight: 600,
            transition: 'all 0.2s',
          }}
          onMouseOver={(e) => (e.currentTarget.style.background = 'rgba(244, 63, 94, 0.2)')}
          onMouseOut={(e) => (e.currentTarget.style.background = 'rgba(244, 63, 94, 0.1)')}
        >
          <LogOut size={16} />
          <span>Logout</span>
        </button>
      </div>
    </header>
  );
};
