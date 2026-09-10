import React from 'react';

export const Card = ({ children, className = '', style = {}, onClick }) => {
  return (
    <div
      onClick={onClick}
      className={`glass-panel ${className}`}
      style={{
        padding: '1.5rem',
        cursor: onClick ? 'pointer' : 'default',
        ...style,
      }}
    >
      {children}
    </div>
  );
};
