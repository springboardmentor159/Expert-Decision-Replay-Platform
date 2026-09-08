import React from 'react';
import { ShieldAlert, ArrowLeft } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import Button from '../components/common/Button';
import Badge from '../components/common/Badge';

export const UnauthorizedPage = () => {
  const { user } = useAuth();

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '60vh',
        textAlign: 'center',
        padding: '40px 20px',
      }}
    >
      <div
        style={{
          width: '72px',
          height: '72px',
          borderRadius: 'var(--radius-pill)',
          backgroundColor: '#fee2e2',
          color: '#dc2626',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          marginBottom: '20px',
        }}
      >
        <ShieldAlert size={36} />
      </div>

      <h1
        style={{
          fontSize: '28px',
          fontWeight: 600,
          color: 'var(--color-ink)',
          marginBottom: '10px',
          letterSpacing: '-0.3px',
        }}
      >
        403 — Access Restricted
      </h1>

      <p
        style={{
          fontSize: '15px',
          color: 'var(--color-ink-muted-48)',
          maxWidth: '440px',
          lineHeight: 1.5,
          marginBottom: '16px',
        }}
      >
        You do not have the required permissions to access this page. Your current role is{' '}
        <Badge variant="role">{user?.role || 'Guest'}</Badge>.
      </p>

      <div style={{ marginTop: '12px' }}>
        <Link to="/dashboard">
          <Button variant="primary" icon={ArrowLeft}>
            Return to Dashboard
          </Button>
        </Link>
      </div>
    </div>
  );
};

export default UnauthorizedPage;
