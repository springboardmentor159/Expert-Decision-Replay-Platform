import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";
import { ROLES } from "../utils/roles";

const navigationByRole = {
  [ROLES.EMPLOYEE]: [
    { label: "Dashboard", path: "/dashboard" },
    { label: "My Decisions", path: "/decisions" },
    { label: "Create Decision", path: "/decisions/create" },
    { label: "Discussions", path: "/decisions/20/discussions" },
    { label: "Knowledge Repository", path: "/knowledge-repository" },
  ],

  [ROLES.REVIEWER]: [
    { label: "Dashboard", path: "/dashboard" },
    { label: "Assigned Reviews", path: "/approvals" },
    { label: "Decisions", path: "/decisions" },
    { label: "Alternatives", path: "/decisions/20/alternatives" },
    { label: "Discussions", path: "/decisions/20/discussions" },
  ],

  [ROLES.MANAGER]: [
    { label: "Dashboard", path: "/dashboard" },
    { label: "Team Decisions", path: "/decisions" },
    { label: "Pending Approvals", path: "/approvals" },
    { label: "Decision Analytics", path: "/analytics" },
    { label: "Reports", path: "/reports" },
  ],

  [ROLES.ADMINISTRATOR]: [
    { label: "Dashboard", path: "/dashboard" },
    { label: "User Management", path: "/users" },
    { label: "Decisions", path: "/decisions" },
    { label: "Audit Logs", path: "/audit" },
    { label: "Reports", path: "/reports" },
    { label: "System Information", path: "/system" },
  ],
};

function DashboardLayout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const navigationItems =
    navigationByRole[user?.role] || [];

  const handleLogout = () => {
    logout();
    navigate("/login", { replace: true });
  };

  return (
    <div className="app-layout">
      <aside className="sidebar">
        <div className="sidebar-brand">
          <h2>Expert Decision Replay</h2>
          <span>Decision Intelligence Platform</span>
        </div>

        <div className="user-summary">
          <div className="user-avatar">
            {user?.email?.charAt(0).toUpperCase() || "U"}
          </div>

          <div>
            <strong>{user?.email || "User"}</strong>
            <span>{user?.role || "User"}</span>
          </div>
        </div>

        <nav className="sidebar-nav">
          {navigationItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                isActive
                  ? "nav-link active"
                  : "nav-link"
              }
            >
              {item.label}
            </NavLink>
          ))}
        </nav>

        <div className="sidebar-bottom">
          <button
            type="button"
            className="logout-button"
            onClick={handleLogout}
          >
            Logout
          </button>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div>
            <h1>Expert Decision Replay</h1>
          </div>

          <div className="topbar-user">
            <span>{user?.email}</span>
            <span className="role-badge">
              {user?.role}
            </span>
          </div>
        </header>

        <section className="page-content">
          <Outlet />
        </section>
      </main>
    </div>
  );
}

export default DashboardLayout;