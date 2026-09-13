import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Navbar() {
  const { user, logoutUser } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logoutUser();
    navigate('/login');
  };

  const navItems = {
    Employee: [
      { label: 'Dashboard', path: '/dashboard' },
      { label: 'My Decisions', path: '/decisions' },
      { label: 'Create Decision', path: '/decisions/create' },
      { label: 'Repository', path: '/repository' },
      { label: 'Reports', path: '/reports' },
    ],
    Reviewer: [
      { label: 'Dashboard', path: '/dashboard' },
      { label: 'Decisions', path: '/decisions' },
      { label: 'Repository', path: '/repository' },
      { label: 'Reports', path: '/reports' },
    ],
    Manager: [
      { label: 'Dashboard', path: '/manager' },
      { label: 'Decisions', path: '/decisions' },
      { label: 'Repository', path: '/repository' },
      { label: 'Reports', path: '/reports' },
    ],
    Administrator: [
      { label: 'Dashboard', path: '/admin' },
      { label: 'Decisions', path: '/decisions' },
      { label: 'Repository', path: '/repository' },
      { label: 'Reports', path: '/reports' },
      { label: 'Audit Logs', path: '/admin/audit' },
    ],
  };

  const links = navItems[user?.role] || navItems['Employee'];

  return (
    <nav style={styles.navbar}>
      <div style={styles.brand} onClick={() => navigate('/dashboard')}>
        🏢 Expert Decision Replay
      </div>
      <div style={styles.links}>
        {links.map(item => (
          <span
            key={item.path}
            style={{
              ...styles.link,
              ...(window.location.pathname === item.path ? styles.activeLink : {})
            }}
            onClick={() => navigate(item.path)}
          >
            {item.label}
          </span>
        ))}
      </div>
      <div style={styles.userSection}>
        <span style={styles.userName}>{user?.full_name}</span>
        <span style={styles.userRole}>{user?.role}</span>
        <button style={styles.logoutBtn} onClick={handleLogout}>
          Logout
        </button>
      </div>
    </nav>
  );
}

const styles = {
  navbar: {
    backgroundColor: '#2C3E50',
    padding: '0 32px',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    height: '60px',
    position: 'sticky',
    top: 0,
    zIndex: 1000,
    boxShadow: '0 2px 8px rgba(0,0,0,0.2)',
  },
  brand: {
    color: 'white',
    fontSize: '18px',
    fontWeight: 'bold',
    cursor: 'pointer',
    whiteSpace: 'nowrap',
  },
  links: {
    display: 'flex',
    gap: '4px',
    flex: 1,
    justifyContent: 'center',
  },
  link: {
    color: 'rgba(255,255,255,0.8)',
    cursor: 'pointer',
    fontSize: '14px',
    padding: '8px 14px',
    borderRadius: '6px',
    transition: 'all 0.2s',
  },
  activeLink: {
    backgroundColor: 'rgba(255,255,255,0.15)',
    color: 'white',
  },
  userSection: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    whiteSpace: 'nowrap',
  },
  userName: {
    color: 'white',
    fontSize: '14px',
    fontWeight: '600',
  },
  userRole: {
    color: 'rgba(255,255,255,0.6)',
    fontSize: '12px',
    backgroundColor: 'rgba(255,255,255,0.1)',
    padding: '2px 8px',
    borderRadius: '10px',
  },
  logoutBtn: {
    padding: '6px 14px',
    backgroundColor: '#e74c3c',
    color: 'white',
    border: 'none',
    borderRadius: '6px',
    cursor: 'pointer',
    fontSize: '13px',
  },
};