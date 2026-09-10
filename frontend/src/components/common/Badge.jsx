import React from 'react';

export const StatusBadge = ({ status }) => {
  const normalized = (status || '').toLowerCase().replace(/\s+/g, '-');

  let badgeClass = 'badge-draft';
  if (normalized === 'under-review') badgeClass = 'badge-review';
  else if (normalized === 'approved') badgeClass = 'badge-approved';
  else if (normalized === 'rejected') badgeClass = 'badge-rejected';
  else if (normalized === 'archived') badgeClass = 'badge-archived';

  return <span className={`badge ${badgeClass}`}>{status || 'Draft'}</span>;
};

export const RoleBadge = ({ role }) => {
  return <span className="badge badge-role">{role || 'Employee'}</span>;
};

export const RiskBadge = ({ risk }) => {
  const r = (risk || '').toLowerCase();
  let color = '#10b981';
  let bg = 'rgba(16, 185, 129, 0.15)';
  let border = 'rgba(16, 185, 129, 0.3)';

  if (r === 'medium') {
    color = '#f59e0b';
    bg = 'rgba(245, 158, 11, 0.15)';
    border = 'rgba(245, 158, 11, 0.3)';
  } else if (r === 'high') {
    color = '#f43f5e';
    bg = 'rgba(244, 63, 94, 0.15)';
    border = 'rgba(244, 63, 94, 0.3)';
  }

  return (
    <span
      className="badge"
      style={{
        backgroundColor: bg,
        color,
        borderColor: border,
      }}
    >
      {risk} Risk
    </span>
  );
};
