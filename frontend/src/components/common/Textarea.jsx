import React from 'react';

export const Textarea = React.forwardRef(({
  placeholder,
  value,
  onChange,
  disabled = false,
  rows = 4,
  error = false,
  className = '',
  style = {},
  ...props
}, ref) => {
  return (
    <textarea
      ref={ref}
      rows={rows}
      placeholder={placeholder}
      value={value}
      onChange={onChange}
      disabled={disabled}
      style={{
        width: '100%',
        padding: '12px 14px',
        backgroundColor: 'var(--color-canvas)',
        border: `1px solid ${error ? '#dc2626' : 'var(--color-hairline)'}`,
        borderRadius: 'var(--radius-sm)',
        color: 'var(--color-ink)',
        fontSize: '15px',
        lineHeight: 1.5,
        outline: 'none',
        resize: 'vertical',
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
  );
});

Textarea.displayName = 'Textarea';
export default Textarea;
