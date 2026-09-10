import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { Search, LogOut, User as UserIcon, Shield, Bell } from 'lucide-react';
import { RoleBadge } from './StatusBadge';

export const Navbar = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/repository?q=${encodeURIComponent(searchQuery.trim())}`);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <header className="app-header">
      <div className="header-left">
        <form onSubmit={handleSearch} className="header-search">
          <Search size={16} className="header-search-icon" />
          <input
            type="text"
            placeholder="Search decisions, criteria, rationale..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </form>
      </div>

      <div className="header-right">
        <RoleBadge role={user?.role} />

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <button
            className="btn btn-secondary btn-sm"
            onClick={handleLogout}
            title="Sign out of your session"
          >
            <LogOut size={16} />
            <span>Sign Out</span>
          </button>
        </div>
      </div>
    </header>
  );
};
