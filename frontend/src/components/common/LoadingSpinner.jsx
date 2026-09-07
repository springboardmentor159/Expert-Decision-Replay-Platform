import React from 'react';

export function LoadingSpinner({ message = 'Loading...', size = 'medium' }) {
  const spinnerSize = size === 'small' ? '16px' : size === 'large' ? '36px' : '24px';

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '3rem 1rem',
      gap: '1rem',
      color: 'var(--text-secondary)',
    }}>
      <div
        className="spinner"
        style={{
          width: spinnerSize,
          height: spinnerSize,
          borderWidth: size === 'small' ? '2px' : '3px',
          borderColor: 'var(--primary-light)',
          borderTopColor: 'var(--primary)',
        }}
      />
      {message && <span style={{ fontSize: '0.9rem', fontWeight: 500 }}>{message}</span>}
    </div>
  );
}
