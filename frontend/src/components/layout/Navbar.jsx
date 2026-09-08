import React from 'react';
import { LogOut, User as UserIcon, Shield, Layers, LayoutGrid } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { Link, useNavigate } from 'react-router-dom';
import Badge from '../common/Badge';

export const Navbar = ({ onToggleSidebar, sidebarOpen }) => {
  const { user, logout, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <header style={{ position: 'sticky', top: 0, zIndex: 100 }}>
      {/* Apple Global Nav (Black bar, 44px) */}
      <div
        style={{
          height: '44px',
          backgroundColor: 'var(--color-surface-black)',
          color: 'var(--color-on-dark)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '0 24px',
          fontSize: '12px',
          letterSpacing: '-0.12px',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
          <button
            onClick={onToggleSidebar}
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'var(--color-on-dark)',
              padding: '4px',
              borderRadius: 'var(--radius-xs)',
            }}
            aria-label="Toggle navigation menu"
          >
            <LayoutGrid size={16} />
          </button>
          <Link
            to="/dashboard"
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              color: 'var(--color-on-dark)',
              fontWeight: 600,
              fontSize: '13px',
              textDecoration: 'none',
            }}
          >
            <Layers size={16} color="var(--color-primary-on-dark)" />
            <span>Expert Decision Replay</span>
          </Link>
        </div>

        {isAuthenticated && user && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <div
                style={{
                  width: '26px',
                  height: '26px',
                  borderRadius: 'var(--radius-pill)',
                  backgroundColor: 'var(--color-surface-tile-1)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: 'var(--color-on-dark)',
                }}
              >
                <UserIcon size={14} />
              </div>
              <span style={{ color: 'var(--color-body-muted)', fontSize: '12px' }}>
                {user.full_name || user.email}
              </span>
              <Badge variant="role" size="small">
                {user.role}
              </Badge>
            </div>

            <button
              onClick={handleLogout}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                color: 'var(--color-body-muted)',
                backgroundColor: 'var(--color-surface-tile-1)',
                padding: '4px 10px',
                borderRadius: 'var(--radius-sm)',
                fontSize: '12px',
                transition: 'color 0.15s ease, background-color 0.15s ease',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.color = '#ffffff';
                e.currentTarget.style.backgroundColor = 'var(--color-surface-tile-2)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.color = 'var(--color-body-muted)';
                e.currentTarget.style.backgroundColor = 'var(--color-surface-tile-1)';
              }}
              title="Sign Out"
            >
              <LogOut size={12} />
              <span>Sign Out</span>
            </button>
          </div>
        )}
      </div>
    </header>
  );
};

export default Navbar;
