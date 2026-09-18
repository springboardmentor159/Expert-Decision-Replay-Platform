import type { ReactNode } from "react";

export interface AlertProps {
  variant?: "info" | "success" | "warning" | "error";
  children: ReactNode;
}

export default function Alert({
  variant = "info",
  children,
}: AlertProps) {
  return (
    <div
      className={`alert alert-${variant}`}
      role={variant === "error" ? "alert" : "status"}
    >
      {children}
    </div>
  );
}