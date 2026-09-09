import {
  BrowserRouter,
  Navigate,
  Route,
  Routes,
  useLocation,
} from "react-router-dom";

import { useContext } from "react";

import {
  AuthContext,
  AuthProvider,
} from "./context/AuthContext";

import DashboardLayout from "./components/DashboardLayout";

import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";

import Decisions from "./pages/Decisions";
import CreateDecision from "./pages/CreateDecision";
import EditDecision from "./pages/EditDecision";
import DecisionDetails from "./pages/DecisionDetails";
import DecisionHistory from "./pages/DecisionHistory";

import Alternatives from "./pages/Alternatives";
import CreateAlternative from "./pages/CreateAlternative";
import AlternativeComparison from "./pages/AlternativeComparison";

import Discussions from "./pages/Discussions";

import AssignedReviews from "./pages/AssignedReviews";
import ReviewApproval from "./pages/ReviewApproval";

import KnowledgeRepository from "./pages/KnowledgeRepository";

import Reports from "./pages/Reports";
import AuditLogs from "./pages/AuditLogs";

import Analytics from "./pages/Analytics";

import UserManagement from "./pages/UserManagement";


function ProtectedRoute({ children }) {
  const { user, loading } =
    useContext(AuthContext);

  const location = useLocation();

  if (loading) {
    return (
      <div className="loading-state">
        Loading application...
      </div>
    );
  }

  if (!user) {
    return (
      <Navigate
        to="/login"
        replace
        state={{
          from: location,
        }}
      />
    );
  }

  return children;
}


function PlaceholderPage({
  title,
  description,
}) {
  return (
    <div className="page-container">

      <div className="page-header">

        <div>
          <h1>{title}</h1>

          <p>
            {description}
          </p>
        </div>

      </div>


      <div className="card">

        <div className="empty-state">

          <h2>{title}</h2>

          <p>
            This section is available in the
            application structure and can be
            expanded with additional functionality.
          </p>

        </div>

      </div>

    </div>
  );
}


function AppRoutes() {
  return (
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


      {/* =========================
          PROTECTED APPLICATION
      ========================= */}

      <Route
        element={
          <ProtectedRoute>
            <DashboardLayout />
          </ProtectedRoute>
        }
      >

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

        <Route
          path="/decisions/:decisionId/edit"
          element={<EditDecision />}
        />

        <Route
          path="/decisions/:decisionId/history"
          element={<DecisionHistory />}
        />


        {/* =========================
            ALTERNATIVES
        ========================= */}

        <Route
          path="/alternatives"
          element={<Alternatives />}
        />

        <Route
          path="/decisions/:decisionId/alternatives"
          element={<Alternatives />}
        />

        <Route
          path="/decisions/:decisionId/alternatives/create"
          element={<CreateAlternative />}
        />

        <Route
          path="/decisions/:decisionId/alternatives/compare"
          element={<AlternativeComparison />}
        />


        {/* =========================
            DISCUSSIONS
        ========================= */}

        <Route
          path="/discussions"
          element={<Discussions />}
        />

        <Route
          path="/decisions/:decisionId/discussions"
          element={<Discussions />}
        />


        {/* =========================
            APPROVALS
        ========================= */}

        <Route
          path="/approvals"
          element={<AssignedReviews />}
        />

        <Route
          path="/approvals/:approvalId"
          element={<ReviewApproval />}
        />


        {/* =========================
            KNOWLEDGE REPOSITORY
        ========================= */}

        <Route
          path="/knowledge-repository"
          element={<KnowledgeRepository />}
        />


        {/* =========================
            REPORTS
        ========================= */}

        <Route
          path="/reports"
          element={<Reports />}
        />


        {/* =========================
            AUDIT
        ========================= */}

        <Route
          path="/audit"
          element={<AuditLogs />}
        />


        {/* =========================
            ANALYTICS
        ========================= */}

        <Route
          path="/analytics"
          element={<Analytics />}
        />


        {/* =========================
            ADMIN - USER MANAGEMENT
        ========================= */}

        <Route
          path="/users"
          element={<UserManagement />}
        />


        {/* =========================
            ADMIN - SYSTEM
        ========================= */}

        <Route
          path="/system"
          element={
            <PlaceholderPage
              title="System Information"
              description="View platform and system information."
            />
          }
        />

      </Route>


      {/* =========================
          DEFAULT ROUTES
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
  );
}


function App() {
  return (
    <BrowserRouter>

      <AuthProvider>

        <AppRoutes />

      </AuthProvider>

    </BrowserRouter>
  );
}


export default App;