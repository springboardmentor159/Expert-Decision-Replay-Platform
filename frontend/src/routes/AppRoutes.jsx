import { Navigate, Route, Routes } from "react-router-dom";

import Login from "../pages/Login";
import Register from "../pages/Register";
import Dashboard from "../pages/Dashboard";
import Decisions from "../pages/Decisions";
import CreateDecision from "../pages/CreateDecision";
import DecisionDetails from "../pages/DecisionDetails";
import EditDecision from "../pages/EditDecision";
import Alternatives from "../pages/Alternatives";
import AlternativeComparison from "../pages/AlternativeComparison";
import Comments from "../pages/Comments";
import Approvals from "../pages/Approvals";
import KnowledgeRepository from "../pages/KnowledgeRepository";
import VersionHistory from "../pages/VersionHistory";
import AuditLogs from "../pages/AuditLogs";
import Reports from "../pages/Reports";

import { useAuth } from "../context/AuthContext";
import Layout from "../components/Layout";


function ProtectedRoute({ children }) {
  const { isAuthenticated } = useAuth();

  return isAuthenticated
    ? children
    : <Navigate to="/login" replace />;
}


function AppRoutes() {
  return (
    <Routes>

      {/* ================= LOGIN / REGISTER ================= */}

      <Route
        path="/login"
        element={<Login />}
      />

      <Route
        path="/register"
        element={<Register />}
      />


      {/* ================= PROTECTED APPLICATION ================= */}

      <Route
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >

        {/* Dashboard */}
        <Route
          path="/dashboard"
          element={<Dashboard />}
        />

        {/* Decisions */}
        <Route
          path="/decisions"
          element={<Decisions />}
        />

        {/* Create Decision */}
        <Route
          path="/decisions/create"
          element={<CreateDecision />}
        />

        {/* Edit Decision */}
        <Route
          path="/decisions/:id/edit"
          element={<EditDecision />}
        />

        {/* Decision Details */}
        <Route
          path="/decisions/:id"
          element={<DecisionDetails />}
        />

        {/* Alternatives */}
        <Route
          path="/decisions/:id/alternatives"
          element={<Alternatives />}
        />

        {/* Compare Alternatives */}
        <Route
          path="/decisions/:id/alternatives/compare"
          element={<AlternativeComparison />}
        />

        {/* Discussions & Comments */}
        <Route
          path="/decisions/:id/comments"
          element={<Comments />}
        />

        {/* Approval Workflow */}
        <Route
          path="/decisions/:id/approvals"
          element={<Approvals />}
        />

        {/* Knowledge Repository */}
        <Route
          path="/knowledge"
          element={<KnowledgeRepository />}
        />

        {/* Version History */}
        <Route
          path="/decisions/:id/history"
          element={<VersionHistory />}
        />

        {/* Audit Logs */}
        <Route
          path="/audit-logs"
          element={<AuditLogs />}
        />

        {/* Reports */}
        <Route
          path="/reports"
          element={<Reports />}
        />

      </Route>


      {/* ================= DEFAULT ================= */}

      <Route
        path="/"
        element={<Navigate to="/login" replace />}
      />

      {/* ================= INVALID URL ================= */}

      <Route
        path="*"
        element={<Navigate to="/login" replace />}
      />

    </Routes>
  );
}

export default AppRoutes;