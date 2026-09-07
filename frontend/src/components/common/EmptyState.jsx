import React from 'react';
import { FolderOpen } from 'lucide-react';

export function EmptyState({
  title = 'No items found',
  description = 'There is currently no data to display.',
  icon: Icon = FolderOpen,
  action = null,
}) {
  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '4rem 1.5rem',
      textAlign: 'center',
      background: 'var(--bg-card)',
      border: '1px dashed var(--border-color)',
      borderRadius: '12px',
      margin: '1.5rem 0',
    }}>
      <div style={{
        width: '54px',
        height: '54px',
        borderRadius: '50%',
        background: 'var(--bg-hover)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        color: 'var(--text-muted)',
        marginBottom: '1rem',
      }}>
        <Icon size={26} />
      </div>
      <h3 style={{ fontSize: '1.15rem', marginBottom: '0.4rem', color: 'var(--text-primary)' }}>
        {title}
      </h3>
      <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', maxWidth: '400px', marginBottom: action ? '1.5rem' : 0 }}>
        {description}
      </p>
      {action && <div>{action}</div>}
    </div>
  );
}
