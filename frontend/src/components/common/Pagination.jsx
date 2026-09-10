import React from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { Button } from './Button';

export const Pagination = ({
  page,
  totalPages,
  totalItems,
  pageSize,
  onPageChange,
}) => {
  if (totalPages <= 1) return null;

  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        marginTop: '1.5rem',
        padding: '0.75rem 0',
      }}
    >
      <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
        Showing page <strong style={{ color: '#ffffff' }}>{page}</strong> of{' '}
        <strong style={{ color: '#ffffff' }}>{totalPages}</strong>
        {totalItems !== undefined && ` (${totalItems} total items)`}
      </span>
      <div style={{ display: 'flex', gap: '0.5rem' }}>
        <Button
          variant="secondary"
          size="sm"
          disabled={page <= 1}
          onClick={() => onPageChange(page - 1)}
          icon={ChevronLeft}
        >
          Previous
        </Button>
        <Button
          variant="secondary"
          size="sm"
          disabled={page >= totalPages}
          onClick={() => onPageChange(page + 1)}
        >
          Next <ChevronRight size={14} style={{ marginLeft: '4px' }} />
        </Button>
      </div>
    </div>
  );
};
