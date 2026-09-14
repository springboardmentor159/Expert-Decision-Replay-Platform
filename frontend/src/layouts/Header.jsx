import { useNavigate } from "react-router-dom";
import {
  getStoredUser,
  logoutUser,
} from "../auth/authService";

function Header() {
  const navigate = useNavigate();
  const user = getStoredUser();

  const handleLogout = () => {
    logoutUser();
    navigate("/login", { replace: true });
  };

  return (
    <header className="header">
      <div className="header-title">
        <h2>Dashboard</h2>
      </div>

      <div className="header-user">
        <div className="user-info">
          <strong>{user?.email || "User"}</strong>
          <span>{user?.role || "Employee"}</span>
        </div>

        <button onClick={handleLogout} className="logout-button">
          Logout
        </button>
      </div>
    </header>
  );
}

export default Header;