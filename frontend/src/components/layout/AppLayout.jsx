import React, { useState } from 'react';
import { Navbar } from './Navbar';
import { Sidebar } from './Sidebar';

export function AppLayout({ currentView, setCurrentView, children }) {
  const [sidebarOpen, setSidebarOpen] = useState(true);

  return (
    <div className="app-container">
      {sidebarOpen && <Sidebar currentView={currentView} setCurrentView={setCurrentView} />}
      <div className="main-content">
        <Navbar
          onToggleSidebar={() => setSidebarOpen(!sidebarOpen)}
          onNavigateProfile={() => setCurrentView('profile')}
        />
        <main className="page-wrapper">{children}</main>
      </div>
    </div>
  );
}
