import { useAuth } from "../../context/AuthContext";
import { ROLES } from "../../utils/roles";
import EmployeeDashboard from "./EmployeeDashboard";
import ReviewerDashboard from "./ReviewerDashboard";
import ManagerDashboard from "./ManagerDashboard";
import AdminDashboard from "./AdminDashboard";
import LoadingState from "../../components/ui/LoadingState";

export default function DashboardRouter() {
  const { user } = useAuth();
  if (!user) return <LoadingState />;

  switch (user.role) {
    case ROLES.ADMINISTRATOR:
      return <AdminDashboard />;
    case ROLES.MANAGER:
      return <ManagerDashboard />;
    case ROLES.REVIEWER:
      return <ReviewerDashboard />;
    case ROLES.EMPLOYEE:
    default:
      return <EmployeeDashboard />;
  }
}
