import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";


const Sidebar = () => {
  const { user, role, logout } = useAuth();
  const navigate = useNavigate();


  const isManager =
    role === "Manager";

  const isAdmin =
    role === "Administrator";

  const canManageTeams =
    isManager || isAdmin;


  const handleLogout = () => {
    logout();
    navigate("/login", { replace: true });
  };


  return (
    <aside className="sidebar">

      {/* =====================================================
          BRAND
      ===================================================== */}

      <div className="sidebar-brand">

        <div className="sidebar-brand-logo">
          ED
        </div>

        <div className="sidebar-brand-text">

          <strong>
            Decision Replay
          </strong>

          <span>
            {role || "User"}
          </span>

        </div>

      </div>


      {/* =====================================================
          MAIN MENU
      ===================================================== */}

      <div className="sidebar-section">

        <div className="sidebar-section-title">
          MAIN MENU
        </div>


        <NavLink
          to="/dashboard"
          className={({ isActive }) =>
            `sidebar-link ${
              isActive ? "active" : ""
            }`
          }
        >
          <span className="sidebar-icon">
            ⌂
          </span>

          <span>
            Dashboard
          </span>
        </NavLink>


        {/* My Decisions */}
        <NavLink
          to="/my-decisions"
          className={({ isActive }) =>
            `sidebar-link ${
              isActive ? "active" : ""
            }`
          }
        >
          <span className="sidebar-icon">
            ▣
          </span>

          <span>
            My Decisions
          </span>
        </NavLink>


        <NavLink
          to="/decisions/create"
          className={({ isActive }) =>
            `sidebar-link ${
              isActive ? "active" : ""
            }`
          }
        >
          <span className="sidebar-icon">
            +
          </span>

          <span>
            Create Decision
          </span>
        </NavLink>


        <NavLink
          to="/repository"
          className={({ isActive }) =>
            `sidebar-link ${
              isActive ? "active" : ""
            }`
          }
        >
          <span className="sidebar-icon">
            ▤
          </span>

          <span>
            Knowledge Repository
          </span>
        </NavLink>


        <NavLink
          to="/reports"
          className={({ isActive }) =>
            `sidebar-link ${
              isActive ? "active" : ""
            }`
          }
        >
          <span className="sidebar-icon">
            ▥
          </span>

          <span>
            Reports
          </span>
        </NavLink>

      </div>


      {/* =====================================================
          COLLABORATION
      ===================================================== */}

      <div className="sidebar-section">

        <div className="sidebar-section-title">
          COLLABORATION
        </div>


        {/* No hardcoded decision ID */}

        <NavLink
          to="/decisions"
          className={({ isActive }) =>
            `sidebar-link ${
              isActive ? "active" : ""
            }`
          }
        >
          <span className="sidebar-icon">
            ☷
          </span>

          <span>
            Discussions
          </span>
        </NavLink>

      </div>


      {/* =====================================================
          WORKFLOW
      ===================================================== */}

      <div className="sidebar-section">

        <div className="sidebar-section-title">
          WORKFLOW
        </div>


        {(role === "Reviewer" ||
          role === "Manager" ||
          role === "Administrator") && (

          <NavLink
            to="/approvals"
            className={({ isActive }) =>
              `sidebar-link ${
                isActive ? "active" : ""
              }`
            }
          >
            <span className="sidebar-icon">
              ✓
            </span>

            <span>
              Approvals
            </span>
          </NavLink>

        )}

      </div>


      {/* =====================================================
          MANAGEMENT
      ===================================================== */}

      {canManageTeams && (

        <div className="sidebar-section">

          <div className="sidebar-section-title">
            MANAGEMENT
          </div>


          <NavLink
            to="/teams"
            className={({ isActive }) =>
              `sidebar-link ${
                isActive ? "active" : ""
              }`
            }
          >
            <span className="sidebar-icon">
              ♟
            </span>

            <span>
              Teams
            </span>
          </NavLink>

        </div>

      )}


      {/* =====================================================
          ADMINISTRATION
      ===================================================== */}

      {isAdmin && (

        <div className="sidebar-section">

          <div className="sidebar-section-title">
            ADMINISTRATION
          </div>


          <NavLink
            to="/audit"
            className={({ isActive }) =>
              `sidebar-link ${
                isActive ? "active" : ""
              }`
            }
          >
            <span className="sidebar-icon">
              ◫
            </span>

            <span>
              Audit Logs
            </span>
          </NavLink>

        </div>

      )}


      {/* =====================================================
          BOTTOM MENU
      ===================================================== */}

      <div className="sidebar-bottom">

        <NavLink
          to="/profile"
          className={({ isActive }) =>
            `sidebar-link ${
              isActive ? "active" : ""
            }`
          }
        >
          <span className="sidebar-icon">
            ♙
          </span>

          <span>
            My Profile
          </span>
        </NavLink>


        <button
          type="button"
          className="sidebar-link sidebar-logout"
          onClick={handleLogout}
        >

          <span className="sidebar-icon">
            ↪
          </span>

          <span>
            Logout
          </span>

        </button>

      </div>

    </aside>
  );
};


export default Sidebar;