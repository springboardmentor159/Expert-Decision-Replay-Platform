import React, { useState, useEffect } from 'react';
import { userService, authService } from '../../api/authService';
import { Card } from '../../components/common/Card';
import { Button } from '../../components/common/Button';
import { Input, Select } from '../../components/common/Input';
import { Modal } from '../../components/common/Modal';
import { RoleBadge } from '../../components/common/Badge';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import { EmptyState } from '../../components/common/EmptyState';
import { useToast } from '../../context/ToastContext';
import { useAuth } from '../../context/AuthContext';
import { Users, UserPlus, Edit, Trash2, Shield, Lock } from 'lucide-react';

export const UserManagementPage = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);

  const [formData, setFormData] = useState({
    full_name: '',
    email: '',
    password: '',
    role: 'Employee',
    department: 'Engineering',
    designation: 'Software Engineer',
    employee_id: '',
    phone_number: '',
  });

  const { success, error } = useToast();
  const { user: currentUser } = useAuth();

  const fetchUsers = async () => {
    try {
      setLoading(true);
      const data = await userService.getUsers();
      setUsers(data || []);
    } catch (err) {
      error(err.message || 'Failed to load user directory');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  const handleOpenCreate = () => {
    setIsEditing(false);
    setSelectedUser(null);
    setFormData({
      full_name: '',
      email: '',
      password: '',
      role: 'Employee',
      department: 'Engineering',
      designation: 'Software Engineer',
      employee_id: '',
      phone_number: '',
    });
    setShowModal(true);
  };

  const handleOpenEdit = (user) => {
    setIsEditing(true);
    setSelectedUser(user);
    setFormData({
      full_name: user.full_name || '',
      email: user.email || '',
      password: '',
      role: user.role || 'Employee',
      department: user.department || '',
      designation: user.designation || '',
      employee_id: user.employee_id || '',
      phone_number: user.phone_number || '',
    });
    setShowModal(true);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (isEditing) {
        const payload = {
          full_name: formData.full_name,
          role: formData.role,
          department: formData.department,
          designation: formData.designation,
          phone_number: formData.phone_number,
        };
        if (formData.password) payload.password = formData.password;

        await userService.updateUser(selectedUser.id, payload);
        success(`User ${formData.full_name} updated successfully!`);
      } else {
        await authService.register(formData);
        success(`User ${formData.full_name} registered successfully!`);
      }
      setShowModal(false);
      fetchUsers();
    } catch (err) {
      error(err.message || 'User operation failed');
    }
  };

  const handleDelete = async (user) => {
    if (user.id === currentUser?.id) {
      error('You cannot delete your own logged-in account.');
      return;
    }
    if (!window.confirm(`Delete user ${user.full_name} (${user.email})?`)) return;

    try {
      await userService.deleteUser(user.id);
      success('User deleted successfully.');
      fetchUsers();
    } catch (err) {
      error(err.message || 'Failed to delete user');
    }
  };

  if (currentUser?.role !== 'Administrator') {
    return (
      <EmptyState
        icon={Lock}
        title="403 Forbidden"
        description="Only system administrators can access and manage user tenant accounts."
      />
    );
  }

  return (
    <div>
      {/* Header */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '1.5rem',
          flexWrap: 'wrap',
          gap: '1rem',
        }}
      >
        <div>
          <h2 style={{ fontSize: '1.75rem', fontWeight: 800, color: '#ffffff' }}>
            User Management & Directory
          </h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.925rem' }}>
            Provision accounts, assign departmental roles, and govern access permissions.
          </p>
        </div>
        <Button variant="primary" icon={UserPlus} onClick={handleOpenCreate}>
          Add New User
        </Button>
      </div>

      {loading ? (
        <LoadingSpinner message="Loading user directory..." />
      ) : (
        <Card>
          <div className="table-container">
            <table className="custom-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Full Name</th>
                  <th>Email</th>
                  <th>Role</th>
                  <th>Department</th>
                  <th>Designation</th>
                  <th style={{ textAlign: 'right' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {users.map((u) => (
                  <tr key={u.id}>
                    <td>#{u.id}</td>
                    <td style={{ fontWeight: 600, color: '#ffffff' }}>{u.full_name}</td>
                    <td>{u.email}</td>
                    <td>
                      <RoleBadge role={u.role} />
                    </td>
                    <td>{u.department || 'General'}</td>
                    <td style={{ color: 'var(--text-secondary)' }}>{u.designation || '-'}</td>
                    <td style={{ textAlign: 'right' }}>
                      <div style={{ display: 'inline-flex', gap: '0.5rem' }}>
                        <Button
                          variant="outline"
                          size="sm"
                          icon={Edit}
                          onClick={() => handleOpenEdit(u)}
                        />
                        <Button
                          variant="danger"
                          size="sm"
                          icon={Trash2}
                          disabled={u.id === currentUser?.id}
                          onClick={() => handleDelete(u)}
                        />
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}

      {/* User Create/Edit Modal */}
      <Modal
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        title={isEditing ? `Edit User #${selectedUser?.id}` : 'Create New User Account'}
      >
        <form onSubmit={handleSubmit}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <Input
              label="Full Name"
              value={formData.full_name}
              onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
              required
            />
            <Input
              label="Email"
              type="email"
              value={formData.email}
              disabled={isEditing}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              required
            />
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <Input
              label={isEditing ? 'New Password (leave blank to keep)' : 'Password'}
              type="password"
              placeholder={isEditing ? '••••••••' : 'Password123!'}
              value={formData.password}
              onChange={(e) => setFormData({ ...formData, password: e.target.value })}
              required={!isEditing}
            />

            <Select
              label="Role"
              value={formData.role}
              onChange={(e) => setFormData({ ...formData, role: e.target.value })}
              options={[
                { value: 'Employee', label: 'Employee' },
                { value: 'Reviewer', label: 'Reviewer' },
                { value: 'Manager', label: 'Manager' },
                { value: 'Administrator', label: 'Administrator' },
              ]}
              required
            />
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <Input
              label="Department"
              value={formData.department}
              onChange={(e) => setFormData({ ...formData, department: e.target.value })}
            />
            <Input
              label="Designation"
              value={formData.designation}
              onChange={(e) => setFormData({ ...formData, designation: e.target.value })}
            />
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '1.25rem' }}>
            <Button variant="secondary" onClick={() => setShowModal(false)}>
              Cancel
            </Button>
            <Button type="submit" variant="primary">
              {isEditing ? 'Save Changes' : 'Create User'}
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
