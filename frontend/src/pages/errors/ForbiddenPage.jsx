import React from 'react';
import { Link } from 'react-router-dom';
import { ShieldAlert, ArrowLeft } from 'lucide-react';

export const ForbiddenPage = () => {
  return (
    <div
      style={{
        minHeight: '70vh',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        textAlign: 'center',
        padding: '2rem',
      }}
    >
      <div
        style={{
          width: '72px',
          height: '72px',
          borderRadius: '50%',
          background: 'var(--danger-surface)',
          border: '1px solid var(--danger-border)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: '#dc2626',
          marginBottom: '1.5rem',
        }}
      >
        <ShieldAlert size={36} />
      </div>

      <h1 style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--text-primary)', marginBottom: '0.5rem' }}>
        403 - Access Forbidden
      </h1>
      <p className="text-muted" style={{ maxWidth: '440px', fontSize: '0.95rem', marginBottom: '1.5rem' }}>
        You do not have the required role permissions to view or interact with this resource. If you believe this is in error, contact your system administrator.
      </p>

      <Link to="/dashboard" className="btn btn-primary">
        <ArrowLeft size={16} /> Return to Dashboard
      </Link>
    </div>
  );
};
