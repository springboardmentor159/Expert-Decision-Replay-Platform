import React from 'react';

export const Input = ({
  label,
  error,
  id,
  type = 'text',
  placeholder,
  value,
  onChange,
  required = false,
  disabled = false,
  helperText,
  className = '',
  ...props
}) => {
  return (
    <div className="form-group">
      {label && (
        <label htmlFor={id} className="form-label">
          <span>
            {label} {required && <span style={{ color: 'var(--accent-rose)' }}>*</span>}
          </span>
        </label>
      )}
      <input
        id={id}
        type={type}
        placeholder={placeholder}
        value={value}
        onChange={onChange}
        required={required}
        disabled={disabled}
        className={`form-input ${error ? 'border-rose-500' : ''} ${className}`}
        {...props}
      />
      {error && <span className="form-error">{error}</span>}
      {!error && helperText && (
        <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{helperText}</span>
      )}
    </div>
  );
};

export const TextArea = ({
  label,
  error,
  id,
  placeholder,
  value,
  onChange,
  required = false,
  disabled = false,
  rows = 4,
  className = '',
  ...props
}) => {
  return (
    <div className="form-group">
      {label && (
        <label htmlFor={id} className="form-label">
          <span>
            {label} {required && <span style={{ color: 'var(--accent-rose)' }}>*</span>}
          </span>
        </label>
      )}
      <textarea
        id={id}
        rows={rows}
        placeholder={placeholder}
        value={value}
        onChange={onChange}
        required={required}
        disabled={disabled}
        className={`form-textarea ${className}`}
        {...props}
      />
      {error && <span className="form-error">{error}</span>}
    </div>
  );
};

export const Select = ({
  label,
  error,
  id,
  options = [],
  value,
  onChange,
  required = false,
  disabled = false,
  placeholder = 'Select option...',
  className = '',
  ...props
}) => {
  return (
    <div className="form-group">
      {label && (
        <label htmlFor={id} className="form-label">
          <span>
            {label} {required && <span style={{ color: 'var(--accent-rose)' }}>*</span>}
          </span>
        </label>
      )}
      <select
        id={id}
        value={value}
        onChange={onChange}
        required={required}
        disabled={disabled}
        className={`form-select ${className}`}
        {...props}
      >
        {placeholder && <option value="">{placeholder}</option>}
        {options.map((opt) => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>
      {error && <span className="form-error">{error}</span>}
    </div>
  );
};
