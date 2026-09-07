import React, { useState, useEffect } from 'react';
import { Users, Plus, Shield, Mail, Building, Briefcase } from 'lucide-react';
import { usersApi } from '../../api/users';
import { useAuth } from '../../context/AuthContext';
import { useNotification } from '../../context/NotificationContext';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import { RoleBadge } from '../../components/common/StatusBadge';
import { EmptyState } from '../../components/common/EmptyState';

export function UserManagementPage() {
  const { isAdmin } = useAuth();
  const { error } = useNotification();
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadUsers() {
      setLoading(true);
      try {
        const list = await usersApi.getUsers();
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

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      <div>
        <h1 style={{ fontSize: '1.75rem', marginBottom: '0.25rem', display: 'flex', alignItems: 'center', gap: '10px' }}>
          <Users size={26} style={{ color: 'var(--primary)' }} /> User Directory & Governance Access
        </h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
          Manage organizational member identities, roles, and functional permissions ({users.length} total members).
        </p>
      </div>

      {loading ? (
        <LoadingSpinner message="Loading user directory..." />
      ) : users.length === 0 ? (
        <EmptyState title="No users found" />
      ) : (
        <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
          <div className="table-container" style={{ border: 'none', borderRadius: 0 }}>
            <table className="table">
              <thead>
                <tr>
                  <th>User</th>
                  <th>Role</th>
                  <th>Department</th>
                  <th>Designation</th>
                  <th>Employee ID</th>
                  <th>Organization ID</th>
                </tr>
              </thead>
              <tbody>
                {users.map((u) => (
                  <tr key={u.id}>
                    <td>
                      <div style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{u.full_name}</div>
                      <div style={{ fontSize: '0.775rem', color: 'var(--text-muted)' }}>{u.email}</div>
                    </td>
                    <td><RoleBadge role={u.role} /></td>
                    <td>{u.department || '—'}</td>
                    <td>{u.designation || '—'}</td>
                    <td><code style={{ fontSize: '0.8rem' }}>{u.employee_id || '—'}</code></td>
                    <td>Org #{u.organization_id}</td>
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
