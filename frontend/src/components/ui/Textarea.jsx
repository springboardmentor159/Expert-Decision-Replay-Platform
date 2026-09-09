export default function Textarea({ label, error, id, className = "", ...rest }) {
  const inputId = id || rest.name;
  return (
    <div className="field">
      {label && (
        <label htmlFor={inputId}>
          {label}
          {rest.required && <span className="required">*</span>}
        </label>
      )}
      <textarea id={inputId} className={`input textarea ${error ? "input-error" : ""} ${className}`} {...rest} />
      {error && <div className="field-error">{error}</div>}
    </div>
  );
}
