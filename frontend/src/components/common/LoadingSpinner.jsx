import React from 'react';

export const LoadingSpinner = ({ message = 'Loading...', size = 'md' }) => {
  const dim = size === 'sm' ? 24 : size === 'lg' ? 48 : 36;

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '3rem 1rem',
        gap: '1rem',
        color: 'var(--text-secondary)',
      }}
    >
      <div
        style={{
          width: `${dim}px`,
          height: `${dim}px`,
          border: '3px solid rgba(59, 130, 246, 0.15)',
          borderTopColor: 'var(--accent-blue)',
          borderRadius: '50%',
          animation: 'spin 0.8s linear infinite',
        }}
      />
      <span style={{ fontSize: '0.95rem', fontWeight: 500 }}>{message}</span>
      <style>{`
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};
