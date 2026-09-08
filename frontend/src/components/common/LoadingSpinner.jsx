import React from 'react';
import { Loader2 } from 'lucide-react';

export const LoadingSpinner = ({
  size = 'medium', // 'small' | 'medium' | 'large'
  color = 'var(--color-primary)',
  text = '',
  className = '',
}) => {
  const pixelSize = size === 'small' ? 16 : size === 'large' ? 36 : 24;

  return (
    <div
      style={{
        display: 'inline-flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        gap: '8px',
        padding: '8px',
      }}
      className={className}
    >
      <Loader2
        size={pixelSize}
        color={color}
        style={{
          animation: 'spin 0.8s linear infinite',
        }}
      />
      {text && (
        <span
          style={{
            fontSize: '13px',
            color: 'var(--color-ink-muted-48)',
            fontWeight: 500,
          }}
        >
          {text}
        </span>
      )}
      <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};

export default LoadingSpinner;
