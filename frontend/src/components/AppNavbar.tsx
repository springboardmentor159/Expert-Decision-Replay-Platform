import {
  Activity,
  BarChart3,
  ClipboardList,
  LayoutDashboard,
  LogOut,
} from "lucide-react";
import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../context/useAuth";

export default function AppNavbar() {
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  const handleLogout = async () => {
    await logout();
    navigate("/login");
  };

  return (
    <header className="app-navbar">
      <div className="app-navbar-inner">
        {/* Brand */}
        <button
          type="button"
          className="app-navbar-brand"
          onClick={() => navigate("/dashboard")}
        >
          <div className="app-navbar-logo">
            <BarChart3 size={20} strokeWidth={2.2} />
          </div>

          <div className="app-navbar-brand-text">
            <span className="app-navbar-brand-title">
              Expert Decision
            </span>

            <span className="app-navbar-brand-subtitle">
              Replay Platform
            </span>
          </div>
        </button>

        {/* Main Navigation */}
        <nav className="app-navbar-nav">
          <NavLink
            to="/dashboard"
            className={({ isActive }) =>
              `app-nav-link ${isActive ? "active" : ""}`
            }
          >
            <LayoutDashboard size={18} />
            <span>Dashboard</span>
          </NavLink>

          <NavLink
            to="/decisions"
            className={({ isActive }) =>
              `app-nav-link ${isActive ? "active" : ""}`
            }
          >
            <ClipboardList size={18} />
            <span>Decisions</span>
          </NavLink>

          <NavLink
            to="/audit-activity"
            className={({ isActive }) =>
              `app-nav-link ${isActive ? "active" : ""}`
            }
          >
            <Activity size={18} />
            <span>Audit & Activity</span>
          </NavLink>
        </nav>

        {/* User Area */}
        <div className="app-navbar-user-area">
          <div className="app-navbar-user">
            <div className="app-navbar-avatar">
              {user?.full_name?.charAt(0).toUpperCase() || "U"}
            </div>

            <div className="app-navbar-user-info">
              <span className="app-navbar-user-name">
                {user?.full_name || "User"}
              </span>

              <span className="app-navbar-user-role">
                {user?.role || "User"}
              </span>
            </div>
          </div>

          <button
            type="button"
            className="app-navbar-logout"
            onClick={handleLogout}
            title="Logout"
          >
            <LogOut size={18} />
            <span>Logout</span>
          </button>
        </div>
      </div>
    </header>
  );
}