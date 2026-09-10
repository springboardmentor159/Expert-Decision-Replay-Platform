import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { authService } from '../../services/authService';
import { useToast } from '../../components/common/Toast';
import { Layers, ArrowRight, User, Mail, Lock, Building, Briefcase, Phone, BadgeCheck } from 'lucide-react';

export const RegisterPage = () => {
  const navigate = useNavigate();
  const { addToast } = useToast();

  const [formData, setFormData] = useState({
    full_name: '',
    email: '',
    password: '',
    confirm_password: '',
    role: 'Employee',
    employee_id: '',
    department: 'Engineering',
    designation: 'Software Engineer',
    phone_number: '+1-555-0100',
  });

  const [errors, setErrors] = useState({});
  const [serverError, setServerError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const validate = () => {
    const errs = {};

    if (!formData.full_name.trim()) {
      errs.full_name = 'Full Name is required';
    }

    if (!formData.email.trim()) {
      errs.email = 'Email address is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      errs.email = 'Please provide a valid email address';
    }

    if (!formData.password) {
      errs.password = 'Password is required';
    } else if (formData.password.length < 8) {
      errs.password = 'Password must be at least 8 characters long';
    }

    if (formData.password !== formData.confirm_password) {
      errs.confirm_password = 'Passwords do not match';
    }

    if (!formData.employee_id.trim()) {
      errs.employee_id = 'Employee ID is required';
    }

    setErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setServerError('');
    if (!validate()) return;

    setIsSubmitting(true);
    try {
      const payload = {
        full_name: formData.full_name.trim(),
        email: formData.email.trim(),
        password: formData.password,
        role: formData.role,
        employee_id: formData.employee_id.trim(),
        department: formData.department.trim() || undefined,
        designation: formData.designation.trim() || undefined,
        phone_number: formData.phone_number.trim() || undefined,
      };

      await authService.register(payload);
      addToast('Registration successful! Please sign in with your credentials.', 'success');
      navigate('/login');
    } catch (err) {
      setServerError(err.userMessage || 'Registration failed. Please check your inputs.');
    } finally {
      setIsSubmitting(false);
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
        background: 'radial-gradient(circle at top, #ecfdf5 0%, #f0fdf4 35%, #f8fafc 100%)',
      }}
    >
      <div
        style={{
          width: '100%',
          maxWidth: '620px',
          background: '#ffffff',
          border: '1px solid var(--border-subtle)',
          borderRadius: 'var(--radius-lg)',
          boxShadow: '0 20px 35px -10px rgba(16, 185, 129, 0.1), 0 1px 3px rgba(0, 0, 0, 0.05)',
          padding: '2.5rem',
        }}
      >
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <div
            style={{
              width: '48px',
              height: '48px',
              borderRadius: 'var(--radius-md)',
              background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
              display: 'inline-flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'white',
              marginBottom: '1rem',
              boxShadow: '0 4px 16px rgba(16, 185, 129, 0.35)',
            }}
          >
            <Layers size={26} />
          </div>
          <h2 style={{ fontSize: '1.6rem', color: 'var(--text-primary)', fontWeight: 800 }}>
            Create Your Account
          </h2>
          <p className="text-muted" style={{ fontSize: '0.9rem', marginTop: '0.25rem' }}>
            Join the Expert Decision Replay Platform
          </p>
        </div>

        {serverError && (
          <div className="alert alert-error" id="reg-server-error">
            <span>{serverError}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} id="form-register">
          <div className="form-row">
            <div className="form-group">
              <label className="form-label form-label-required" htmlFor="input-reg-name">Full Name</label>
              <input
                id="input-reg-name"
                type="text"
                className="form-input"
                placeholder="Jane Doe"
                value={formData.full_name}
                onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
              />
              {errors.full_name && <span className="form-error" id="error-reg-name">{errors.full_name}</span>}
            </div>

            <div className="form-group">
              <label className="form-label form-label-required" htmlFor="input-reg-email">Work Email</label>
              <input
                id="input-reg-email"
                type="email"
                className="form-input"
                placeholder="jane.doe@organization.com"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              />
              {errors.email && <span className="form-error" id="error-reg-email">{errors.email}</span>}
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label className="form-label form-label-required" htmlFor="input-reg-password">Password</label>
              <input
                id="input-reg-password"
                type="password"
                className="form-input"
                placeholder="Min. 8 characters"
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
              />
              {errors.password && <span className="form-error" id="error-reg-password">{errors.password}</span>}
            </div>

            <div className="form-group">
              <label className="form-label form-label-required" htmlFor="input-reg-confirm-password">Confirm Password</label>
              <input
                id="input-reg-confirm-password"
                type="password"
                className="form-input"
                placeholder="Re-enter password"
                value={formData.confirm_password}
                onChange={(e) => setFormData({ ...formData, confirm_password: e.target.value })}
              />
              {errors.confirm_password && (
                <span className="form-error" id="error-reg-confirm-password">{errors.confirm_password}</span>
              )}
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label className="form-label form-label-required" htmlFor="select-reg-role">Assigned Role</label>
              <select
                id="select-reg-role"
                className="form-select"
                value={formData.role}
                onChange={(e) => setFormData({ ...formData, role: e.target.value })}
              >
                <option value="Employee">Employee (Create & Explore)</option>
                <option value="Reviewer">Reviewer (Evaluate & Review)</option>
                <option value="Manager">Manager (Team Decisions & Approvals)</option>
                <option value="Administrator">Administrator (System & Audit Controls)</option>
              </select>
            </div>

            <div className="form-group">
              <label className="form-label form-label-required" htmlFor="input-reg-employee-id">Employee ID</label>
              <input
                id="input-reg-employee-id"
                type="text"
                className="form-input"
                placeholder="EMP-1042"
                value={formData.employee_id}
                onChange={(e) => setFormData({ ...formData, employee_id: e.target.value })}
              />
              {errors.employee_id && <span className="form-error" id="error-reg-employee-id">{errors.employee_id}</span>}
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label className="form-label" htmlFor="input-reg-department">Department</label>
              <input
                id="input-reg-department"
                type="text"
                className="form-input"
                placeholder="Platform Engineering"
                value={formData.department}
                onChange={(e) => setFormData({ ...formData, department: e.target.value })}
              />
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="input-reg-designation">Designation</label>
              <input
                id="input-reg-designation"
                type="text"
                className="form-input"
                placeholder="Senior Architect"
                value={formData.designation}
                onChange={(e) => setFormData({ ...formData, designation: e.target.value })}
              />
            </div>
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="input-reg-phone">Phone Number</label>
            <input
              id="input-reg-phone"
              type="text"
              className="form-input"
              placeholder="+1-555-0199"
              value={formData.phone_number}
              onChange={(e) => setFormData({ ...formData, phone_number: e.target.value })}
            />
          </div>

          <button
            id="btn-reg-submit"
            type="submit"
            className="btn btn-primary btn-lg"
            style={{ width: '100%', marginTop: '0.75rem' }}
            disabled={isSubmitting}
          >
            {isSubmitting ? 'Creating Account...' : 'Complete Registration'}
            <ArrowRight size={18} />
          </button>
        </form>

        <div style={{ textAlign: 'center', marginTop: '1.5rem', fontSize: '0.88rem' }}>
          <span className="text-muted">Already registered? </span>
          <Link to="/login" id="link-login" style={{ fontWeight: 600 }}>
            Sign In here
          </Link>
        </div>
      </div>
    </div>
  );
};
