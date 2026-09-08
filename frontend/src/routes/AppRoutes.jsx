import { Navigate, Route, Routes } from "react-router-dom";
import Login from "../pages/Login";
import Register from "../pages/Register";
import Dashboard from "../pages/Dashboard";
import Decisions from "../pages/Decisions";
import CreateDecision from "../pages/CreateDecision";
import DecisionDetails from "../pages/DecisionDetails";
import Alternatives from "../pages/Alternatives";
import AlternativeComparison from "../pages/AlternativeComparison";
import Comments from "../pages/Comments";
import Approvals from "../pages/Approvals";
import KnowledgeRepository from "../pages/KnowledgeRepository";
import VersionHistory from "../pages/VersionHistory";
import AuditLogs from "../pages/AuditLogs";
import Reports from "../pages/Reports";
import { useAuth } from "../context/AuthContext";

function ProtectedRoute({ children }) {
  const { isAuthenticated } = useAuth();

  return isAuthenticated ? children : <Navigate to="/login" replace />;
}

function AppRoutes() {
  return (
    <Routes>
      {/* Login */}
      <Route path="/login" element={<Login />} />

      {/* Registration */}
      <Route path="/register" element={<Register />} />

      {/* Dashboard */}
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        }
      />

      {/* Decisions List */}
      <Route
        path="/decisions"
        element={
          <ProtectedRoute>
            <Decisions />
          </ProtectedRoute>
        }
      />

      {/* Create Decision */}
      <Route
        path="/decisions/create"
        element={
          <ProtectedRoute>
            <CreateDecision />
          </ProtectedRoute>
        }
      />

      {/* Decision Details */}
      <Route
        path="/decisions/:id"
        element={
          <ProtectedRoute>
            <DecisionDetails />
          </ProtectedRoute>
        }
      />

      {/* Alternative Analysis */}
      <Route
        path="/decisions/:id/alternatives"
        element={
          <ProtectedRoute>
            <Alternatives />
          </ProtectedRoute>
        }
      />

      {/* Compare Alternatives */}
      <Route
        path="/decisions/:id/alternatives/compare"
        element={
          <ProtectedRoute>
            <AlternativeComparison />
          </ProtectedRoute>
        }
      />

      {/* Discussion & Comments */}
      <Route
        path="/decisions/:id/comments"
        element={
          <ProtectedRoute>
            <Comments />
          </ProtectedRoute>
        }
      />

      {/* Approval Workflow */}
      <Route
        path="/decisions/:id/approvals"
        element={
          <ProtectedRoute>
            <Approvals />
          </ProtectedRoute>
        }
      />

      {/* Knowledge Repository */}
      <Route
        path="/knowledge"
        element={
          <ProtectedRoute>
            <KnowledgeRepository />
          </ProtectedRoute>
        }
      />

      {/* Version History & Timeline */}
      <Route
        path="/decisions/:id/history"
        element={
          <ProtectedRoute>
            <VersionHistory />
          </ProtectedRoute>
        }
      />

      {/* Audit & Activity Logs */}
      <Route
        path="/audit-logs"
        element={
          <ProtectedRoute>
            <AuditLogs />
          </ProtectedRoute>
        }
      />

      {/* Reports */}
      <Route
        path="/reports"
        element={
          <ProtectedRoute>
            <Reports />
          </ProtectedRoute>
        }
      />

      {/* Default Route */}
      <Route
        path="/"
        element={<Navigate to="/login" replace />}
      />

      {/* Invalid Route */}
      <Route
        path="*"
        element={<Navigate to="/login" replace />}
      />
    </Routes>
  );
}

export default AppRoutes;