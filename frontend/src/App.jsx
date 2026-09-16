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
import EditAlternative from "./pages/EditAlternative";
import AlternativeComparison from "./pages/AlternativeComparison";

import Discussions from "./pages/Discussions";

import AssignedReviews from "./pages/AssignedReviews";
import ReviewApproval from "./pages/ReviewApproval";

import KnowledgeRepository from "./pages/KnowledgeRepository";

import Reports from "./pages/Reports";
import AuditLogs from "./pages/AuditLogs";

import Analytics from "./pages/Analytics";

import UserManagement from "./pages/UserManagement";

import {
  Activity,
  CheckCircle2,
  Database,
  FileText,
  KeyRound,
  Layers3,
  LockKeyhole,
  Server,
  ShieldCheck,
  Users,
  Workflow,
} from "lucide-react";


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


function SystemInformation() {
  const { user } = useContext(AuthContext);

  return (
    <div className="page-container system-page">

      <div className="page-header">
        <div>
          <h1>System Information</h1>
          <p>
            View platform, architecture, security, and
            application information.
          </p>
        </div>
      </div>


      {/* Platform Overview */}
      <div className="system-card">
        <div className="system-card-header">
          <div className="system-title-icon">
            <Server size={22} />
          </div>

          <div>
            <h2>Platform Overview</h2>
            <p>
              Technical information about the Expert
              Decision Replay Platform.
            </p>
          </div>
        </div>

        <div className="system-info-grid">

          <div className="system-info-item">
            <span>Platform Name</span>
            <strong>
              Expert Decision Replay
            </strong>
          </div>

          <div className="system-info-item">
            <span>Application Type</span>
            <strong>
              Decision Management Platform
            </strong>
          </div>

          <div className="system-info-item">
            <span>Frontend</span>
            <strong>
              React + Vite
            </strong>
          </div>

          <div className="system-info-item">
            <span>Backend</span>
            <strong>
              FastAPI
            </strong>
          </div>

          <div className="system-info-item">
            <span>Database</span>
            <strong>
              PostgreSQL
            </strong>
          </div>

          <div className="system-info-item">
            <span>ORM</span>
            <strong>
              SQLAlchemy
            </strong>
          </div>

        </div>
      </div>


      {/* Architecture */}
      <div className="system-card">

        <div className="system-card-header">
          <div className="system-title-icon">
            <Layers3 size={22} />
          </div>

          <div>
            <h2>System Architecture</h2>
            <p>
              Main technologies used by the application.
            </p>
          </div>
        </div>


        <div className="architecture-flow">

          <div className="architecture-box">
            <FileText size={24} />
            <strong>React Frontend</strong>
            <span>User Interface</span>
          </div>

          <div className="architecture-arrow">
            →
          </div>

          <div className="architecture-box">
            <Workflow size={24} />
            <strong>API Layer</strong>
            <span>Axios / REST APIs</span>
          </div>

          <div className="architecture-arrow">
            →
          </div>

          <div className="architecture-box">
            <Server size={24} />
            <strong>FastAPI Backend</strong>
            <span>Business Logic</span>
          </div>

          <div className="architecture-arrow">
            →
          </div>

          <div className="architecture-box">
            <Database size={24} />
            <strong>PostgreSQL</strong>
            <span>Data Storage</span>
          </div>

        </div>

      </div>


      {/* Security */}
      <div className="system-card">

        <div className="system-card-header">
          <div className="system-title-icon">
            <ShieldCheck size={22} />
          </div>

          <div>
            <h2>Security & Access Control</h2>
            <p>
              Authentication and authorization features
              available in the platform.
            </p>
          </div>
        </div>


        <div className="system-feature-grid">

          <div className="system-feature">
            <div className="feature-icon">
              <KeyRound size={20} />
            </div>

            <div>
              <strong>JWT Authentication</strong>
              <p>
                Secure token-based authentication is used
                for API access.
              </p>
            </div>

            <CheckCircle2
              size={20}
              className="feature-check"
            />
          </div>


          <div className="system-feature">
            <div className="feature-icon">
              <Users size={20} />
            </div>

            <div>
              <strong>Role-Based Access</strong>
              <p>
                Employee, Reviewer, Manager and
                Administrator roles are supported.
              </p>
            </div>

            <CheckCircle2
              size={20}
              className="feature-check"
            />
          </div>


          <div className="system-feature">
            <div className="feature-icon">
              <LockKeyhole size={20} />
            </div>

            <div>
              <strong>Protected Routes</strong>
              <p>
                Application pages require authenticated
                access.
              </p>
            </div>

            <CheckCircle2
              size={20}
              className="feature-check"
            />
          </div>


          <div className="system-feature">
            <div className="feature-icon">
              <Activity size={20} />
            </div>

            <div>
              <strong>Audit Logging</strong>
              <p>
                User and system activities are recorded
                for traceability.
              </p>
            </div>

            <CheckCircle2
              size={20}
              className="feature-check"
            />
          </div>

        </div>

      </div>


      {/* Application Modules */}
      <div className="system-card">

        <div className="system-card-header">
          <div className="system-title-icon">
            <Workflow size={22} />
          </div>

          <div>
            <h2>Application Modules</h2>
            <p>
              Major functional modules available in the
              platform.
            </p>
          </div>
        </div>


        <div className="module-grid">

          <div className="module-item">
            <CheckCircle2 size={18} />
            <span>Decision Management</span>
          </div>

          <div className="module-item">
            <CheckCircle2 size={18} />
            <span>Alternative Analysis</span>
          </div>

          <div className="module-item">
            <CheckCircle2 size={18} />
            <span>Discussion & Comments</span>
          </div>

          <div className="module-item">
            <CheckCircle2 size={18} />
            <span>Approval Workflow</span>
          </div>

          <div className="module-item">
            <CheckCircle2 size={18} />
            <span>Knowledge Repository</span>
          </div>

          <div className="module-item">
            <CheckCircle2 size={18} />
            <span>Version History</span>
          </div>

          <div className="module-item">
            <CheckCircle2 size={18} />
            <span>Audit Logs</span>
          </div>

          <div className="module-item">
            <CheckCircle2 size={18} />
            <span>Reports & Export</span>
          </div>

        </div>

      </div>


      {/* Current User */}
      <div className="system-card">

        <div className="system-card-header">
          <div className="system-title-icon">
            <Users size={22} />
          </div>

          <div>
            <h2>Current Session</h2>
            <p>
              Information about the currently authenticated
              user.
            </p>
          </div>
        </div>


        <div className="system-session">

          <div className="session-avatar">
            {user?.full_name?.charAt(0)?.toUpperCase() ||
              user?.name?.charAt(0)?.toUpperCase() ||
              "A"}
          </div>

          <div className="session-details">

            <strong>
              {user?.full_name ||
                user?.name ||
                "Administrator"}
            </strong>

            <span>
              {user?.email ||
                "pragna@example.com"}
            </span>

            <span className="session-role">
              Role:{" "}
              {user?.role ||
                "Administrator"}
            </span>

          </div>

          <div className="session-status">
            <CheckCircle2 size={18} />
            Authenticated
          </div>

        </div>

      </div>


      {/* Footer */}
      <div className="system-footer">

        <div>
          <strong>
            Expert Decision Replay Platform
          </strong>

          <span>
            Secure decision management and replay system
          </span>
        </div>

        <div className="system-status">
          <span className="status-dot"></span>
          Application Online
        </div>

      </div>


      <style>{`

        .system-page {
          padding-bottom: 40px;
        }

        .system-card {
          background: #ffffff;
          border: 1px solid #e5e7eb;
          border-radius: 16px;
          padding: 24px;
          margin-bottom: 20px;
          box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
        }

        .system-card-header {
          display: flex;
          align-items: flex-start;
          gap: 14px;
          margin-bottom: 22px;
        }

        .system-card-header h2 {
          margin: 0 0 5px;
          font-size: 20px;
          color: #0f172a;
        }

        .system-card-header p {
          margin: 0;
          color: #64748b;
          font-size: 14px;
        }

        .system-title-icon {
          width: 44px;
          height: 44px;
          border-radius: 12px;
          background: #eff6ff;
          color: #2563eb;
          display: flex;
          align-items: center;
          justify-content: center;
          flex-shrink: 0;
        }

        .system-info-grid {
          display: grid;
          grid-template-columns:
            repeat(3, minmax(0, 1fr));
          gap: 14px;
        }

        .system-info-item {
          padding: 16px;
          background: #f8fafc;
          border: 1px solid #e2e8f0;
          border-radius: 12px;
        }

        .system-info-item span {
          display: block;
          color: #64748b;
          font-size: 13px;
          margin-bottom: 7px;
        }

        .system-info-item strong {
          display: block;
          color: #0f172a;
          font-size: 15px;
        }

        .architecture-flow {
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 12px;
          flex-wrap: wrap;
        }

        .architecture-box {
          min-width: 150px;
          padding: 18px;
          border: 1px solid #dbe3ef;
          border-radius: 14px;
          background: #f8fafc;
          display: flex;
          flex-direction: column;
          align-items: center;
          text-align: center;
          gap: 7px;
          color: #2563eb;
        }

        .architecture-box strong {
          color: #0f172a;
          font-size: 14px;
        }

        .architecture-box span {
          color: #64748b;
          font-size: 12px;
        }

        .architecture-arrow {
          font-size: 25px;
          color: #94a3b8;
        }

        .system-feature-grid {
          display: grid;
          grid-template-columns:
            repeat(2, minmax(0, 1fr));
          gap: 14px;
        }

        .system-feature {
          display: flex;
          align-items: center;
          gap: 13px;
          padding: 17px;
          border: 1px solid #e2e8f0;
          border-radius: 13px;
          background: #ffffff;
        }

        .feature-icon {
          width: 40px;
          height: 40px;
          border-radius: 10px;
          background: #eff6ff;
          color: #2563eb;
          display: flex;
          align-items: center;
          justify-content: center;
          flex-shrink: 0;
        }

        .system-feature > div:nth-child(2) {
          flex: 1;
        }

        .system-feature strong {
          display: block;
          color: #0f172a;
          font-size: 14px;
          margin-bottom: 4px;
        }

        .system-feature p {
          margin: 0;
          color: #64748b;
          font-size: 12px;
          line-height: 1.5;
        }

        .feature-check {
          color: #16a34a;
          flex-shrink: 0;
        }

        .module-grid {
          display: grid;
          grid-template-columns:
            repeat(4, minmax(0, 1fr));
          gap: 12px;
        }

        .module-item {
          display: flex;
          align-items: center;
          gap: 9px;
          padding: 14px;
          border-radius: 10px;
          background: #f8fafc;
          border: 1px solid #e2e8f0;
          color: #334155;
          font-size: 13px;
        }

        .module-item svg {
          color: #16a34a;
          flex-shrink: 0;
        }

        .system-session {
          display: flex;
          align-items: center;
          gap: 15px;
          padding: 17px;
          background: #f8fafc;
          border: 1px solid #e2e8f0;
          border-radius: 13px;
        }

        .session-avatar {
          width: 48px;
          height: 48px;
          border-radius: 50%;
          background: #dbeafe;
          color: #2563eb;
          display: flex;
          align-items: center;
          justify-content: center;
          font-weight: 700;
          font-size: 18px;
        }

        .session-details {
          display: flex;
          flex-direction: column;
          gap: 3px;
          flex: 1;
        }

        .session-details strong {
          color: #0f172a;
          font-size: 15px;
        }

        .session-details span {
          color: #64748b;
          font-size: 13px;
        }

        .session-details .session-role {
          color: #2563eb;
          font-weight: 600;
        }

        .session-status {
          display: flex;
          align-items: center;
          gap: 7px;
          color: #15803d;
          background: #f0fdf4;
          border: 1px solid #bbf7d0;
          padding: 8px 12px;
          border-radius: 20px;
          font-size: 12px;
          font-weight: 600;
        }

        .system-footer {
          display: flex;
          justify-content: space-between;
          align-items: center;
          gap: 20px;
          padding: 20px 4px;
          color: #64748b;
        }

        .system-footer > div:first-child {
          display: flex;
          flex-direction: column;
          gap: 4px;
        }

        .system-footer strong {
          color: #334155;
          font-size: 14px;
        }

        .system-footer span {
          font-size: 12px;
        }

        .system-status {
          display: flex;
          align-items: center;
          gap: 8px;
          color: #15803d !important;
          font-weight: 600;
        }

        .status-dot {
          width: 8px;
          height: 8px;
          border-radius: 50%;
          background: #22c55e;
          display: inline-block;
        }

        @media (max-width: 1000px) {

          .system-info-grid {
            grid-template-columns:
              repeat(2, minmax(0, 1fr));
          }

          .module-grid {
            grid-template-columns:
              repeat(2, minmax(0, 1fr));
          }

        }

        @media (max-width: 700px) {

          .system-info-grid,
          .system-feature-grid {
            grid-template-columns: 1fr;
          }

          .architecture-flow {
            flex-direction: column;
          }

          .architecture-arrow {
            transform: rotate(90deg);
          }

          .system-session {
            align-items: flex-start;
            flex-wrap: wrap;
          }

          .session-status {
            width: 100%;
            justify-content: center;
          }

          .system-footer {
            flex-direction: column;
            align-items: flex-start;
          }

        }

        @media (max-width: 480px) {

          .system-card {
            padding: 17px;
          }

          .module-grid {
            grid-template-columns: 1fr;
          }

          .architecture-box {
            width: 100%;
          }

        }

      `}</style>

    </div>
  );
}


