export default function StatCard({ label, value, tone = "default" }) {
  return (
    <div className={`stat-card stat-${tone}`}>
      <div className="stat-value">{value ?? "-"}</div>
      <div className="stat-label">{label}</div>
    </div>
  );
}
