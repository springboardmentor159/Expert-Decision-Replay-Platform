import React from 'react';
import { AlertCircle, CheckCircle2, AlertTriangle, Info, X } from 'lucide-react';

export const Alert = ({
  type = 'info', // 'info' | 'success' | 'warning' | 'error'
  title,
  children,
  onClose,
  className = '',
  style = {},
}) => {
  const getStyles = () => {
    switch (type) {
      case 'success':
        return {
          bg: 'var(--status-approved-bg)',
          color: 'var(--status-approved-text)',
          border: 'rgba(5, 150, 105, 0.25)',
          Icon: CheckCircle2,
        };
      case 'warning':
        return {
          bg: 'var(--status-review-bg)',
          color: 'var(--status-review-text)',
          border: 'rgba(217, 119, 6, 0.25)',
          Icon: AlertTriangle,
        };
      case 'error':
        return {
          bg: 'var(--status-rejected-bg)',
          color: 'var(--status-rejected-text)',
          border: 'rgba(220, 38, 38, 0.25)',
          Icon: AlertCircle,
        };
      case 'info':
      default:
        return {
          bg: '#eff6ff',
          color: '#1e40af',
          border: 'rgba(37, 99, 235, 0.25)',
          Icon: Info,
        };
    }
  };

  const { bg, color, border, Icon } = getStyles();

  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'flex-start',
        gap: '12px',
        padding: '14px 18px',
        backgroundColor: bg,
        color: color,
        border: `1px solid ${border}`,
        borderRadius: 'var(--radius-md)',
        fontSize: '14px',
        lineHeight: 1.4,
        ...style,
      }}
      className={className}
    >
      <Icon size={18} style={{ flexShrink: 0, marginTop: '2px' }} />
      <div style={{ flex: 1 }}>
        {title && <div style={{ fontWeight: 600, marginBottom: '2px' }}>{title}</div>}
        <div>{children}</div>
      </div>
      {onClose && (
        <button
          onClick={onClose}
          style={{
            color: 'inherit',
            opacity: 0.6,
            padding: '2px',
            display: 'flex',
            alignItems: 'center',
          }}
          aria-label="Dismiss alert"
        >
          <X size={14} />
        </button>
      )}
    </div>
  );
};

export default Alert;
