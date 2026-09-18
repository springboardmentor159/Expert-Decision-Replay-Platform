import { NavLink } from "react-router-dom";

const menuItems = [
  {
    name: "Dashboard",
    path: "/dashboard",
    icon: "▦",
  },
  {
    name: "Decisions",
    path: "/decisions",
    icon: "▤",
  },
  {
    name: "Create Decision",
    path: "/create-decision",
    icon: "+",
  },
  {
    name: "Alternatives",
    path: "/alternatives",
    icon: "⇄",
  },
  {
    name: "Knowledge Repository",
    path: "/knowledge-repository",
    icon: "▣",
  },
  {
    name: "Audit Logs",
    path: "/audit-logs",
    icon: "◷",
  },
  {
    name: "Notifications",
    path: "/notifications",
    icon: "♧",
  },
  {
    name: "Reports",
    path: "/reports",
    icon: "▥",
  },
  {
    name: "Teams",
    path: "/teams",
    icon: "♙",
  },
];

const Sidebar = () => {
  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <div className="brand-icon">ED</div>

        <div>
          <h2>Expert Decision</h2>
          <span>Replay Platform</span>
        </div>
      </div>

      <nav className="sidebar-nav">
        <p className="nav-heading">MAIN MENU</p>

        {menuItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              isActive ? "nav-link active" : "nav-link"
            }
          >
            <span className="nav-icon">{item.icon}</span>
            <span>{item.name}</span>
          </NavLink>
        ))}
      </nav>

      <div className="sidebar-footer">
        <span className="footer-dot"></span>
        <span>Decision Management System</span>
      </div>
    </aside>
  );
};

export default Sidebar;