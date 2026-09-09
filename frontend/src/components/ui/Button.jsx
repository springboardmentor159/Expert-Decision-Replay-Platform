export default function Button({ children, variant = "primary", size = "md", loading = false, disabled, className = "", ...rest }) {
  const classes = ["btn", `btn-${variant}`, `btn-${size}`, className].join(" ");
  return (
    <button className={classes} disabled={disabled || loading} {...rest}>
      {loading ? "Please wait…" : children}
    </button>
  );
}
