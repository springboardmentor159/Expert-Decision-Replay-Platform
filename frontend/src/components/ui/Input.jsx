export default function Input({ label, error, hint, id, className = "", ...rest }) {
  const inputId = id || rest.name;
  return (
    <div className="field">
      {label && (
        <label htmlFor={inputId}>
          {label}
          {rest.required && <span className="required">*</span>}
        </label>
      )}
      <input id={inputId} className={`input ${error ? "input-error" : ""} ${className}`} {...rest} />
      {hint && !error && <div className="field-hint">{hint}</div>}
      {error && <div className="field-error">{error}</div>}
    </div>
  );
}
