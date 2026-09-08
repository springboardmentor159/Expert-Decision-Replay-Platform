import React from 'react';
import { ChevronUp, ChevronDown } from 'lucide-react';
import Skeleton from './Skeleton';
import EmptyState from './EmptyState';

export const Table = ({
  columns = [],
  data = [],
  loading = false,
  emptyTitle = 'No data available',
  emptyDescription = 'There are no records to display.',
  onRowClick,
  sortColumn,
  sortDirection,
  onSort,
  className = '',
  style = {},
}) => {
  return (
    <div
      style={{
        backgroundColor: 'var(--color-canvas)',
        borderRadius: 'var(--radius-lg)',
        border: '1px solid var(--color-hairline)',
        overflow: 'hidden',
        boxShadow: 'var(--shadow-subtle)',
        width: '100%',
        ...style,
      }}
      className={className}
    >
      <div style={{ overflowX: 'auto', width: '100%' }}>
        <table
          style={{
            width: '100%',
            borderCollapse: 'collapse',
            textAlign: 'left',
            fontSize: '14px',
          }}
        >
          <thead>
            <tr
              style={{
                backgroundColor: 'var(--color-surface-pearl)',
                borderBottom: '1px solid var(--color-hairline)',
              }}
            >
              {columns.map((col) => {
                const isSortable = col.sortable && onSort;
                const isSorted = sortColumn === col.key;

                return (
                  <th
                    key={col.key}
                    style={{
                      padding: '12px 18px',
                      fontWeight: 600,
                      color: 'var(--color-ink-muted-80)',
                      cursor: isSortable ? 'pointer' : 'default',
                      userSelect: 'none',
                      whiteSpace: 'nowrap',
                      width: col.width || 'auto',
                    }}
                    onClick={() => isSortable && onSort(col.key)}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <span>{col.header}</span>
                      {isSortable && (
                        <div style={{ display: 'flex', flexDirection: 'column', color: isSorted ? 'var(--color-primary)' : 'var(--color-ink-muted-48)' }}>
                          {isSorted && sortDirection === 'asc' ? (
                            <ChevronUp size={14} />
                          ) : isSorted && sortDirection === 'desc' ? (
                            <ChevronDown size={14} />
                          ) : (
                            <div style={{ opacity: 0.4 }}>
                              <ChevronUp size={12} style={{ marginBottom: '-4px' }} />
                              <ChevronDown size={12} />
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  </th>
                );
              })}
            </tr>
          </thead>
          <tbody>
            {loading ? (
              // Loading Skeleton Rows
              Array.from({ length: 5 }).map((_, rIndex) => (
                <tr
                  key={`skeleton-${rIndex}`}
                  style={{
                    borderBottom: '1px solid var(--color-divider-soft)',
                  }}
                >
                  {columns.map((col, cIndex) => (
                    <td key={`skeleton-cell-${cIndex}`} style={{ padding: '16px 18px' }}>
                      <Skeleton width={cIndex === 0 ? '60%' : '80%'} height="16px" />
                    </td>
                  ))}
                </tr>
              ))
            ) : data.length === 0 ? (
              <tr>
                <td colSpan={columns.length} style={{ padding: '32px 16px' }}>
                  <EmptyState title={emptyTitle} description={emptyDescription} style={{ border: 'none', padding: '32px' }} />
                </td>
              </tr>
            ) : (
              data.map((row, rowIndex) => (
                <tr
                  key={row.id || rowIndex}
                  onClick={() => onRowClick && onRowClick(row)}
                  style={{
                    borderBottom: '1px solid var(--color-divider-soft)',
                    cursor: onRowClick ? 'pointer' : 'default',
                    transition: 'background-color 0.1s ease',
                  }}
                  onMouseEnter={(e) => {
                    if (onRowClick) e.currentTarget.style.backgroundColor = 'var(--color-surface-pearl)';
                  }}
                  onMouseLeave={(e) => {
                    if (onRowClick) e.currentTarget.style.backgroundColor = 'transparent';
                  }}
                >
                  {columns.map((col) => (
                    <td
                      key={col.key}
                      style={{
                        padding: '14px 18px',
                        color: 'var(--color-body)',
                        verticalAlign: 'middle',
                      }}
                    >
                      {col.render ? col.render(row[col.key], row) : row[col.key]}
                    </td>
                  ))}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default Table;
