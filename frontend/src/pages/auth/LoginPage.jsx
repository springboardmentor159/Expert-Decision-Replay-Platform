import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { useToast } from '../../components/common/Toast';
import { Layers, Mail, Lock, ArrowRight, ShieldCheck, CheckCircle2, UserCheck } from 'lucide-react';

export const LoginPage = () => {
  const { login, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const { addToast } = useToast();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [errors, setErrors] = useState({});
  const [serverError, setServerError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Check if redirected due to expired token
  useEffect(() => {
    const params = new URLSearchParams(location.search);
    if (params.get('expired')) {
      setServerError('Your session has expired. Please log in again.');
    }
  }, [location]);

  // If already authenticated, redirect to dashboard
  useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard');
    }
  }, [isAuthenticated, navigate]);

  const validate = () => {
    const errs = {};
    if (!email.trim()) {
      errs.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(email)) {
      errs.email = 'Please enter a valid email address';
    }
    if (!password) {
      errs.password = 'Password is required';
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
      const data = await login(email.trim(), password);
      addToast(`Welcome back, ${data.user?.full_name || 'User'}!`, 'success');
      navigate('/dashboard');
    } catch (err) {
      setServerError(err.userMessage || 'Invalid email or password.');
    } finally {
      setIsSubmitting(false);
    }
  };

  // Demo user helper to quickly populate credentials
  const handleQuickFill = (demoEmail, demoPassword) => {
    setEmail(demoEmail);
    setPassword(demoPassword);
    setErrors({});
    setServerError('');
  };

  return (
    <div
      style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '2rem',
        background: 'radial-gradient(circle at top, #ecfdf5 0%, #f0fdf4 35%, #f8fafc 100%)',
      }}
    >
      <div
        style={{
          width: '100%',
          maxWidth: '460px',
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
            Sign In to Platform
          </h2>
          <p className="text-muted" style={{ fontSize: '0.9rem', marginTop: '0.25rem' }}>
            Enterprise Decision Replay & Audit System
          </p>
        </div>

        {serverError && (
          <div className="alert alert-error" id="login-server-error">
            <span>{serverError}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} id="form-login">
          <div className="form-group">
            <label className="form-label form-label-required" htmlFor="input-login-email">Email Address</label>
            <div style={{ position: 'relative' }}>
              <input
                id="input-login-email"
                type="email"
                className="form-input"
                placeholder="name@organization.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                style={{ paddingLeft: '2.5rem' }}
              />
              <Mail
                size={18}
                style={{
                  position: 'absolute',
                  left: '0.85rem',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  color: 'var(--text-dim)',
                  pointerEvents: 'none',
                }}
              />
            </div>
            {errors.email && <span className="form-error" id="error-login-email">{errors.email}</span>}
          </div>

          <div className="form-group">
            <label className="form-label form-label-required" htmlFor="input-login-password">Password</label>
            <div style={{ position: 'relative' }}>
              <input
                id="input-login-password"
                type="password"
                className="form-input"
                placeholder="••••••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                style={{ paddingLeft: '2.5rem' }}
              />
              <Lock
                size={18}
                style={{
                  position: 'absolute',
                  left: '0.85rem',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  color: 'var(--text-dim)',
                  pointerEvents: 'none',
                }}
              />
            </div>
            {errors.password && <span className="form-error" id="error-login-password">{errors.password}</span>}
          </div>

          <button
            id="btn-login-submit"
            type="submit"
            className="btn btn-primary btn-lg"
            style={{ width: '100%', marginTop: '0.5rem' }}
            disabled={isSubmitting}
          >
            {isSubmitting ? 'Authenticating...' : 'Sign In'}
            <ArrowRight size={18} />
          </button>
        </form>

        {/* Demo Quick-Fill Roles Box */}
        <div
          style={{
            marginTop: '2rem',
            padding: '1rem',
            background: 'var(--bg-elevated)',
            borderRadius: 'var(--radius-sm)',
            border: '1px solid var(--border-subtle)',
          }}
        >
          <div
            style={{
              fontSize: '0.75rem',
              fontWeight: 700,
              textTransform: 'uppercase',
              letterSpacing: '0.05em',
              color: 'var(--text-muted)',
              marginBottom: '0.75rem',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
            }}
          >
            <UserCheck size={14} color="var(--primary)" /> Quick Demo Account Switcher
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem' }}>
            <button
              id="btn-demo-employee"
              type="button"
              className="btn btn-secondary btn-sm"
              onClick={() => handleQuickFill('master_emp@example.com', 'Password123!')}
              style={{ fontSize: '0.78rem', justifyContent: 'flex-start' }}
            >
              <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#10b981' }}></span>
              Employee
            </button>
            <button
              id="btn-demo-reviewer"
              type="button"
              className="btn btn-secondary btn-sm"
              onClick={() => handleQuickFill('master_rev@example.com', 'Password123!')}
              style={{ fontSize: '0.78rem', justifyContent: 'flex-start' }}
            >
              <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#0d9488' }}></span>
              Reviewer
            </button>
            <button
              id="btn-demo-manager"
              type="button"
              className="btn btn-secondary btn-sm"
              onClick={() => handleQuickFill('master_mgr@example.com', 'Password123!')}
              style={{ fontSize: '0.78rem', justifyContent: 'flex-start' }}
            >
              <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#2563eb' }}></span>
              Manager
            </button>
            <button
              id="btn-demo-admin"
              type="button"
              className="btn btn-secondary btn-sm"
              onClick={() => handleQuickFill('master_adm@example.com', 'Password123!')}
              style={{ fontSize: '0.78rem', justifyContent: 'flex-start' }}
            >
              <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#7c3aed' }}></span>
              Admin
            </button>
          </div>
        </div>

        <div style={{ textAlign: 'center', marginTop: '1.5rem', fontSize: '0.88rem' }}>
          <span className="text-muted">Don't have an account yet? </span>
          <Link to="/register" id="link-register" style={{ fontWeight: 600 }}>
            Register here
          </Link>
        </div>
      </div>
    </div>
  );
};
