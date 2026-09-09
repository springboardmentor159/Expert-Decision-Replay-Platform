export default function Alert({ type = "info", children, onClose }) {
  if (!children) return null;
  return (
    <div className={`alert alert-${type}`}>
      <span>{children}</span>
      {onClose && (
        <button className="alert-close" onClick={onClose} aria-label="Dismiss">
          ×
        </button>
      )}
    </div>
  );
}
