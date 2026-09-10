import React, { useState, useEffect } from 'react';
import { authService } from '../../services/authService';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import { EmptyState } from '../../components/common/EmptyState';
import { Modal } from '../../components/common/Modal';
import { RoleBadge } from '../../components/common/StatusBadge';
import { useAuth } from '../../context/AuthContext';
import { useToast } from '../../components/common/Toast';
import { Users, UserPlus, Trash2, Edit, Shield, Mail, Building } from 'lucide-react';

export const UserManagementPage = () => {
  const { user, isAdmin } = useAuth();
  const { addToast } = useToast();

  const [users, setUsers] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  // Create/Edit User Modal
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingUser, setEditingUser] = useState(null);
  const [formData, setFormData] = useState({
    full_name: '',
    email: '',
    password: '',
    role: 'Employee',
    employee_id: '',
    department: 'Engineering',
    designation: 'Engineer',
  });
  const [modalErrors, setModalErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const fetchUsers = async () => {
    setIsLoading(true);
    setError('');
    try {
      const data = await authService.getUsers();
      setUsers(data);
    } catch (err) {
      setError(err.userMessage || 'Failed to load user directory');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  const openCreateModal = () => {
    setEditingUser(null);
    setFormData({
      full_name: '',
      email: '',
      password: '',
      role: 'Employee',
      employee_id: `EMP-${Math.floor(1000 + Math.random() * 9000)}`,
      department: 'Engineering',
      designation: 'Engineer',
    });
    setModalErrors({});
    setIsModalOpen(true);
  };

  const openEditModal = (u) => {
    setEditingUser(u);
    setFormData({
      full_name: u.full_name || '',
      email: u.email || '',
      password: '', // optional on edit
      role: u.role || 'Employee',
      employee_id: u.employee_id || '',
      department: u.department || '',
      designation: u.designation || '',
    });
    setModalErrors({});
    setIsModalOpen(true);
  };

  const validateModal = () => {
    const errs = {};
    if (!formData.full_name.trim()) errs.full_name = 'Name is required';
    if (!formData.email.trim()) errs.email = 'Email is required';
    if (!editingUser && !formData.password) errs.password = 'Password is required';
    setModalErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const handleSaveUser = async (e) => {
    e.preventDefault();
    if (!validateModal()) return;

    setIsSubmitting(true);
    try {
      if (editingUser) {
        const payload = {
          full_name: formData.full_name.trim(),
          role: formData.role,
          department: formData.department.trim(),
          designation: formData.designation.trim(),
        };
        if (formData.password) payload.password = formData.password;
        await authService.updateUser(editingUser.id, payload);
        addToast('User updated successfully', 'success');
      } else {
        await authService.register({
          full_name: formData.full_name.trim(),
          email: formData.email.trim(),
          password: formData.password,
          role: formData.role,
          employee_id: formData.employee_id.trim(),
          department: formData.department.trim(),
          designation: formData.designation.trim(),
        });
        addToast('User created successfully', 'success');
      }
      setIsModalOpen(false);
      fetchUsers();
    } catch (err) {
      addToast(err.userMessage || 'Failed to save user', 'error');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDeleteUser = async (uId, uName) => {
    if (uId === user?.id) {
      addToast('You cannot delete your own account', 'error');
      return;
    }
    if (!window.confirm(`Are you sure you want to delete user "${uName}"?`)) return;

    try {
      await authService.deleteUser(uId);
      addToast('User deleted successfully', 'success');
      fetchUsers();
    } catch (err) {
      addToast(err.userMessage || 'Failed to delete user', 'error');
    }
  };

  if (!isAdmin) {
    return (
      <div style={{ margin: '3rem auto', maxWidth: '500px', textAlign: 'center' }}>
        <div className="alert alert-error">
          <span>Access Denied: Only Administrators are authorized to manage user accounts.</span>
        </div>
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.75rem' }}>
      {/* Top Header */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '1rem',
        }}
      >
        <div>
          <h1 className="page-title">
            <Users size={28} />
            Personnel Directory & Access Control
          </h1>
          <p className="page-description">
            Manage organizational roles, onboard new reviewers and managers, and enforce access permissions.
          </p>
        </div>

        <button className="btn btn-primary" onClick={openCreateModal}>
          <UserPlus size={18} />
          <span>Add New User</span>
        </button>
      </div>

      {isLoading ? (
        <LoadingSpinner message="Loading user directory..." />
      ) : error ? (
        <div className="alert alert-error">
          <span>{error}</span>
        </div>
      ) : users.length === 0 ? (
        <EmptyState title="No users found" description="The directory is currently empty." />
      ) : (
        <div className="table-container">
          <table className="table">
            <thead>
              <tr>
                <th>Personnel</th>
                <th>Role</th>
                <th>Employee ID</th>
                <th>Department</th>
                <th>Designation</th>
                <th style={{ textAlign: 'right' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {users.map((u) => (
                <tr key={u.id}>
                  <td>
                    <div className="table-cell-title">{u.full_name}</div>
                    <span className="text-dim" style={{ fontSize: '0.8rem' }}>{u.email}</span>
                  </td>
                  <td>
                    <RoleBadge role={u.role} />
                  </td>
                  <td className="font-mono" style={{ fontSize: '0.82rem' }}>
                    {u.employee_id || '—'}
                  </td>
                  <td>{u.department || 'General'}</td>
                  <td>{u.designation || '—'}</td>
                  <td style={{ textAlign: 'right' }}>
                    <div style={{ display: 'inline-flex', gap: '0.5rem' }}>
                      <button
                        className="btn btn-secondary btn-sm"
                        onClick={() => openEditModal(u)}
                        title="Edit User"
                      >
                        <Edit size={14} />
                      </button>
                      <button
                        className="btn btn-secondary btn-sm"
                        onClick={() => handleDeleteUser(u.id, u.full_name)}
                        style={{ color: '#f87171' }}
                        title="Delete User"
                        disabled={u.id === user?.id}
                      >
                        <Trash2 size={14} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* User Create / Edit Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title={editingUser ? `Edit ${editingUser.full_name}` : 'Create New Personnel'}
        size="md"
        footer={
          <>
            <button className="btn btn-secondary" onClick={() => setIsModalOpen(false)}>
              Cancel
            </button>
            <button className="btn btn-primary" onClick={handleSaveUser} disabled={isSubmitting}>
              {isSubmitting ? 'Saving...' : editingUser ? 'Update User' : 'Create User'}
            </button>
          </>
        }
      >
        <form onSubmit={handleSaveUser}>
          <div className="form-group">
            <label className="form-label form-label-required">Full Name</label>
            <input
              type="text"
              className="form-input"
              value={formData.full_name}
              onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
              required
            />
            {modalErrors.full_name && <span className="form-error">{modalErrors.full_name}</span>}
          </div>

          <div className="form-group">
            <label className="form-label form-label-required">Work Email</label>
            <input
              type="email"
              className="form-input"
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              disabled={!!editingUser}
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">
              {editingUser ? 'New Password (leave empty to keep current)' : 'Initial Password'}
            </label>
            <input
              type="password"
              className="form-input"
              value={formData.password}
              onChange={(e) => setFormData({ ...formData, password: e.target.value })}
              placeholder={editingUser ? '••••••••' : 'Min. 8 characters'}
            />
            {modalErrors.password && <span className="form-error">{modalErrors.password}</span>}
          </div>

          <div className="form-group">
            <label className="form-label form-label-required">Role Permission</label>
            <select
              className="form-select"
              value={formData.role}
              onChange={(e) => setFormData({ ...formData, role: e.target.value })}
            >
              <option value="Employee">Employee</option>
              <option value="Reviewer">Reviewer</option>
              <option value="Manager">Manager</option>
              <option value="Administrator">Administrator</option>
            </select>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label className="form-label">Department</label>
              <input
                type="text"
                className="form-input"
                value={formData.department}
                onChange={(e) => setFormData({ ...formData, department: e.target.value })}
              />
            </div>
            <div className="form-group">
              <label className="form-label">Designation</label>
              <input
                type="text"
                className="form-input"
                value={formData.designation}
                onChange={(e) => setFormData({ ...formData, designation: e.target.value })}
              />
            </div>
          </div>
        </form>
      </Modal>
    </div>
  );
};