function AppRoutes() {
  return (
    <Routes>

      {/* Public Routes */}

      <Route
        path="/login"
        element={<Login />}
      />

      <Route
        path="/register"
        element={<Register />}
      />


      {/* Protected Application */}

      <Route
        element={
          <ProtectedRoute>
            <DashboardLayout />
          </ProtectedRoute>
        }
      >

        <Route
          path="/dashboard"
          element={<Dashboard />}
        />


        {/* Decisions */}

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


        {/* Alternatives */}

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
          path="/alternatives/:alternativeId/edit"
          element={<EditAlternative />}
        />

        <Route
          path="/decisions/:decisionId/alternatives/compare"
          element={<AlternativeComparison />}
        />


        {/* Discussions */}

        <Route
          path="/discussions"
          element={<Discussions />}
        />

        <Route
          path="/decisions/:decisionId/discussions"
          element={<Discussions />}
        />


        {/* Approvals */}

        <Route
          path="/approvals"
          element={<AssignedReviews />}
        />

        <Route
          path="/approvals/:approvalId"
          element={<ReviewApproval />}
        />


        {/* Knowledge Repository */}

        <Route
          path="/knowledge-repository"
          element={<KnowledgeRepository />}
        />


        {/* Reports */}

        <Route
          path="/reports"
          element={<Reports />}
        />


        {/* Audit */}

        <Route
          path="/audit"
          element={<AuditLogs />}
        />


        {/* Analytics */}

        <Route
          path="/analytics"
          element={<Analytics />}
        />


        {/* User Management */}

        <Route
          path="/users"
          element={<UserManagement />}
        />


        {/* System Information */}

        <Route
          path="/system"
          element={<SystemInformation />}
        />

      </Route>


      {/* Default */}

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