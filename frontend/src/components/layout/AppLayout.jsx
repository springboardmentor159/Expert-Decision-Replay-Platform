import React, { useState } from 'react';
import { Navbar } from './Navbar';
import { Sidebar } from './Sidebar';

export const AppLayout = ({ children, currentRoute, onRouteChange, pageTitle }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="app-container">
      <Sidebar
        currentRoute={currentRoute}
        onRouteChange={(route) => {
          onRouteChange(route);
          setSidebarOpen(false);
        }}
        isOpen={sidebarOpen}
      />
      <div className="main-content">
        <Navbar
          activePageTitle={pageTitle}
          onToggleSidebar={() => setSidebarOpen(!sidebarOpen)}
        />
        <main className="page-body">{children}</main>
      </div>
    </div>
  );
};
