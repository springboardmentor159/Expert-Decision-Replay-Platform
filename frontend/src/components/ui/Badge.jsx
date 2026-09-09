const STATUS_TONES = {
  Draft: "gray",
  "Under Review": "blue",
  Approved: "green",
  Rejected: "red",
  Archived: "purple",
  Pending: "blue",
  Open: "blue",
  Resolved: "green",
  Closed: "gray",
  Low: "green",
  Medium: "blue",
  High: "orange",
  Critical: "red",
};

export default function Badge({ children, tone }) {
  const resolvedTone = tone || STATUS_TONES[children] || "gray";
  return <span className={`badge badge-${resolvedTone}`}>{children}</span>;
}
