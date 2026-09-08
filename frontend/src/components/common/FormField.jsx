import React from 'react';

export const FormField = ({
  label,
  required = false,
  error,
  hint,
  children,
  className = '',
  style = {},
}) => {
  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        gap: '6px',
        width: '100%',
        ...style,
      }}
      className={className}
    >
      {label && (
        <label
          style={{
            fontSize: '13px',
            fontWeight: 600,
            color: 'var(--color-ink-muted-80)',
            letterSpacing: '-0.1px',
            display: 'flex',
            alignItems: 'center',
            gap: '4px',
          }}
        >
          {label}
          {required && <span style={{ color: '#dc2626' }}>*</span>}
        </label>
      )}
      {children}
      {error && (
        <span
          style={{
            fontSize: '12px',
            color: '#dc2626',
            fontWeight: 500,
            display: 'flex',
            alignItems: 'center',
            gap: '4px',
          }}
        >
          {error}
        </span>
      )}
      {!error && hint && (
        <span
          style={{
            fontSize: '12px',
            color: 'var(--color-ink-muted-48)',
          }}
        >
          {hint}
        </span>
      )}
    </div>
  );
};

export default FormField;
