import React from 'react';
import { LogOut, User as UserIcon, Shield, Layers } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { ThemeToggle } from './ThemeToggle';
import { RoleBadge } from '../common/StatusBadge';

export function Navbar({ onToggleSidebar }) {
  const { user, role, logout, login } = useAuth();

  const handleQuickSwitch = async (email) => {
    try {
      await login(email, 'Password123!');
    } catch {
      // Handled in auth context
    }
  };

  return (
    <header style={{
      height: '68px',
      borderBottom: '1px solid var(--border-color)',
      background: 'var(--bg-card)',
      backdropFilter: 'var(--glass-blur)',
      padding: '0 1.5rem',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      position: 'sticky',
      top: 0,
      zIndex: 100,
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
        <button
          onClick={onToggleSidebar}
          className="btn btn-secondary btn-sm"
          style={{ display: 'none' }}
          id="sidebar-toggle"
        >
          <Layers size={18} />
        </button>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
          <div style={{
            width: '32px',
            height: '32px',
            borderRadius: '8px',
            background: 'linear-gradient(135deg, var(--primary), var(--purple))',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#fff',
            fontWeight: 'bold',
            fontSize: '0.9rem',
          }}>
            ED
          </div>
          <div>
            <div style={{ fontWeight: 700, fontSize: '1rem', letterSpacing: '-0.01em' }}>
              Expert Decision Replay
            </div>
            <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
              Audit-Grade Governance Platform
            </div>
          </div>
        </div>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
        {/* Quick Role Switcher for Demo Evaluation */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.35rem',
          background: 'var(--bg-hover)',
          padding: '0.3rem 0.5rem',
          borderRadius: '8px',
          border: '1px solid var(--border-color)',
          fontSize: '0.75rem',
        }}>
          <span style={{ color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '4px' }}>
            <Shield size={13} /> Switch Role:
          </span>
          <button
            onClick={() => handleQuickSwitch('employee@example.com')}
            className={`btn btn-sm ${role === 'Employee' ? 'btn-primary' : 'btn-secondary'}`}
            style={{ padding: '0.2rem 0.5rem', fontSize: '0.72rem' }}
            title="Log in as Employee"
          >
            Employee
          </button>
          <button
            onClick={() => handleQuickSwitch('reviewer@example.com')}
            className={`btn btn-sm ${role === 'Reviewer' ? 'btn-primary' : 'btn-secondary'}`}
            style={{ padding: '0.2rem 0.5rem', fontSize: '0.72rem' }}
            title="Log in as Reviewer"
          >
            Reviewer
          </button>
          <button
            onClick={() => handleQuickSwitch('manager@example.com')}
            className={`btn btn-sm ${role === 'Manager' ? 'btn-primary' : 'btn-secondary'}`}
            style={{ padding: '0.2rem 0.5rem', fontSize: '0.72rem' }}
            title="Log in as Manager"
          >
            Manager
          </button>
          <button
            onClick={() => handleQuickSwitch('admin@example.com')}
            className={`btn btn-sm ${role === 'Administrator' ? 'btn-primary' : 'btn-secondary'}`}
            style={{ padding: '0.2rem 0.5rem', fontSize: '0.72rem' }}
            title="Log in as Administrator"
          >
            Admin
          </button>
        </div>

        {/* Light/Dark Theme Switcher */}
        <ThemeToggle />

        {/* User Info & Profile */}
        {user && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginLeft: '0.5rem' }}>
            <div style={{
              width: '36px',
              height: '36px',
              borderRadius: '50%',
              background: 'var(--primary-light)',
              color: 'var(--primary)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontWeight: 600,
              fontSize: '0.85rem',
              border: '1px solid var(--border-color)',
            }}>
              {user.full_name?.charAt(0) || <UserIcon size={18} />}
            </div>
            <div style={{ lineHeight: 1.2 }}>
              <div style={{ fontWeight: 600, fontSize: '0.875rem' }}>{user.full_name}</div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', marginTop: '2px' }}>
                <RoleBadge role={user.role} />
                {user.department && (
                  <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                    • {user.department}
                  </span>
                )}
              </div>
            </div>

            <button
              onClick={logout}
              className="btn btn-secondary btn-sm"
              style={{ marginLeft: '0.5rem', padding: '0.4rem 0.6rem' }}
              title="Log Out"
            >
              <LogOut size={16} />
            </button>
          </div>
        )}
      </div>
    </header>
  );
}
