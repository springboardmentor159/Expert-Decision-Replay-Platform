export default function EmptyState({ title = "Nothing here yet", description, action }) {
  return (
    <div className="state-block empty-state">
      <p className="empty-title">{title}</p>
      {description && <p className="empty-desc">{description}</p>}
      {action}
    </div>
  );
}
