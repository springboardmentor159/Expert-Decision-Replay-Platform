import React from 'react';
import { RotateCcw } from 'lucide-react';
import SearchInput from './SearchInput';
import Select from './Select';
import Button from './Button';

export const FilterBar = ({
  searchValue = '',
  onSearchChange,
  searchPlaceholder = 'Search records...',
  filters = [], // array of { key, label, value, options, placeholder, onChange }
  onReset,
  showReset = true,
  actionButton,
  className = '',
  style = {},
}) => {
  const hasActiveFilters = searchValue || filters.some((f) => f.value);

  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '16px',
        marginBottom: '20px',
        width: '100%',
        ...style,
      }}
      className={className}
    >
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '12px',
          flex: 1,
          minWidth: '280px',
        }}
      >
        {onSearchChange && (
          <SearchInput
            value={searchValue}
            onChange={(e) => onSearchChange(e.target.value)}
            onClear={() => onSearchChange('')}
            placeholder={searchPlaceholder}
          />
        )}

        {filters.map((filter) => (
          <div key={filter.key} style={{ minWidth: '160px' }}>
            <Select
              options={filter.options}
              value={filter.value}
              onChange={(e) => filter.onChange(e.target.value)}
              placeholder={filter.placeholder || filter.label}
              style={{ height: '44px', borderRadius: 'var(--radius-pill)', paddingLeft: '16px' }}
            />
          </div>
        ))}

        {showReset && hasActiveFilters && onReset && (
          <Button
            variant="ghost"
            size="small"
            onClick={onReset}
            icon={RotateCcw}
            style={{ color: 'var(--color-ink-muted-48)', fontSize: '13px' }}
          >
            Reset
          </Button>
        )}
      </div>

      {actionButton && <div>{actionButton}</div>}
    </div>
  );
};

export default FilterBar;
