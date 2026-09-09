export function formatDate(value) {
  if (!value) return "-";
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return "-";
  return d.toLocaleString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function formatCurrency(value) {
  if (value === null || value === undefined) return "-";
  return new Intl.NumberFormat(undefined, { style: "currency", currency: "USD" }).format(value);
}

export const DECISION_STATUSES = ["Draft", "Under Review", "Approved", "Rejected", "Archived"];
export const RISK_LEVELS = ["Low", "Medium", "High", "Critical"];
