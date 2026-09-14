import { useAuth } from "../context/AuthContext";

const Dashboard = () => {
  const { user, role } = useAuth();

  return (
    <div>
      <h1>{role} Dashboard</h1>

      <h3>Welcome, {user?.full_name}</h3>

      <p>
        Your role: <strong>{role}</strong>
      </p>

      <p>
        The actual role-based dashboard will be implemented next.
      </p>
    </div>
  );
};

export default Dashboard;