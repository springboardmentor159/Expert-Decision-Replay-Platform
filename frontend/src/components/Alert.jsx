const Alert = ({
  message,
  type = "error",
  onClose,
}) => {
  if (!message) {
    return null;
  }

  return (
    <div className={`alert alert-${type}`}>

      <span>{message}</span>

      {onClose && (
        <button
          className="alert-close"
          onClick={onClose}
        >
          ×
        </button>
      )}

    </div>
  );
};

export default Alert;