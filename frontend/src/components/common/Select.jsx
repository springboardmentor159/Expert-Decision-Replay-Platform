import React from 'react';
import { ChevronDown } from 'lucide-react';

export const Select = React.forwardRef(({
  options = [],
  value,
  onChange,
  disabled = false,
  placeholder = 'Select an option',
  error = false,
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
      <select
        ref={ref}
        value={value}
        onChange={onChange}
        disabled={disabled}
        style={{
          width: '100%',
          height: '42px',
          padding: '0 36px 0 14px',
          backgroundColor: 'var(--color-canvas)',
          border: `1px solid ${error ? '#dc2626' : 'var(--color-hairline)'}`,
          borderRadius: 'var(--radius-sm)',
          color: 'var(--color-ink)',
          fontSize: '15px',
          outline: 'none',
          appearance: 'none',
          WebkitAppearance: 'none',
          cursor: disabled ? 'not-allowed' : 'pointer',
          transition: 'border-color 0.15s ease, box-shadow 0.15s ease',
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
      >
        {placeholder && (
          <option value="" disabled>
            {placeholder}
          </option>
        )}
        {options.map((opt) => {
          const optValue = typeof opt === 'object' ? opt.value : opt;
          const optLabel = typeof opt === 'object' ? opt.label : opt;
          return (
            <option key={optValue} value={optValue}>
              {optLabel}
            </option>
          );
        })}
      </select>
      <div
        style={{
          position: 'absolute',
          right: '12px',
          color: 'var(--color-ink-muted-48)',
          pointerEvents: 'none',
          display: 'flex',
          alignItems: 'center',
        }}
      >
        <ChevronDown size={16} />
      </div>
    </div>
  );
});

Select.displayName = 'Select';
export default Select;
