import React from 'react';
import { HelpCircle, ArrowLeft } from 'lucide-react';
import { Link } from 'react-router-dom';
import Button from '../components/common/Button';

export const NotFoundPage = () => {
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
          backgroundColor: 'var(--color-surface-pearl)',
          color: 'var(--color-ink-muted-48)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          marginBottom: '20px',
        }}
      >
        <HelpCircle size={36} />
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
        404 — Page Not Found
      </h1>

      <p
        style={{
          fontSize: '15px',
          color: 'var(--color-ink-muted-48)',
          maxWidth: '420px',
          lineHeight: 1.5,
          marginBottom: '24px',
        }}
      >
        The page you are looking for does not exist or may have been moved.
      </p>

      <Link to="/dashboard">
        <Button variant="primary" icon={ArrowLeft}>
          Back to Dashboard
        </Button>
      </Link>
    </div>
  );
};

export default NotFoundPage;
