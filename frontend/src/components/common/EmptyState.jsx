import React from 'react';
import { FolderOpen } from 'lucide-react';
import Button from './Button';

export const EmptyState = ({
  icon: Icon = FolderOpen,
  title = 'No items found',
  description = 'There are no records matching your current selection.',
  actionText,
  onAction,
  className = '',
  style = {},
}) => {
  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        textAlign: 'center',
        padding: '60px 24px',
        backgroundColor: 'var(--color-canvas)',
        borderRadius: 'var(--radius-lg)',
        border: '1px solid var(--color-hairline)',
        ...style,
      }}
      className={className}
    >
      <div
        style={{
          width: '56px',
          height: '56px',
          borderRadius: 'var(--radius-pill)',
          backgroundColor: 'var(--color-canvas-parchment)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: 'var(--color-ink-muted-48)',
          marginBottom: '16px',
        }}
      >
        <Icon size={28} />
      </div>
      <h3
        style={{
          fontSize: '18px',
          fontWeight: 600,
          color: 'var(--color-ink)',
          marginBottom: '8px',
          letterSpacing: '-0.2px',
        }}
      >
        {title}
      </h3>
      <p
        style={{
          fontSize: '14px',
          color: 'var(--color-ink-muted-48)',
          maxWidth: '380px',
          marginBottom: actionText ? '24px' : '0px',
          lineHeight: 1.5,
        }}
      >
        {description}
      </p>
      {actionText && onAction && (
        <Button variant="primary" size="medium" onClick={onAction}>
          {actionText}
        </Button>
      )}
    </div>
  );
};

export default EmptyState;
