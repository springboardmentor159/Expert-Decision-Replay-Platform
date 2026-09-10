import React, { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { Input } from '../../components/common/Input';
import { Button } from '../../components/common/Button';
import { Card } from '../../components/common/Card';
import { Sparkles, LogIn, UserCheck, Shield, Award, Briefcase } from 'lucide-react';

export const LoginPage = ({ onNavigateToRegister }) => {
  const { login } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});

  const validate = () => {
    const errs = {};
    if (!email.trim()) errs.email = 'Email address is required.';
    else if (!/\S+@\S+\.\S+/.test(email)) errs.email = 'Please enter a valid email address.';

    if (!password) errs.password = 'Password is required.';
    else if (password.length < 6) errs.password = 'Password must be at least 6 characters.';

    setErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validate()) return;

    setLoading(true);
    try {
      await login(email.trim(), password);
    } catch {
      // Error handled in AuthContext with toast
    } finally {
      setLoading(false);
    }
  };

  // Quick-fill helper for demo accounts
  const quickFill = (demoEmail, demoPassword) => {
    setEmail(demoEmail);
    setPassword(demoPassword);
    setErrors({});
  };

  return (
    <div
      style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '2rem 1rem',
        position: 'relative',
        zIndex: 1,
      }}
    >
      <div style={{ maxWidth: '440px', width: '100%' }}>
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
            Expert Decision Replay
          </h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.925rem', marginTop: '0.25rem' }}>
            Sign in to access your role-based decision workspace
          </p>
        </div>

        {/* Login Card */}
        <Card>
          <form onSubmit={handleSubmit}>
            <Input
              id="login-email"
              label="Email Address"
              type="email"
              placeholder="user@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              error={errors.email}
              required
            />

            <Input
              id="login-password"
              label="Password"
              type="password"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              error={errors.password}
              required
            />

            <Button
              type="submit"
              variant="primary"
              loading={loading}
              icon={LogIn}
              style={{ width: '100%', marginTop: '0.75rem' }}
            >
              Sign In
            </Button>
          </form>

          {/* Quick Demo Fill Buttons */}
          <div
            style={{
              marginTop: '1.75rem',
              paddingTop: '1.25rem',
              borderTop: '1px solid var(--border-subtle)',
            }}
          >
            <span
              style={{
                display: 'block',
                fontSize: '0.75rem',
                textTransform: 'uppercase',
                color: 'var(--text-muted)',
                fontWeight: 700,
                letterSpacing: '0.05em',
                marginBottom: '0.75rem',
                textAlign: 'center',
              }}
            >
              Quick-Fill Demo Roles (Click to autofill)
            </span>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem' }}>
              <button
                type="button"
                className="btn btn-outline btn-sm"
                onClick={() => quickFill('employee@example.com', 'Password123!')}
              >
                <Briefcase size={14} color="#3b82f6" /> Employee
              </button>
              <button
                type="button"
                className="btn btn-outline btn-sm"
                onClick={() => quickFill('reviewer@example.com', 'Password123!')}
              >
                <UserCheck size={14} color="#06b6d4" /> Reviewer
              </button>
              <button
                type="button"
                className="btn btn-outline btn-sm"
                onClick={() => quickFill('manager@example.com', 'Password123!')}
              >
                <Award size={14} color="#f59e0b" /> Manager
              </button>
              <button
                type="button"
                className="btn btn-outline btn-sm"
                onClick={() => quickFill('admin@example.com', 'Password123!')}
              >
                <Shield size={14} color="#10b981" /> Administrator
              </button>
            </div>
          </div>

          {/* Switch to Register */}
          <div style={{ textAlign: 'center', marginTop: '1.5rem', fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
            Don't have an account?{' '}
            <button
              type="button"
              onClick={onNavigateToRegister}
              style={{
                background: 'transparent',
                border: 'none',
                color: 'var(--accent-blue)',
                fontWeight: 600,
                cursor: 'pointer',
                textDecoration: 'underline',
              }}
            >
              Create an account
            </button>
          </div>
        </Card>
      </div>
    </div>
  );
};
