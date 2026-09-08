import React from 'react';

export const Input = React.forwardRef(({
  type = 'text',
  placeholder,
  value,
  onChange,
  disabled = false,
  error = false,
  icon: Icon,
  className = '',
  style = {},
  ...props
}, ref) => {
  return (
    <div
      style={{
        position: 'relative',
        display: 'flex',
        alignItems: 'center',
        width: '100%',
      }}
    >
      {Icon && (
        <div
          style={{
            position: 'absolute',
            left: '14px',
            color: 'var(--color-ink-muted-48)',
            pointerEvents: 'none',
            display: 'flex',
            alignItems: 'center',
          }}
        >
          <Icon size={16} />
        </div>
      )}
      <input
        ref={ref}
        type={type}
        placeholder={placeholder}
        value={value}
        onChange={onChange}
        disabled={disabled}
        style={{
          width: '100%',
          height: '42px',
          padding: Icon ? '0 14px 0 40px' : '0 14px',
          backgroundColor: 'var(--color-canvas)',
          border: `1px solid ${error ? '#dc2626' : 'var(--color-hairline)'}`,
          borderRadius: 'var(--radius-sm)',
          color: 'var(--color-ink)',
          fontSize: '15px',
          outline: 'none',
          transition: 'border-color 0.15s ease, box-shadow 0.15s ease',
          boxShadow: error ? '0 0 0 1px #dc2626' : 'none',
          opacity: disabled ? 0.6 : 1,
          ...style,
        }}
        onFocus={(e) => {
          if (!error) {
            e.target.style.borderColor = 'var(--color-primary-focus)';
            e.target.style.boxShadow = '0 0 0 2px rgba(0, 113, 227, 0.2)';
          }
        }}
        onBlur={(e) => {
          if (!error) {
            e.target.style.borderColor = 'var(--color-hairline)';
            e.target.style.boxShadow = 'none';
          }
        }}
        className={className}
        {...props}
      />
    </div>
  );
});

Input.displayName = 'Input';
export default Input;
