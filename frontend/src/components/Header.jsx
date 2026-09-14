import { useAuth } from "../context/AuthContext";

const Header = () => {
  const { user, role } = useAuth();

  return (
    <header className="app-header">
      <div className="header-left">
        <div className="header-logo">
          ED
        </div>

        <div>
          <h1>Expert Decision Replay Platform</h1>
          <p>Decision Management System</p>
        </div>
      </div>

      <div className="header-right">
        <div className="header-user">
          <div className="user-avatar">
            {user?.full_name
              ? user.full_name.charAt(0).toUpperCase()
              : "U"}
          </div>

          <div className="user-info">
            <strong>{user?.full_name || "User"}</strong>
            <span>{role || "User"}</span>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;