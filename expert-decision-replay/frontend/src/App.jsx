import { Navigate, Route, Routes } from "react-router-dom";

import ProtectedRoute from "./components/ProtectedRoute";
import RoleGuard from "./components/RoleGuard";
import Layout from "./layouts/Layout";

// Pages
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Decisions from "./pages/Decisions";
import CreateDecision from "./pages/CreateDecision";
import DecisionDetails from "./pages/DecisionDetails";
import AlternativeComparision from "./pages/AlternativeComparision";
import KnowledgeRepository from "./pages/KnowledgeRepository";
import AuditLogs from "./pages/AuditLogs";
import Teams from "./pages/Teams";
import Notifications from "./pages/Notifications";
import Reports from "./pages/Reports";

function App() {
  return (
    <Routes>

      {/* Login */}
      <Route path="/login" element={<Login />} />

      {/* Protected Pages */}
      <Route element={<ProtectedRoute />}>
        <Route element={<Layout />}>

          <Route
            path="/dashboard"
            element={<Dashboard />}
          />

          <Route
            path="/decisions"
            element={<Decisions />}
          />

          <Route
            path="/create-decision"
            element={<CreateDecision />}
          />

          <Route
            path="/decisions/:decisionId"
            element={<DecisionDetails />}
          />

          <Route
            path="/alternatives"
            element={<AlternativeComparision />}
          />

          <Route
            path="/knowledge-repository"
            element={<KnowledgeRepository />}
          />

          <Route
            path="/audit-logs"
            element={<AuditLogs />}
          />

          <Route
            path="/notifications"
            element={<Notifications />}
          />

          <Route
            path="/reports"
            element={<Reports />}
          />

          {/* Manager/Admin only */}
          <Route
            element={
              <RoleGuard
                allowedRoles={[
                  "manager",
                  "admin",
                ]}
              />
            }
          >
            <Route
              path="/teams"
              element={<Teams />}
            />
          </Route>

        </Route>
      </Route>

      {/* Default page */}
      <Route
        path="/"
        element={
          <Navigate
            to="/login"
            replace
          />
        }
      />

      {/* Unknown URL */}
      <Route
        path="*"
        element={
          <Navigate
            to="/login"
            replace
          />
        }
      />

    </Routes>
  );
}

export default App;