import { useAuth } from "../context/AuthContext";
import Forbidden from "../pages/Forbidden";

export default function RoleRoute({ allow, children }) {
  const { user } = useAuth();

  if (!user || !allow.includes(user.role)) {
    return <Forbidden />;
  }

  return children;
}
