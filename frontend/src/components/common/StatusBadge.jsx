import React from 'react';
import { Clock, CheckCircle, XCircle, FileText, Archive, Shield } from 'lucide-react';

export function StatusBadge({ status }) {
  if (!status) return null;
  const s = typeof status === 'string' ? status.toLowerCase() : '';

  if (s === 'draft') {
    return (
      <span className="badge badge-draft">
        <FileText size={12} />
        Draft
      </span>
    );
  }

  if (s === 'under review' || s === 'under_review') {
    return (
      <span className="badge badge-review">
        <Clock size={12} />
        Under Review
      </span>
    );
  }

  if (s === 'approved') {
    return (
      <span className="badge badge-approved">
        <CheckCircle size={12} />
        Approved
      </span>
    );
  }

  if (s === 'rejected') {
    return (
      <span className="badge badge-rejected">
        <XCircle size={12} />
        Rejected
      </span>
    );
  }

  if (s === 'archived') {
    return (
      <span className="badge badge-archived">
        <Archive size={12} />
        Archived
      </span>
    );
  }

  return <span className="badge badge-role">{status}</span>;
}

export function RoleBadge({ role }) {
  if (!role) return null;
  return (
    <span className="badge badge-role">
      <Shield size={12} />
      {role}
    </span>
  );
}

export function RiskBadge({ level }) {
  if (!level) return null;
  const l = level.toLowerCase();
  let cls = 'badge-review';
  if (l === 'low') cls = 'badge-approved';
  if (l === 'high') cls = 'badge-rejected';
  if (l === 'medium') cls = 'badge-draft';

  return (
    <span className={`badge ${cls}`}>
      {level} Risk
    </span>
  );
}
