import React, { useState, useEffect } from 'react';
import { Users, Shield, Search, UserCheck, Briefcase, Building } from 'lucide-react';
import { usersApi } from '../../api/users';
import { organizationsApi } from '../../api/organizations';
import { useAuth } from '../../context/AuthContext';
import { useNotification } from '../../context/NotificationContext';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import { RoleBadge } from '../../components/common/StatusBadge';
import { EmptyState } from '../../components/common/EmptyState';

export function UserManagementPage() {
  const { isAdmin } = useAuth();
  const { error } = useNotification();
  const [users, setUsers] = useState([]);
  const [orgMap, setOrgMap] = useState({});
  const [loading, setLoading] = useState(true);
  const [activeRoleTab, setActiveRoleTab] = useState('ALL'); // 'ALL' | 'Employee' | 'Reviewer' | 'Manager' | 'Administrator'
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    async function loadUsers() {
      setLoading(true);
      try {
        const [list, orgs] = await Promise.all([
          usersApi.getUsers(),
          organizationsApi.getPublicList().catch(() => []),
        ]);
        const map = {};
        if (Array.isArray(orgs)) {
          orgs.forEach((o) => {
            map[o.id] = o.name;
          });
        }
        setOrgMap(map);
        setUsers(list || []);
      } catch (err) {
        error(err.message || 'Failed to fetch users');
      } finally {
        setLoading(false);
      }
    }
    loadUsers();
  }, [error]);

  if (!isAdmin) {
    return (
      <EmptyState
        icon={Shield}
        title="Admin Access Required"
        description="Only Administrators can access user directory management."
      />
    );
  }

  const roleCounts = {
    Employee: users.filter((u) => u.role === 'Employee').length,
    Reviewer: users.filter((u) => u.role === 'Reviewer').length,
    Manager: users.filter((u) => u.role === 'Manager').length,
    Administrator: users.filter((u) => u.role === 'Administrator').length,
  };

  const filteredUsers = users.filter((u) => {
    const matchesRole = activeRoleTab === 'ALL' || u.role === activeRoleTab;
    const term = searchTerm.toLowerCase().trim();
    const matchesSearch =
      !term ||
      u.full_name?.toLowerCase().includes(term) ||
      u.email?.toLowerCase().includes(term) ||
      u.department?.toLowerCase().includes(term) ||
      u.employee_id?.toLowerCase().includes(term);

    return matchesRole && matchesSearch;
  });

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.75rem' }}>
      <div>
        <h1 style={{ fontSize: '1.75rem', marginBottom: '0.25rem', display: 'flex', alignItems: 'center', gap: '10px' }}>
          <Users size={26} style={{ color: 'var(--primary)' }} /> User Directory & Role Management
        </h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
          Manage organizational member identities across distinct functional roles ({users.length} total members).
        </p>
      </div>

      {/* Role Summary KPI Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
        <div
          className="card card-interactive"
          onClick={() => setActiveRoleTab('Employee')}
          style={{
            borderColor: activeRoleTab === 'Employee' ? 'var(--primary)' : 'var(--border-color)',
            background: activeRoleTab === 'Employee' ? 'var(--bg-active)' : 'var(--bg-card)',
          }}
        >
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>
            Employees
          </div>
          <div style={{ fontSize: '1.75rem', fontWeight: 700, fontFamily: 'Outfit', color: 'var(--primary)', marginTop: '4px' }}>
            {roleCounts.Employee}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '2px' }}>
            Proposal authors
          </div>
        </div>

        <div
          className="card card-interactive"
          onClick={() => setActiveRoleTab('Reviewer')}
          style={{
            borderColor: activeRoleTab === 'Reviewer' ? 'var(--info)' : 'var(--border-color)',
            background: activeRoleTab === 'Reviewer' ? 'var(--bg-active)' : 'var(--bg-card)',
          }}
        >
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>
            Reviewers
          </div>
          <div style={{ fontSize: '1.75rem', fontWeight: 700, fontFamily: 'Outfit', color: 'var(--info)', marginTop: '4px' }}>
            {roleCounts.Reviewer}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '2px' }}>
            Technical evaluators
          </div>
        </div>

        <div
          className="card card-interactive"
          onClick={() => setActiveRoleTab('Manager')}
          style={{
            borderColor: activeRoleTab === 'Manager' ? 'var(--warning)' : 'var(--border-color)',
            background: activeRoleTab === 'Manager' ? 'var(--bg-active)' : 'var(--bg-card)',
          }}
        >
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>
            Managers
          </div>
          <div style={{ fontSize: '1.75rem', fontWeight: 700, fontFamily: 'Outfit', color: 'var(--warning)', marginTop: '4px' }}>
            {roleCounts.Manager}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '2px' }}>
            Approval authorities
          </div>
        </div>

        <div
          className="card card-interactive"
          onClick={() => setActiveRoleTab('Administrator')}
          style={{
            borderColor: activeRoleTab === 'Administrator' ? 'var(--purple)' : 'var(--border-color)',
            background: activeRoleTab === 'Administrator' ? 'var(--bg-active)' : 'var(--bg-card)',
          }}
        >
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>
            Administrators
          </div>
          <div style={{ fontSize: '1.75rem', fontWeight: 700, fontFamily: 'Outfit', color: 'var(--purple)', marginTop: '4px' }}>
            {roleCounts.Administrator}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '2px' }}>
            System governance
          </div>
        </div>
      </div>

      {/* Role Navigation Tabs & Search */}
      <div className="card" style={{ padding: '1rem 1.25rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
          <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
            {['ALL', 'Employee', 'Reviewer', 'Manager', 'Administrator'].map((r) => (
              <button
                key={r}
                onClick={() => setActiveRoleTab(r)}
                className={`btn btn-sm ${activeRoleTab === r ? 'btn-primary' : 'btn-secondary'}`}
              >
                {r === 'ALL' ? 'All Roles' : `${r}s`}
              </button>
            ))}
          </div>

          <div style={{ position: 'relative', minWidth: '240px' }}>
            <Search size={16} style={{ position: 'absolute', left: '10px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
            <input
              type="text"
              className="form-input"
              style={{ paddingLeft: '2rem', height: '36px', fontSize: '0.85rem' }}
              placeholder="Search by name, email, department..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
        </div>
      </div>

      {/* Users Table */}
      {loading ? (
        <LoadingSpinner message="Loading user directory..." />
      ) : filteredUsers.length === 0 ? (
        <EmptyState
          title={`No ${activeRoleTab === 'ALL' ? '' : activeRoleTab} users found`}
          description="Try clearing search filters or select another role category."
        />
      ) : (
        <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
          <div className="table-container" style={{ border: 'none', borderRadius: 0 }}>
            <table className="table">
              <thead>
                <tr>
                  <th>User Details</th>
                  <th>Role</th>
                  <th>Department</th>
                  <th>Designation</th>
                  <th>Employee ID</th>
                  <th>Organization</th>
                </tr>
              </thead>
              <tbody>
                {filteredUsers.map((u) => (
                  <tr key={u.id}>
                    <td>
                      <div style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{u.full_name}</div>
                      <div style={{ fontSize: '0.775rem', color: 'var(--text-muted)' }}>{u.email}</div>
                    </td>
                    <td><RoleBadge role={u.role} /></td>
                    <td>{u.department || '—'}</td>
                    <td>{u.designation || '—'}</td>
                    <td><code style={{ fontSize: '0.8rem' }}>{u.employee_id || '—'}</code></td>
                    <td>
                      <span style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', fontSize: '0.85rem' }}>
                        <Building size={14} style={{ color: 'var(--primary)', flexShrink: 0 }} />
                        {orgMap[u.organization_id] || (u.organization_id ? `Org #${u.organization_id}` : '—')}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
