import React from 'react';

export const LoadingSpinner = ({ message = 'Loading...' }) => {
  return (
    <div className="loading-spinner-container">
      <div className="spinner"></div>
      <p className="text-muted" style={{ fontSize: '0.9rem', fontWeight: 500 }}>{message}</p>
    </div>
  );
};
