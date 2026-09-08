import React from 'react';
import { Search, X } from 'lucide-react';

export const SearchInput = ({
  value,
  onChange,
  onClear,
  placeholder = 'Search...',
  className = '',
  style = {},
  ...props
}) => {
  return (
    <div
      style={{
        position: 'relative',
        display: 'flex',
        alignItems: 'center',
        width: '100%',
        maxWidth: '360px',
      }}
      className={className}
    >
      <div
        style={{
          position: 'absolute',
          left: '16px',
          color: 'var(--color-ink-muted-48)',
          display: 'flex',
          alignItems: 'center',
          pointerEvents: 'none',
        }}
      >
        <Search size={16} />
      </div>
      <input
        type="text"
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        style={{
          width: '100%',
          height: '44px',
          padding: '0 38px 0 42px',
          backgroundColor: 'var(--color-canvas)',
          color: 'var(--color-ink)',
          border: '1px solid rgba(0, 0, 0, 0.08)',
          borderRadius: 'var(--radius-pill)',
          fontSize: '15px',
          outline: 'none',
          boxShadow: 'var(--shadow-subtle)',
          transition: 'border-color 0.15s ease, box-shadow 0.15s ease',
          ...style,
        }}
        onFocus={(e) => {
          e.target.style.borderColor = 'var(--color-primary-focus)';
          e.target.style.boxShadow = '0 0 0 2px rgba(0, 113, 227, 0.2)';
        }}
        onBlur={(e) => {
          e.target.style.borderColor = 'rgba(0, 0, 0, 0.08)';
          e.target.style.boxShadow = 'var(--shadow-subtle)';
        }}
        {...props}
      />
      {value && onClear && (
        <button
          type="button"
          onClick={onClear}
          style={{
            position: 'absolute',
            right: '14px',
            color: 'var(--color-ink-muted-48)',
            display: 'flex',
            alignItems: 'center',
            padding: '2px',
          }}
          aria-label="Clear search"
        >
          <X size={14} />
        </button>
      )}
    </div>
  );
};

export default SearchInput;
