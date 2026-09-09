import { Link, NavLink, Outlet, useNavigate } from "react-router-dom";
import { useContext } from "react";

import { AuthContext } from "../context/AuthContext";

function DashboardLayout({ children }) {
  const navigate = useNavigate();
  const { user, logout } = useContext(AuthContext);

  const role = user?.role || "";

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  const getNavItems = () => {
    switch (role) {
      case "Employee":
        return [
          {
            label: "Dashboard",
            path: "/dashboard",
          },
          {
            label: "My Decisions",
            path: "/decisions",
          },
          {
            label: "Create Decision",
            path: "/decisions/create",
          },
          {
            label: "Discussions",
            path: "/discussions",
          },
          {
            label: "Knowledge Repository",
            path: "/knowledge-repository",
          },
        ];

      case "Reviewer":
        return [
          {
            label: "Dashboard",
            path: "/dashboard",
          },
          {
            label: "Assigned Reviews",
            path: "/approvals",
          },
          {
            label: "Decisions",
            path: "/decisions",
          },
          {
            label: "Alternatives",
            path: "/alternatives",
          },
          {
            label: "Discussions",
            path: "/discussions",
          },
        ];

      case "Manager":
        return [
          {
            label: "Dashboard",
            path: "/dashboard",
          },
          {
            label: "Team Decisions",
            path: "/decisions",
          },
          {
            label: "Pending Approvals",
            path: "/approvals",
          },
          {
            label: "Decision Analytics",
            path: "/analytics",
          },
          {
            label: "Reports",
            path: "/reports",
          },
        ];

      case "Administrator":
        return [
          {
            label: "Dashboard",
            path: "/dashboard",
          },
          {
            label: "User Management",
            path: "/users",
          },
          {
            label: "Decisions",
            path: "/decisions",
          },
          {
            label: "Audit Logs",
            path: "/audit",
          },
          {
            label: "Reports",
            path: "/reports",
          },
          {
            label: "System Information",
            path: "/system",
          },
        ];

      default:
        return [
          {
            label: "Dashboard",
            path: "/dashboard",
          },
        ];
    }
  };

  const navItems = getNavItems();

  return (
    <div className="dashboard-layout">
      <aside className="sidebar">
        <div className="sidebar-header">
          <Link
            to="/dashboard"
            className="sidebar-logo"
          >
            Expert Decision Replay
          </Link>
        </div>

        <div className="sidebar-user">
          <div className="sidebar-user-name">
            {user?.name ||
              user?.full_name ||
              user?.email ||
              "User"}
          </div>

          <div className="sidebar-user-role">
            {role || "User"}
          </div>
        </div>

        <nav className="sidebar-nav">
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `sidebar-nav-link ${
                  isActive ? "active" : ""
                }`
              }
            >
              {item.label}
            </NavLink>
          ))}
        </nav>

        <div className="sidebar-footer">
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
        {children || <Outlet />}
      </main>
    </div>
  );
}

export default DashboardLayout;