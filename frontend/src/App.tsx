import { Navigate, Route, Routes } from "react-router-dom";
import { AuthProvider, useAuth } from "./context/AuthContext";

import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";
import Decisions from "./pages/Decisions";
import CreateDecision from "./pages/CreateDecision";
import DecisionDetails from "./pages/DecisionDetails";
import Alternatives from "./pages/Alternatives";
import Discussions from "./pages/Discussions";
import ThreadDetails from "./pages/ThreadDetails";
import Approvals from "./pages/Approvals";
import History from "./pages/History";
import Reports from "./pages/Reports";
import Audit from "./pages/Audit";
import Forbidden from "./pages/Forbidden";

import AppLayout from "./layouts/AppLayout";
import RoleGuard from "./components/RoleGuard";

function ProtectedRoute() {
  const { isAuthenticated } = useAuth();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <AppLayout />;
}

function App() {
  return (
    <AuthProvider>
      <Routes>

        {/* =========================
            PUBLIC ROUTES
        ========================= */}

        <Route
          path="/login"
          element={<Login />}
        />

        <Route
          path="/register"
          element={<Register />}
        />

        <Route
          path="/forbidden"
          element={<Forbidden />}
        />

        {/* =========================
            PROTECTED ROUTES
        ========================= */}

        <Route element={<ProtectedRoute />}>

          {/* =========================
              DASHBOARD
          ========================= */}

          <Route
            path="/dashboard"
            element={<Dashboard />}
          />

          {/* =========================
              DECISIONS
          ========================= */}

          <Route
            path="/decisions"
            element={<Decisions />}
          />

          <Route
            path="/decisions/create"
            element={<CreateDecision />}
          />

          <Route
            path="/decisions/:decisionId"
            element={<DecisionDetails />}
          />

          {/* =========================
              ALTERNATIVES
          ========================= */}

          <Route
            path="/decisions/:decisionId/alternatives"
            element={<Alternatives />}
          />

          {/* =========================
              DISCUSSIONS
          ========================= */}

          <Route
            path="/decisions/:decisionId/discussions"
            element={<Discussions />}
          />

          <Route
            path="/decisions/:decisionId/discussions/:threadId"
            element={<ThreadDetails />}
          />

          {/* =========================
              VERSION HISTORY
          ========================= */}

          <Route
            path="/decisions/:decisionId/history"
            element={<History />}
          />

          {/* =========================
              APPROVALS
          ========================= */}

          <Route
            path="/approvals"
            element={
              <RoleGuard
                allowedRoles={[
                  "Reviewer",
                  "Manager",
                  "Administrator",
                ]}
              >
                <Approvals />
              </RoleGuard>
            }
          />

          {/* =========================
              REPORTS
          ========================= */}

          <Route
            path="/reports"
            element={
              <RoleGuard
                allowedRoles={[
                  "Administrator",
                ]}
              >
                <Reports />
              </RoleGuard>
            }
          />

          {/* =========================
              AUDIT
          ========================= */}

          <Route
            path="/audit"
            element={
              <RoleGuard
                allowedRoles={[
                  "Administrator",
                ]}
              >
                <Audit />
              </RoleGuard>
            }
          />

        </Route>

        {/* =========================
            DEFAULT ROUTE
        ========================= */}

        <Route
          path="/"
          element={
            <Navigate
              to="/dashboard"
              replace
            />
          }
        />

        {/* =========================
            UNKNOWN ROUTES
        ========================= */}

        <Route
          path="*"
          element={
            <Navigate
              to="/dashboard"
              replace
            />
          }
        />

      </Routes>
    </AuthProvider>
  );
}

export default App;