import React, { useState } from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import Navbar from './Navbar';
import Sidebar from './Sidebar';

export const AppLayout = () => {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const location = useLocation();

  const toggleSidebar = () => setSidebarOpen((prev) => !prev);

  // Breadcrumb / title based on pathname
  const getPageTitle = () => {
    const path = location.pathname;
    if (path.includes('/dashboard')) return 'Dashboard';
    if (path.includes('/decisions')) return 'Decisions Overview';
    if (path.includes('/manager')) return 'Manager Statistics';
    if (path.includes('/admin/users')) return 'User Administration';
    if (path.includes('/admin/audit')) return 'System Audit Trail';
    if (path.includes('/admin/security-logs')) return 'Security & Access Logs';
    if (path.includes('/reports')) return 'Reports & Data Exports';
    return 'Workspace';
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Navbar onToggleSidebar={toggleSidebar} sidebarOpen={sidebarOpen} />

      {/* Apple Sub-Nav Frosted Glass Strip (52px) */}
      <div
        style={{
          height: '52px',
          backgroundColor: 'rgba(245, 245, 247, 0.85)',
          backdropFilter: 'blur(20px) saturate(180%)',
          WebkitBackdropFilter: 'blur(20px) saturate(180%)',
          borderBottom: '1px solid rgba(0, 0, 0, 0.08)',
          position: 'sticky',
          top: '44px',
          zIndex: 80,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '0 32px',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span
            style={{
              fontFamily: 'var(--font-family-display)',
              fontSize: '18px',
              fontWeight: 600,
              color: 'var(--color-ink)',
              letterSpacing: '-0.2px',
            }}
          >
            {getPageTitle()}
          </span>
        </div>
      </div>

      <div style={{ display: 'flex', flex: 1, minHeight: 'calc(100vh - 96px)' }}>
        <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
        <main
          style={{
            flex: 1,
            backgroundColor: 'var(--color-canvas-parchment)',
            overflowY: 'auto',
            padding: '32px',
          }}
        >
          <div style={{ maxWidth: '1440px', margin: '0 auto' }}>
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
};

export default AppLayout;
