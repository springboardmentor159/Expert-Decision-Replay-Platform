import { NavLink } from "react-router-dom";
import { NAV_BY_ROLE } from "../../utils/roles";
import { useAuth } from "../../context/AuthContext";

export default function Sidebar() {
  const { user } = useAuth();
  const items = NAV_BY_ROLE[user?.role] || [];

  return (
    <aside className="sidebar">
      <nav>
        {items.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) => `sidebar-link ${isActive ? "active" : ""}`}
          >
            {item.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
