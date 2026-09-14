const EmptyState = ({
  title = "No data found",
  message = "There is nothing to display.",
  action,
}) => {
  return (
    <div className="empty-state">

      <div className="empty-state-icon">
        ◌
      </div>

      <h3>{title}</h3>

      <p>{message}</p>

      {action && (
        <div className="empty-state-action">
          {action}
        </div>
      )}

    </div>
  );
};

export default EmptyState;