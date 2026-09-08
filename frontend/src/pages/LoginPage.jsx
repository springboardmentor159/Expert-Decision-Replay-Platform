import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Lock, Mail, Layers, ArrowRight, ShieldCheck, UserCheck } from 'lucide-react';
import { useAuth, UserRole } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import Button from '../components/common/Button';
import Input from '../components/common/Input';
import FormField from '../components/common/FormField';
import Alert from '../components/common/Alert';

export const LoginPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [errors, setErrors] = useState({});
  const [apiError, setApiError] = useState('');
  const [loading, setLoading] = useState(false);

  const { login } = useAuth();
  const toast = useToast();
  const navigate = useNavigate();
  const location = useLocation();

  const redirectPath = new URLSearchParams(location.search).get('redirect') || '/dashboard';

  const validate = () => {
    const errs = {};
    if (!email) {
      errs.email = 'Email address is required';
    } else if (!/\S+@\S+\.\S+/.test(email)) {
      errs.email = 'Please enter a valid email address';
    }

    if (!password) {
      errs.password = 'Password is required';
    } else if (password.length < 6) {
      errs.password = 'Password must be at least 6 characters';
    }

    setErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const handleSubmit = async (e) => {
    e?.preventDefault();
    setApiError('');

    if (!validate()) return;

    setLoading(true);
    const result = await login(email, password);
    setLoading(false);

    if (result.success) {
      toast.success(`Welcome back, ${result.user.full_name || result.user.email}!`);
      navigate(redirectPath, { replace: true });
    } else {
      setApiError(result.error);
    }
  };

  const quickLogin = (roleEmail, rolePassword) => {
    setEmail(roleEmail);
    setPassword(rolePassword);
    setErrors({});
    setApiError('');
  };

  return (
    <div
      style={{
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        padding: '32px 20px',
        backgroundColor: 'var(--color-canvas-parchment)',
      }}
    >
      {/* Brand Header */}
      <div style={{ textAlign: 'center', marginBottom: '32px' }}>
        <div
          style={{
            width: '60px',
            height: '60px',
            borderRadius: 'var(--radius-pill)',
            backgroundColor: 'var(--color-ink)',
            color: 'var(--color-primary-on-dark)',
            display: 'inline-flex',
            alignItems: 'center',
            justifyContent: 'center',
            marginBottom: '16px',
            boxShadow: 'var(--shadow-subtle)',
          }}
        >
          <Layers size={30} />
        </div>
        <h1
          style={{
            fontSize: '28px',
            fontWeight: 600,
            letterSpacing: '-0.374px',
            color: 'var(--color-ink)',
            marginBottom: '8px',
          }}
        >
          Sign in to Decision Replay
        </h1>
        <p style={{ fontSize: '15px', color: 'var(--color-ink-muted-48)' }}>
          Enterprise Decision Audit & Governance Platform
        </p>
      </div>

      {/* Main Login Card */}
      <div
        className="apple-card"
        style={{
          width: '100%',
          maxWidth: '440px',
          padding: '32px',
        }}
      >
        {apiError && (
          <Alert type="error" style={{ marginBottom: '20px' }}>
            {apiError}
          </Alert>
        )}

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          <FormField label="Email Address" required error={errors.email}>
            <Input
              type="email"
              placeholder="name@company.com"
              value={email}
              onChange={(e) => {
                setEmail(e.target.value);
                if (errors.email) setErrors((prev) => ({ ...prev, email: null }));
              }}
              icon={Mail}
              error={!!errors.email}
              autoComplete="email"
              autoFocus
            />
          </FormField>

          <FormField label="Password" required error={errors.password}>
            <Input
              type="password"
              placeholder="••••••••"
              value={password}
              onChange={(e) => {
                setPassword(e.target.value);
                if (errors.password) setErrors((prev) => ({ ...prev, password: null }));
              }}
              icon={Lock}
              error={!!errors.password}
              autoComplete="current-password"
            />
          </FormField>

          <Button
            type="submit"
            variant="primary"
            size="large"
            loading={loading}
            style={{ width: '100%', marginTop: '8px' }}
          >
            <span>Continue</span>
            <ArrowRight size={16} />
          </Button>
        </form>

        {/* Quick Demo Credentials */}
        <div style={{ marginTop: '28px', paddingTop: '20px', borderTop: '1px solid var(--color-divider-soft)' }}>
          <div
            style={{
              fontSize: '12px',
              fontWeight: 600,
              color: 'var(--color-ink-muted-48)',
              textTransform: 'uppercase',
              letterSpacing: '0.05em',
              marginBottom: '12px',
              textAlign: 'center',
            }}
          >
            Quick Demo Logins (Click to autofill)
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
            <button
              type="button"
              onClick={() => quickLogin('employee@example.com', 'password1234')}
              style={{
                padding: '8px 10px',
                borderRadius: 'var(--radius-sm)',
                backgroundColor: 'var(--color-surface-pearl)',
                border: '1px solid var(--color-hairline)',
                fontSize: '12px',
                fontWeight: 500,
                color: 'var(--color-ink)',
                textAlign: 'left',
              }}
            >
              <div style={{ fontWeight: 600, color: '#475569' }}>Employee</div>
              <div style={{ fontSize: '11px', color: 'var(--color-ink-muted-48)' }}>employee@example.com</div>
            </button>

            <button
              type="button"
              onClick={() => quickLogin('reviewer@example.com', 'password1234')}
              style={{
                padding: '8px 10px',
                borderRadius: 'var(--radius-sm)',
                backgroundColor: 'var(--color-surface-pearl)',
                border: '1px solid var(--color-hairline)',
                fontSize: '12px',
                fontWeight: 500,
                color: 'var(--color-ink)',
                textAlign: 'left',
              }}
            >
              <div style={{ fontWeight: 600, color: '#a21caf' }}>Reviewer</div>
              <div style={{ fontSize: '11px', color: 'var(--color-ink-muted-48)' }}>reviewer@example.com</div>
            </button>

            <button
              type="button"
              onClick={() => quickLogin('manager@example.com', 'password1234')}
              style={{
                padding: '8px 10px',
                borderRadius: 'var(--radius-sm)',
                backgroundColor: 'var(--color-surface-pearl)',
                border: '1px solid var(--color-hairline)',
                fontSize: '12px',
                fontWeight: 500,
                color: 'var(--color-ink)',
                textAlign: 'left',
              }}
            >
              <div style={{ fontWeight: 600, color: '#0369a1' }}>Manager</div>
              <div style={{ fontSize: '11px', color: 'var(--color-ink-muted-48)' }}>manager@example.com</div>
            </button>

            <button
              type="button"
              onClick={() => quickLogin('admin@example.com', 'password1234')}
              style={{
                padding: '8px 10px',
                borderRadius: 'var(--radius-sm)',
                backgroundColor: 'var(--color-surface-pearl)',
                border: '1px solid var(--color-hairline)',
                fontSize: '12px',
                fontWeight: 500,
                color: 'var(--color-ink)',
                textAlign: 'left',
              }}
            >
              <div style={{ fontWeight: 600, color: '#6d28d9' }}>Administrator</div>
              <div style={{ fontSize: '11px', color: 'var(--color-ink-muted-48)' }}>admin@example.com</div>
            </button>
          </div>
        </div>
      </div>

      <div style={{ marginTop: '24px', fontSize: '13px', color: 'var(--color-ink-muted-48)' }}>
        JWT Token Authorization
      </div>
    </div>
  );
};

export default LoginPage;
