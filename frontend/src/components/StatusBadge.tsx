import type { ReactNode } from "react";

type StatusVariant =
  | "success"
  | "warning"
  | "danger"
  | "info"
  | "neutral";

interface StatusBadgeProps {
  children: ReactNode;
  variant?: StatusVariant;
}

export default function StatusBadge({
  children,
  variant = "neutral",
}: StatusBadgeProps) {
  return (
    <span className={`status-badge status-badge-${variant}`}>
      {children}
    </span>
  );
}