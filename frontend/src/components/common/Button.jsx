import React from 'react';
import { Loader2 } from 'lucide-react';

export const Button = ({
  children,
  variant = 'primary', // 'primary' | 'secondary' | 'dark' | 'pearl' | 'danger' | 'ghost' | 'icon'
  size = 'medium', // 'small' | 'medium' | 'large'
  loading = false,
  disabled = false,
  icon: Icon,
  className = '',
  style = {},
  type = 'button',
  onClick,
  ...props
}) => {
  const getStyles = () => {
    const base = {
      display: 'inline-flex',
      alignItems: 'center',
      justifyContent: 'center',
      gap: '8px',
      fontWeight: 500,
      cursor: disabled || loading ? 'not-allowed' : 'pointer',
      opacity: disabled || loading ? 0.6 : 1,
      transition: 'all 0.15s ease',
      outline: 'none',
      userSelect: 'none',
    };

    let variantStyles = {};
    switch (variant) {
      case 'primary':
        variantStyles = {
          backgroundColor: 'var(--color-primary)',
          color: 'var(--color-on-primary)',
          borderRadius: 'var(--radius-pill)',
          border: 'none',
        };
        break;
      case 'secondary':
        variantStyles = {
          backgroundColor: 'transparent',
          color: 'var(--color-primary)',
          border: '1px solid var(--color-primary)',
          borderRadius: 'var(--radius-pill)',
        };
        break;
      case 'dark':
        variantStyles = {
          backgroundColor: 'var(--color-ink)',
          color: 'var(--color-on-dark)',
          borderRadius: 'var(--radius-sm)',
          border: 'none',
        };
        break;
      case 'pearl':
        variantStyles = {
          backgroundColor: 'var(--color-surface-pearl)',
          color: 'var(--color-ink-muted-80)',
          border: '1px solid var(--color-divider-soft)',
          borderRadius: 'var(--radius-md)',
        };
        break;
      case 'danger':
        variantStyles = {
          backgroundColor: '#dc2626',
          color: '#ffffff',
          borderRadius: 'var(--radius-pill)',
          border: 'none',
        };
        break;
      case 'ghost':
        variantStyles = {
          backgroundColor: 'transparent',
          color: 'var(--color-primary)',
          border: 'none',
          borderRadius: 'var(--radius-sm)',
        };
        break;
      case 'icon':
        variantStyles = {
          backgroundColor: 'var(--color-surface-pearl)',
          color: 'var(--color-ink)',
          border: '1px solid var(--color-hairline)',
          borderRadius: 'var(--radius-pill)',
          padding: '8px',
        };
        break;
      default:
        break;
    }

    let sizeStyles = {};
    if (variant !== 'icon') {
      switch (size) {
        case 'small':
          sizeStyles = {
            padding: '6px 14px',
            fontSize: '13px',
          };
          break;
        case 'large':
          sizeStyles = {
            padding: '14px 28px',
            fontSize: '18px',
            fontWeight: 400,
          };
          break;
        case 'medium':
        default:
          sizeStyles = {
            padding: '10px 20px',
            fontSize: '15px',
          };
          break;
      }
    }

    return { ...base, ...variantStyles, ...sizeStyles, ...style };
  };

  return (
    <button
      type={type}
      disabled={disabled || loading}
      onClick={onClick}
      style={getStyles()}
      className={className}
      {...props}
    >
      {loading ? (
        <Loader2 className="animate-spin" size={16} style={{ animation: 'spin 1s linear infinite' }} />
      ) : Icon ? (
        <Icon size={16} />
      ) : null}
      {children}
    </button>
  );
};

export default Button;
