import React, { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { Input, Select } from '../../components/common/Input';
import { Button } from '../../components/common/Button';
import { Card } from '../../components/common/Card';
import { UserPlus, Sparkles, ArrowLeft } from 'lucide-react';

export const RegisterPage = ({ onNavigateToLogin }) => {
  const { register } = useAuth();
  const [formData, setFormData] = useState({
    full_name: '',
    email: '',
    password: '',
    confirm_password: '',
    role: 'Employee',
    department: 'Engineering',
    designation: 'Software Engineer',
    employee_id: '',
    phone_number: '',
  });

  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});

  const validate = () => {
    const errs = {};
    if (!formData.full_name.trim()) errs.full_name = 'Full name is required.';
    if (!formData.email.trim()) errs.email = 'Email is required.';
    else if (!/\S+@\S+\.\S+/.test(formData.email)) errs.email = 'Please enter a valid email address.';

    if (!formData.password) errs.password = 'Password is required.';
    else if (formData.password.length < 6) errs.password = 'Password must be at least 6 characters.';

    if (formData.password !== formData.confirm_password) {
      errs.confirm_password = 'Passwords do not match.';
    }

    setErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const handleChange = (field, value) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors((prev) => ({ ...prev, [field]: null }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validate()) return;

    setLoading(true);
    try {
      const payload = {
        full_name: formData.full_name.trim(),
        email: formData.email.trim(),
        password: formData.password,
        role: formData.role,
        department: formData.department || null,
        designation: formData.designation || null,
        employee_id: formData.employee_id.trim() || `EMP-${Math.floor(1000 + Math.random() * 9000)}`,
        phone_number: formData.phone_number || null,
      };

      await register(payload);
      onNavigateToLogin();
    } catch {
      // Handled in AuthContext
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '2.5rem 1rem',
        position: 'relative',
        zIndex: 1,
      }}
    >
      <div style={{ maxWidth: '540px', width: '100%' }}>
        {/* Brand Header */}
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <div
            style={{
              width: '56px',
              height: '56px',
              borderRadius: 'var(--radius-lg)',
              background: 'linear-gradient(135deg, var(--accent-blue), var(--accent-indigo))',
              display: 'inline-flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#ffffff',
              boxShadow: 'var(--shadow-glow-blue)',
              marginBottom: '1rem',
            }}
          >
            <Sparkles size={30} />
          </div>
          <h1 style={{ fontSize: '1.85rem', fontWeight: 800, color: '#ffffff', letterSpacing: '-0.02em' }}>
            Create Account
          </h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.925rem', marginTop: '0.25rem' }}>
            Register to participate in enterprise decision analysis and workflows
          </p>
        </div>

        <Card>
          <form onSubmit={handleSubmit}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
              <Input
                id="reg-fullname"
                label="Full Name"
                placeholder="Jane Doe"
                value={formData.full_name}
                onChange={(e) => handleChange('full_name', e.target.value)}
                error={errors.full_name}
                required
              />

              <Input
                id="reg-email"
                label="Work Email"
                type="email"
                placeholder="jane.doe@example.com"
                value={formData.email}
                onChange={(e) => handleChange('email', e.target.value)}
                error={errors.email}
                required
              />
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
              <Input
                id="reg-password"
                label="Password"
                type="password"
                placeholder="••••••••"
                value={formData.password}
                onChange={(e) => handleChange('password', e.target.value)}
                error={errors.password}
                required
              />

              <Input
                id="reg-confirm"
                label="Confirm Password"
                type="password"
                placeholder="••••••••"
                value={formData.confirm_password}
                onChange={(e) => handleChange('confirm_password', e.target.value)}
                error={errors.confirm_password}
                required
              />
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
              <Select
                id="reg-role"
                label="Select Role"
                value={formData.role}
                onChange={(e) => handleChange('role', e.target.value)}
                options={[
                  { value: 'Employee', label: 'Employee' },
                  { value: 'Reviewer', label: 'Reviewer' },
                  { value: 'Manager', label: 'Manager' },
                  { value: 'Administrator', label: 'Administrator' },
                ]}
                required
              />

              <Input
                id="reg-department"
                label="Department"
                placeholder="e.g. Engineering, Product"
                value={formData.department}
                onChange={(e) => handleChange('department', e.target.value)}
              />
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
              <Input
                id="reg-designation"
                label="Designation / Title"
                placeholder="e.g. Lead Architect"
                value={formData.designation}
                onChange={(e) => handleChange('designation', e.target.value)}
              />

              <Input
                id="reg-empid"
                label="Employee ID (Optional)"
                placeholder="EMP-1234"
                value={formData.employee_id}
                onChange={(e) => handleChange('employee_id', e.target.value)}
              />
            </div>

            <Button
              type="submit"
              variant="primary"
              loading={loading}
              icon={UserPlus}
              style={{ width: '100%', marginTop: '1rem' }}
            >
              Complete Registration
            </Button>
          </form>

          <div style={{ textAlign: 'center', marginTop: '1.5rem', fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
            Already have an account?{' '}
            <button
              type="button"
              onClick={onNavigateToLogin}
              style={{
                background: 'transparent',
                border: 'none',
                color: 'var(--accent-blue)',
                fontWeight: 600,
                cursor: 'pointer',
                textDecoration: 'underline',
              }}
            >
              Sign In
            </button>
          </div>
        </Card>
      </div>
    </div>
  );
};
