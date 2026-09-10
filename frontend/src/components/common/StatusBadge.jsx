import React from 'react';

export const StatusBadge = ({ status }) => {
  if (!status) return null;

  const normalized = status.toLowerCase();

  let badgeClass = 'badge-draft';
  if (normalized.includes('review')) {
    badgeClass = 'badge-under-review';
  } else if (normalized.includes('approve')) {
    badgeClass = 'badge-approved';
  } else if (normalized.includes('reject')) {
    badgeClass = 'badge-rejected';
  } else if (normalized.includes('archive')) {
    badgeClass = 'badge-archived';
  }

  return (
    <span className={`badge ${badgeClass}`}>
      <span className="badge-dot"></span>
      {status}
    </span>
  );
};

export const RiskBadge = ({ risk }) => {
  if (!risk) return null;
  const normalized = risk.toLowerCase();

  let badgeClass = 'badge-risk-medium';
  if (normalized.includes('low')) badgeClass = 'badge-risk-low';
  if (normalized.includes('high')) badgeClass = 'badge-risk-high';

  return (
    <span className={`badge ${badgeClass}`}>
      {risk} Risk
    </span>
  );
};

export const RoleBadge = ({ role }) => {
  if (!role) return null;
  const normalized = role.toLowerCase();

  let badgeClass = 'badge-role-employee';
  if (normalized.includes('admin')) badgeClass = 'badge-role-admin';
  if (normalized.includes('manager')) badgeClass = 'badge-role-manager';
  if (normalized.includes('reviewer')) badgeClass = 'badge-role-reviewer';

  return (
    <span className={`badge ${badgeClass}`}>
      {role}
    </span>
  );
};
