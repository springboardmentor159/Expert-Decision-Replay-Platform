export default function Select({ label, error, id, options, placeholder, className = "", ...rest }) {
  const inputId = id || rest.name;
  return (
    <div className="field">
      {label && (
        <label htmlFor={inputId}>
          {label}
          {rest.required && <span className="required">*</span>}
        </label>
      )}
      <select id={inputId} className={`input ${error ? "input-error" : ""} ${className}`} {...rest}>
        {placeholder && <option value="">{placeholder}</option>}
        {options.map((opt) => (
          <option key={opt.value ?? opt} value={opt.value ?? opt}>
            {opt.label ?? opt}
          </option>
        ))}
      </select>
      {error && <div className="field-error">{error}</div>}
    </div>
  );
}
