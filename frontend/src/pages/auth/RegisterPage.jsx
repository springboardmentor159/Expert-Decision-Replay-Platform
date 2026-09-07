import React, { useState, useEffect } from 'react';
import { User, Mail, Lock, Building, Briefcase, Phone, ArrowLeft, ArrowRight, ShieldCheck } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { organizationsApi } from '../../api/organizations';
import { ThemeToggle } from '../../components/layout/ThemeToggle';

export function RegisterPage({ onNavigateLogin }) {
  const { register } = useAuth();
  const [organizations, setOrganizations] = useState([]);
  const [formData, setFormData] = useState({
    full_name: '',
    email: '',
    password: '',
    confirmPassword: '',
    role: 'Employee',
    organization_id: 1,
    department: 'Engineering',
    designation: 'Software Engineer',
    phone_number: '+1-555-0100',
    employee_id: `EMP-${Math.floor(1000 + Math.random() * 9000)}`,
  });
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});

  useEffect(() => {
    async function loadOrgs() {
      try {
        const list = await organizationsApi.getPublicList();
        if (list && list.length > 0) {
          setOrganizations(list);
          setFormData((prev) => ({ ...prev, organization_id: list[0].id }));
        }
      } catch {
        // Fallback default
        setOrganizations([{ id: 1, name: 'Default Organization' }]);
      }
    }
    loadOrgs();
  }, []);

  const handleChange = (field, value) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors((prev) => ({ ...prev, [field]: '' }));
    }
  };

  const validate = () => {
    const errs = {};
    if (!formData.full_name.trim()) errs.full_name = 'Full name is required';
    if (!formData.email.trim()) {
      errs.email = 'Email is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email.trim())) {
      errs.email = 'Invalid email address format';
    }
    if (!formData.password) {
      errs.password = 'Password is required';
    } else if (formData.password.length < 8) {
      errs.password = 'Password must be at least 8 characters long';
    }
    if (formData.password !== formData.confirmPassword) {
      errs.confirmPassword = 'Passwords do not match';
    }
    if (!formData.organization_id) {
      errs.organization_id = 'Please select an organization';
    }
    setErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validate()) return;

    try {
      setLoading(true);
      const payload = {
        full_name: formData.full_name.trim(),
        email: formData.email.trim(),
        password: formData.password,
        role: formData.role,
        organization_id: Number(formData.organization_id),
        department: formData.department,
        designation: formData.designation,
        phone_number: formData.phone_number,
        employee_id: formData.employee_id,
      };

      await register(payload);
      onNavigateLogin();
    } catch (err) {
      setErrors({ global: err.message || 'Registration failed' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      flexDirection: 'column',
      background: 'radial-gradient(ellipse at top, rgba(99, 102, 241, 0.15), transparent 70%), var(--bg-app)',
    }}>
      <header style={{
        padding: '1.25rem 2rem',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
          <div style={{
            width: '36px',
            height: '36px',
            borderRadius: '10px',
            background: 'linear-gradient(135deg, var(--primary), var(--purple))',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#fff',
            fontWeight: 800,
          }}>
            ED
          </div>
          <span style={{ fontFamily: 'Outfit', fontWeight: 700, fontSize: '1.15rem' }}>
            Expert Decision Replay
          </span>
        </div>
        <ThemeToggle />
      </header>

      <div style={{
        flex: 1,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '2rem 1.5rem',
      }}>
        <div className="card" style={{ maxWidth: '640px', width: '100%', padding: '2.5rem' }}>
          <button
            type="button"
            className="btn btn-secondary btn-sm"
            onClick={onNavigateLogin}
            style={{ marginBottom: '1.5rem' }}
          >
            <ArrowLeft size={16} /> Back to Sign In
          </button>

          <div style={{ marginBottom: '2rem' }}>
            <h1 style={{ fontSize: '1.75rem', marginBottom: '0.5rem' }}>Create an Account</h1>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
              Join your organization's decision governance platform
            </p>
          </div>

          {errors.global && (
            <div style={{
              background: 'var(--danger-light)',
              border: '1px solid var(--danger)',
              borderRadius: '8px',
              padding: '0.75rem 1rem',
              color: 'var(--danger)',
              fontSize: '0.875rem',
              marginBottom: '1.25rem',
            }}>
              {errors.global}
            </div>
          )}

          <form onSubmit={handleSubmit}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
              <div className="form-group">
                <label className="form-label">Full Name *</label>
                <input
                  type="text"
                  className="form-input"
                  placeholder="e.g. John Doe"
                  value={formData.full_name}
                  onChange={(e) => handleChange('full_name', e.target.value)}
                  disabled={loading}
                />
                {errors.full_name && <div className="form-error">{errors.full_name}</div>}
              </div>

              <div className="form-group">
                <label className="form-label">Email Address *</label>
                <input
                  type="email"
                  className="form-input"
                  placeholder="e.g. john@organization.com"
                  value={formData.email}
                  onChange={(e) => handleChange('email', e.target.value)}
                  disabled={loading}
                />
                {errors.email && <div className="form-error">{errors.email}</div>}
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
              <div className="form-group">
                <label className="form-label">Password *</label>
                <input
                  type="password"
                  className="form-input"
                  placeholder="Min 8 characters"
                  value={formData.password}
                  onChange={(e) => handleChange('password', e.target.value)}
                  disabled={loading}
                />
                {errors.password && <div className="form-error">{errors.password}</div>}
              </div>

              <div className="form-group">
                <label className="form-label">Confirm Password *</label>
                <input
                  type="password"
                  className="form-input"
                  placeholder="Repeat password"
                  value={formData.confirmPassword}
                  onChange={(e) => handleChange('confirmPassword', e.target.value)}
                  disabled={loading}
                />
                {errors.confirmPassword && <div className="form-error">{errors.confirmPassword}</div>}
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
              <div className="form-group">
                <label className="form-label">Role *</label>
                <select
                  className="form-select"
                  value={formData.role}
                  onChange={(e) => handleChange('role', e.target.value)}
                  disabled={loading}
                >
                  <option value="Employee">Employee</option>
                  <option value="Reviewer">Reviewer</option>
                  <option value="Manager">Manager</option>
                  <option value="Administrator">Administrator</option>
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Organization *</label>
                <select
                  className="form-select"
                  value={formData.organization_id}
                  onChange={(e) => handleChange('organization_id', e.target.value)}
                  disabled={loading}
                >
                  {organizations.map((org) => (
                    <option key={org.id} value={org.id}>
                      {org.name}
                    </option>
                  ))}
                </select>
                {errors.organization_id && <div className="form-error">{errors.organization_id}</div>}
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
              <div className="form-group">
                <label className="form-label">Department</label>
                <input
                  type="text"
                  className="form-input"
                  placeholder="e.g. Engineering, Operations"
                  value={formData.department}
                  onChange={(e) => handleChange('department', e.target.value)}
                  disabled={loading}
                />
              </div>

              <div className="form-group">
                <label className="form-label">Designation</label>
                <input
                  type="text"
                  className="form-input"
                  placeholder="e.g. Tech Lead, Analyst"
                  value={formData.designation}
                  onChange={(e) => handleChange('designation', e.target.value)}
                  disabled={loading}
                />
              </div>
            </div>

            <button
              type="submit"
              className="btn btn-primary"
              style={{ width: '100%', marginTop: '1rem', padding: '0.75rem' }}
              disabled={loading}
            >
              {loading ? <span className="spinner" /> : <>Create Account <ArrowRight size={18} /></>}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
