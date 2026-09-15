import { NavLink, Outlet, useNavigate } from "react-router-dom";

function Layout() {
  const navigate = useNavigate();

  const user = JSON.parse(localStorage.getItem("user") || "{}");

  const userName =
    user?.full_name ||
    user?.name ||
    user?.email?.split("@")[0] ||
    "User";

  const role = user?.role || "Employee";

  const navItems = [
    { name: "Dashboard", icon: "⌂", path: "/dashboard" },
    { name: "Decisions", icon: "▣", path: "/decisions" },
    { name: "Create Decision", icon: "+", path: "/decisions/create" },
    { name: "Knowledge Repository", icon: "▤", path: "/knowledge" },
    { name: "Approvals", icon: "✓", path: "/decisions/1/approvals" },
    { name: "Audit Logs", icon: "◉", path: "/audit-logs" },
    { name: "Reports", icon: "▥", path: "/reports" },
  ];

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    navigate("/login");
    window.location.reload();
  };

  return (
    <div className="app-layout">

      {/* SIDEBAR */}
      <aside className="sidebar">

        <div className="sidebar-logo">
          <div className="logo-icon">ED</div>

          <div>
            <h2>Expert Decision</h2>
            <span>Replay Platform</span>
          </div>
        </div>

        <div className="menu-title">
          MAIN MENU
        </div>

        <nav className="sidebar-menu">

          {navItems.map((item) => (
            <NavLink
              key={item.name}
              to={item.path}
              className={({ isActive }) =>
                `sidebar-link ${isActive ? "active" : ""}`
              }
            >
              <span className="menu-icon">
                {item.icon}
              </span>

              <span>{item.name}</span>
            </NavLink>
          ))}

          <div className="menu-title secondary-title">
            DECISION TOOLS
          </div>

          <NavLink
            to="/decisions/1/alternatives"
            className={({ isActive }) =>
              `sidebar-link ${isActive ? "active" : ""}`
            }
          >
            <span className="menu-icon">↔</span>
            <span>Alternatives</span>
          </NavLink>

          <NavLink
            to="/decisions/1/alternatives/compare"
            className={({ isActive }) =>
              `sidebar-link ${isActive ? "active" : ""}`
            }
          >
            <span className="menu-icon">⇄</span>
            <span>Compare Alternatives</span>
          </NavLink>

          <NavLink
            to="/decisions/1/comments"
            className={({ isActive }) =>
              `sidebar-link ${isActive ? "active" : ""}`
            }
          >
            <span className="menu-icon">☷</span>
            <span>Discussions</span>
          </NavLink>

          <NavLink
            to="/decisions/1/history"
            className={({ isActive }) =>
              `sidebar-link ${isActive ? "active" : ""}`
            }
          >
            <span className="menu-icon">◷</span>
            <span>Version History</span>
          </NavLink>

        </nav>

        {/* SIDEBAR BOTTOM */}
        <div className="sidebar-bottom">

          <div className="user-mini">

            <div className="avatar">
              {userName.charAt(0).toUpperCase()}
            </div>

            <div className="user-info">
              <strong>{userName}</strong>
              <span>{role}</span>
            </div>

          </div>

          <button
            className="logout-button"
            onClick={handleLogout}
          >
            <span>↪</span>
            Logout
          </button>

        </div>

      </aside>

      {/* MAIN AREA */}
      <main className="main-area">

        {/* TOP HEADER */}
        <header className="top-header">

          <div className="breadcrumb">
            Workspace
          </div>

          <div className="header-right">

            <div className="search-box">
              <span>⌕</span>
              <input
                type="text"
                placeholder="Search decisions..."
              />
            </div>

            <button className="notification-button">
              ♢
              <span className="notification-dot"></span>
            </button>

            <div className="profile-area">

              <div className="profile-avatar">
                {userName.charAt(0).toUpperCase()}
              </div>

              <div className="profile-details">
                <strong>{userName}</strong>
                <span>{role}</span>
              </div>

            </div>

          </div>

        </header>

        {/* PAGE CONTENT */}
        <section className="page-container">
          <Outlet />
        </section>

      </main>

    </div>
  );
}

export default Layout;