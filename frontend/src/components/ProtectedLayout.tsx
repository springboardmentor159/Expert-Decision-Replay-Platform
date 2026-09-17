import { Outlet } from "react-router-dom";
import AppNavbar from "./AppNavbar";

export default function ProtectedLayout() {
  return (
    <div className="app-shell">
      <AppNavbar />

      <main className="app-main">
        <Outlet />
      </main>
    </div>
  );
}