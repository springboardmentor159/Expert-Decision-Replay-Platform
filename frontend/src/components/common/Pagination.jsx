import React from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import Button from './Button';

export const Pagination = ({
  currentPage = 1,
  totalPages = 1,
  totalItems,
  pageSize = 10,
  onPageChange,
  onPageSizeChange,
  pageSizeOptions = [10, 20, 50, 100],
  className = '',
  style = {},
}) => {
  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '16px',
        padding: '12px 18px',
        fontSize: '13px',
        color: 'var(--color-ink-muted-80)',
        ...style,
      }}
      className={className}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        {totalItems !== undefined && (
          <span>
            Showing <strong style={{ color: 'var(--color-ink)' }}>{(currentPage - 1) * pageSize + 1}</strong> to{' '}
            <strong style={{ color: 'var(--color-ink)' }}>{Math.min(currentPage * pageSize, totalItems)}</strong> of{' '}
            <strong style={{ color: 'var(--color-ink)' }}>{totalItems}</strong> items
          </span>
        )}
        {onPageSizeChange && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span>Show</span>
            <select
              value={pageSize}
              onChange={(e) => onPageSizeChange(Number(e.target.value))}
              style={{
                padding: '4px 8px',
                borderRadius: 'var(--radius-sm)',
                border: '1px solid var(--color-hairline)',
                backgroundColor: 'var(--color-canvas)',
                fontSize: '13px',
                outline: 'none',
              }}
            >
              {pageSizeOptions.map((opt) => (
                <option key={opt} value={opt}>
                  {opt}
                </option>
              ))}
            </select>
            <span>per page</span>
          </div>
        )}
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <Button
          variant="pearl"
          size="small"
          disabled={currentPage <= 1}
          onClick={() => onPageChange(currentPage - 1)}
          icon={ChevronLeft}
        >
          Previous
        </Button>
        <span style={{ padding: '0 4px', fontWeight: 500 }}>
          Page {currentPage} of {Math.max(1, totalPages)}
        </span>
        <Button
          variant="pearl"
          size="small"
          disabled={currentPage >= totalPages}
          onClick={() => onPageChange(currentPage + 1)}
          style={{ flexDirection: 'row-reverse' }}
          icon={ChevronRight}
        >
          Next
        </Button>
      </div>
    </div>
  );
};

export default Pagination;
