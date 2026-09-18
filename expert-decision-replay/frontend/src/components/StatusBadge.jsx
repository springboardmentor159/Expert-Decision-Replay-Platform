const StatusBadge = ({ status = "Unknown" }) => {
  const normalizedStatus = String(status).toLowerCase();

  const statusStyles = {
    pending: "bg-yellow-100 text-yellow-800",
    approved: "bg-green-100 text-green-800",
    rejected: "bg-red-100 text-red-800",
    draft: "bg-gray-100 text-gray-800",
    completed: "bg-blue-100 text-blue-800",
    active: "bg-green-100 text-green-800",
    inactive: "bg-gray-100 text-gray-800",
    under_review: "bg-purple-100 text-purple-800",
  };

  const badgeStyle =
    statusStyles[normalizedStatus] ||
    "bg-gray-100 text-gray-800";

  return (
    <span
      className={`inline-flex rounded-full px-3 py-1 text-xs font-semibold capitalize ${badgeStyle}`}
    >
      {String(status).replaceAll("_", " ")}
    </span>
  );
};

export default StatusBadge;