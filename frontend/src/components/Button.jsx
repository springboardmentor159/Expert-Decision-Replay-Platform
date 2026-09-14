const Button = ({
  children,
  onClick,
  type = "button",
  variant = "primary",
  disabled = false,
}) => {
  return (
    <button
      type={type}
      className={`app-button ${variant}`}
      onClick={onClick}
      disabled={disabled}
    >
      {children}
    </button>
  );
};

export default Button;