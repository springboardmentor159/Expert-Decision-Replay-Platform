import { useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const Header = () => {
  const location = useLocation();
  const { logout } = useAuth();

  const pageNames = {
    "/dashboard": "Dashboard",
    "/decisions": "Decisions",
    "/create-decision": "Create Decision",
    "/alternatives": "Alternatives",
    "/knowledge-repository": "Knowledge Repository",
    "/audit-logs": "Audit Logs",
    "/notifications": "Notifications",
    "/reports": "Reports",
    "/teams": "Teams",
  };

  const currentPage = pageNames[location.pathname] || "Dashboard";

  const handleLogout = () => {
    logout();
  };

  return (
    <header className="top-header">
      <div>
        <p className="breadcrumb">Workspace / {currentPage}</p>
        <h1>{currentPage}</h1>
      </div>

      <div className="header-actions">
        <div className="user-info">
          <div className="user-avatar">M</div>

          <div>
            <strong>Meenakshi</strong>
            <span>Decision Manager</span>
          </div>
        </div>

        <button className="logout-button" onClick={handleLogout}>
          Logout
        </button>
      </div>
    </header>
  );
};

export default Header;