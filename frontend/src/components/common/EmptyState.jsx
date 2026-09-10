import React from 'react';
import { Inbox } from 'lucide-react';

export const EmptyState = ({
  icon: Icon = Inbox,
  title = 'No items found',
  description = 'There are no records to display at this time.',
  actionText,
  onAction,
}) => {
  return (
    <div className="empty-state">
      <div className="empty-icon-halo">
        <Icon size={30} />
      </div>
      <h3 className="empty-title">{title}</h3>
      <p className="empty-description">{description}</p>
      {actionText && onAction && (
        <button className="btn btn-primary btn-sm" onClick={onAction}>
          {actionText}
        </button>
      )}
    </div>
  );
};
