import React from 'react';
import { Link } from 'react-router-dom';
import { HelpCircle, ArrowLeft } from 'lucide-react';

export const NotFoundPage = () => {
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
          background: '#ecfdf5',
          border: '1px solid #a7f3d0',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: 'var(--primary)',
          marginBottom: '1.5rem',
        }}
      >
        <HelpCircle size={36} />
      </div>

      <h1 style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--text-primary)', marginBottom: '0.5rem' }}>
        404 - Page Not Found
      </h1>
      <p className="text-muted" style={{ maxWidth: '440px', fontSize: '0.95rem', marginBottom: '1.5rem' }}>
        The requested URL or decision artifact does not exist or has been relocated.
      </p>

      <Link to="/dashboard" className="btn btn-primary">
        <ArrowLeft size={16} /> Return to Dashboard
      </Link>
    </div>
  );
};
