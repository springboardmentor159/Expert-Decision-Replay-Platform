import { Link, useLocation } from "react-router-dom";
import { getStoredUser } from "../auth/authService";

function Sidebar() {
  const location = useLocation();
  const user = getStoredUser();

  const role = user?.role || "Employee";

  const menuItems = {
    Employee: [
      { name: "Dashboard", path: "/dashboard" },
      { name: "My Decisions", path: "/decisions" },
      { name: "Create Decision", path: "/create-decision" },
      { name: "Knowledge Repository", path: "/knowledge" },
      { name: "Discussions", path: "/discussions" },
      { name: "Reports", path: "/reports"},
      { name: "Profile", path: "/profile" },
    ],

    Reviewer: [
      { name: "Dashboard", path: "/dashboard" },
      { name: "Assigned Reviews", path: "/reviews" },
      { name: "Decision Details", path: "/decisions" },
      { name: "Discussions", path: "/discussions" },
      { name: "Review Actions", path: "/reviews/actions" },
    ],

    Manager: [
      { name: "Dashboard", path: "/dashboard" },
      { name: "Team Decisions", path: "/team-decisions" },
      { name: "Pending Approvals", path: "/approvals" },
      { name: "Reports", path: "/reports" },
      { name: "Decision Statistics", path: "/statistics" },
    ],

    HR: [
      { name: "Dashboard", path: "/dashboard" },
      { name: "Employee Management", path: "/employees" },
      { name: "Team Decisions", path: "/team-decisions" },
      { name: "Reports", path: "/reports" },
      { name: "Activity", path: "/activity" },
      { name: "Profile", path: "/profile" },
    ],

    Administrator: [
      { name: "Admin Dashboard", path: "/dashboard" },
      { name: "User Management", path: "/users" },
      { name: "Audit Logs", path: "/audit-logs" },
      { name: "Reports", path: "/reports" },
      { name: "System Activity", path: "/activity" },
    ],
  };

  const items = menuItems[role] || menuItems.Employee;

  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <h2>Expert Decision</h2>
        <span>Replay Platform</span>
      </div>

      <nav className="sidebar-nav">
        {items.map((item) => {
          const active = location.pathname === item.path;

          return (
            <Link
              key={item.path}
              to={item.path}
              className={active ? "nav-link active" : "nav-link"}
            >
              {item.name}
            </Link>
          );
        })}
      </nav>

      <div className="sidebar-role">
        <small>Logged in as</small>
        <strong>{role}</strong>
      </div>
    </aside>
  );
}

export default Sidebar;