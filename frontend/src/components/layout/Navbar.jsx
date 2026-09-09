import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/login", { replace: true });
  }

  return (
    <header className="navbar">
      <Link to="/dashboard" className="navbar-brand">
        Expert Decision Replay
      </Link>
      {user && (
        <div className="navbar-user">
          <div className="navbar-user-info">
            <span className="navbar-user-name">{user.full_name}</span>
            <span className="navbar-user-role">{user.role}</span>
          </div>
          <button className="btn btn-secondary btn-sm" onClick={handleLogout}>
            Logout
          </button>
        </div>
      )}
    </header>
  );
}
