import type { ReactNode } from "react";

import Navigation from "../components/Navigation";

interface AppLayoutProps {
  children: ReactNode;
}

export default function AppLayout({ children }: AppLayoutProps) {
  return (
    <div className="app-layout">
      <Navigation />

      <main className="app-main">{children}</main>
    </div>
  );
}