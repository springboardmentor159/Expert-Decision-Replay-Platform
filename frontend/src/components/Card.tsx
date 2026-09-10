import type { ReactNode } from "react";

interface CardProps {
  children: ReactNode;
  title?: string;
  description?: string;
  className?: string;
}

export default function Card({
  children,
  title,
  description,
  className = "",
}: CardProps) {
  return (
    <section className={`card ${className}`}>
      {(title || description) && (
        <header className="card-header">
          {title && <h2 className="card-title">{title}</h2>}

          {description && (
            <p className="card-description">{description}</p>
          )}
        </header>
      )}

      <div className="card-content">{children}</div>
    </section>
  );
}