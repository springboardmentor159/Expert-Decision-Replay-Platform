import React from 'react';

export const Badge = ({
  children,
  variant = 'default', // 'draft' | 'under-review' | 'approved' | 'rejected' | 'archived' | 'low' | 'medium' | 'high' | 'critical' | 'role' | 'default'
  size = 'medium', // 'small' | 'medium'
  style = {},
  className = '',
}) => {
  const getBadgeStyles = () => {
    let bg = 'var(--status-draft-bg)';
    let color = 'var(--status-draft-text)';
    let border = 'transparent';

    const normalized = (typeof children === 'string' ? children.toLowerCase() : variant.toLowerCase());

    if (normalized.includes('draft')) {
      bg = 'var(--status-draft-bg)';
      color = 'var(--status-draft-text)';
    } else if (normalized.includes('review') || normalized.includes('under review')) {
      bg = 'var(--status-review-bg)';
      color = 'var(--status-review-text)';
    } else if (normalized.includes('approved')) {
      bg = 'var(--status-approved-bg)';
      color = 'var(--status-approved-text)';
    } else if (normalized.includes('rejected')) {
      bg = 'var(--status-rejected-bg)';
      color = 'var(--status-rejected-text)';
    } else if (normalized.includes('archived')) {
      bg = 'var(--status-archived-bg)';
      color = 'var(--status-archived-text)';
    } else if (normalized.includes('low')) {
      bg = '#ecfdf5';
      color = '#047857';
    } else if (normalized.includes('medium')) {
      bg = '#fef3c7';
      color = '#b45309';
    } else if (normalized.includes('high')) {
      bg = '#ffedd5';
      color = '#c2410c';
    } else if (normalized.includes('critical')) {
      bg = '#fee2e2';
      color = '#b91c1c';
    } else if (normalized.includes('admin') || normalized.includes('administrator')) {
      bg = '#ede9fe';
      color = '#6d28d9';
    } else if (normalized.includes('manager')) {
      bg = '#e0f2fe';
      color = '#0369a1';
    } else if (normalized.includes('reviewer')) {
      bg = '#fdf4ff';
      color = '#a21caf';
    } else if (normalized.includes('employee')) {
      bg = '#f1f5f9';
      color = '#475569';
    }

    return {
      display: 'inline-flex',
      alignItems: 'center',
      justifyContent: 'center',
      borderRadius: 'var(--radius-pill)',
      fontWeight: 600,
      backgroundColor: bg,
      color: color,
      border: `1px solid ${border}`,
      letterSpacing: '-0.12px',
      padding: size === 'small' ? '2px 8px' : '4px 12px',
      fontSize: size === 'small' ? '11px' : '12px',
      lineHeight: '1.2',
      ...style,
    };
  };

  return (
    <span style={getBadgeStyles()} className={className}>
      {children}
    </span>
  );
};

export default Badge;
