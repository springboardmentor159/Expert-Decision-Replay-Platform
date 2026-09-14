const StatusBadge = ({ status }) => {
  const normalizedStatus = status
    ? status.toLowerCase().replace(/\s+/g, "-")
    : "unknown";

  return (
    <span
      className={`status-badge status-${normalizedStatus}`}
    >
      {status || "Unknown"}
    </span>
  );
};

export default StatusBadge;