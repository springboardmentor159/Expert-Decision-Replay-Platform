import {
  LayoutDashboard,
  Users,
  FileText,
  Plus,
  MessageSquare,
  BookOpen,
  ClipboardCheck,
  ArrowLeftRight,
  BarChart3,
  FileBarChart,
  ShieldCheck,
  Settings,
  History,
  LogOut,
  Bell,
  UserRound,
} from "lucide-react";

import {
  Link,
  NavLink,
  Outlet,
  useNavigate,
} from "react-router-dom";

import { useContext } from "react";

import { AuthContext } from "../context/AuthContext";

const roleLabels = {
  Employee: "Employee",
  Reviewer: "Reviewer",
  Manager: "Manager",
  Administrator: "Administrator",
};

const roleInitials = {
  Employee: "EM",
  Reviewer: "RV",
  Manager: "MG",
  Administrator: "AD",
};

function DashboardLayout({ children }) {
  const navigate = useNavigate();

  const { user, logout } =
    useContext(AuthContext);

  const role = user?.role || "";

  const displayName =
    user?.name ||
    user?.full_name ||
    user?.email ||
    "User";

  const displayRole =
    roleLabels[role] || role || "User";

  const initials =
    roleInitials[role] ||
    displayName
      .split(" ")
      .map((part) => part.charAt(0))
      .join("")
      .slice(0, 2)
      .toUpperCase();

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
            icon: LayoutDashboard,
          },
          {
            label: "My Decisions",
            path: "/decisions",
            icon: FileText,
          },
          {
            label: "Create Decision",
            path: "/decisions/create",
            icon: Plus,
          },
          {
            label: "Discussions",
            path: "/discussions",
            icon: MessageSquare,
          },
          {
            label: "Knowledge Repository",
            path: "/knowledge-repository",
            icon: BookOpen,
          },
        ];

      case "Reviewer":
        return [
          {
            label: "Dashboard",
            path: "/dashboard",
            icon: LayoutDashboard,
          },
          {
            label: "Assigned Reviews",
            path: "/approvals",
            icon: ClipboardCheck,
          },
          {
            label: "Decisions",
            path: "/decisions",
            icon: FileText,
          },
          {
            label: "Alternatives",
            path: "/alternatives",
            icon: ArrowLeftRight,
          },
          {
            label: "Discussions",
            path: "/discussions",
            icon: MessageSquare,
          },
        ];

      case "Manager":
        return [
          {
            label: "Dashboard",
            path: "/dashboard",
            icon: LayoutDashboard,
          },
          {
            label: "Team Decisions",
            path: "/decisions",
            icon: FileText,
          },
          {
            label: "Pending Approvals",
            path: "/approvals",
            icon: ClipboardCheck,
          },
          {
            label: "Decision Analytics",
            path: "/analytics",
            icon: BarChart3,
          },
          {
            label: "Reports",
            path: "/reports",
            icon: FileBarChart,
          },
        ];

      case "Administrator":
        return [
          {
            label: "Dashboard",
            path: "/dashboard",
            icon: LayoutDashboard,
          },
          {
            label: "User Management",
            path: "/users",
            icon: Users,
          },
          {
            label: "Decisions",
            path: "/decisions",
            icon: FileText,
          },
          {
            label: "Audit Logs",
            path: "/audit",
            icon: History,
          },
          {
            label: "Reports",
            path: "/reports",
            icon: FileBarChart,
          },
          {
            label: "System Information",
            path: "/system",
            icon: Settings,
          },
        ];

      default:
        return [
          {
            label: "Dashboard",
            path: "/dashboard",
            icon: LayoutDashboard,
          },
        ];
    }
  };

  const navItems = getNavItems();

  return (
    <div className="dashboard-layout">

      {/* ==================================================
          SIDEBAR
      =================================================== */}

      <aside className="sidebar">

        {/* ---------- Logo ---------- */}

        <div className="sidebar-header">

          <Link
            to="/dashboard"
            className="sidebar-logo"
          >
            <span className="logo-mark">
              E
            </span>

            <span className="logo-text">
              Expert Decision
              <strong>Replay</strong>
            </span>
          </Link>

        </div>


        {/* ---------- Main Menu ---------- */}

        <div className="sidebar-section-title">
          MAIN MENU
        </div>

        <nav className="sidebar-nav">

          {navItems.map((item) => {
            const Icon = item.icon;

            return (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  `sidebar-nav-link ${
                    isActive ? "active" : ""
                  }`
                }
              >

                <span className="nav-icon">
                  <Icon
                    size={17}
                    strokeWidth={2}
                  />
                </span>

                <span className="nav-label">
                  {item.label}
                </span>

              </NavLink>
            );
          })}

        </nav>


        {/* ---------- Sidebar User ---------- */}

        <div className="sidebar-bottom">

          <div className="sidebar-user-card">

            <div className="user-avatar">
              {initials}
            </div>

            <div className="sidebar-user-info">

              <div className="sidebar-user-name">
                {displayName}
              </div>

              <div className="sidebar-user-role">
                {displayRole}
              </div>

            </div>

          </div>


          <button
            type="button"
            className="logout-button"
            onClick={handleLogout}
          >

            <span className="logout-icon">
              <LogOut
                size={15}
                strokeWidth={2}
              />
            </span>

            <span>
              Logout
            </span>

          </button>

        </div>

      </aside>


      {/* ==================================================
          MAIN AREA
      =================================================== */}

      <div className="main-area">

        {/* ---------- Top Header ---------- */}

        <header className="top-header">

          <div className="header-left">

            <span className="header-page-label">
              Expert Decision Replay
            </span>

          </div>


          <div className="header-right">

            <button
              type="button"
              className="notification-button"
              aria-label="Notifications"
              title="Notifications"
            >
              <Bell
                size={17}
                strokeWidth={1.8}
              />
            </button>


            <div className="header-user">

              <div className="header-avatar">

                {initials}

              </div>


              <div className="header-user-details">

                <span className="header-user-name">
                  {displayName}
                </span>

                <span className="header-user-role">
                  {displayRole}
                </span>

              </div>

            </div>

          </div>

        </header>


        {/* ---------- Main Content ---------- */}

        <main className="main-content">
          {children || <Outlet />}
        </main>

      </div>

    </div>
  );
}

export default DashboardLayout;