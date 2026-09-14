import { Routes, Route, Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

import ProtectedRoute from "./ProtectedRoute";
import MainLayout from "../layouts/MainLayout";

// Authentication
import Login from "../pages/Login";
import Register from "../pages/Register";
import Profile from "../pages/Profile";

// Role Dashboards
import EmployeeDashboard from "../pages/dashboards/EmployeeDashboard";
import ReviewerDashboard from "../pages/dashboards/ReviewerDashboard";
import ManagerDashboard from "../pages/dashboards/ManagerDashboard";
import AdminDashboard from "../pages/dashboards/AdminDashboard";

// Decisions
import DecisionList from "../pages/decisions/DecisionList";
import MyDecisions from "../pages/decisions/MyDecisions";
import CreateDecision from "../pages/decisions/CreateDecision";
import DecisionDetails from "../pages/decisions/DecisionDetails";
import EditDecision from "../pages/decisions/EditDecision";

// Alternatives
import AlternativeList from "../pages/alternatives/AlternativeList";
import AlternativeForm from "../pages/alternatives/AlternativeForm";
import AlternativeComparison from "../pages/alternatives/AlternativeComparison";

// Discussions
import Discussion from "../pages/discussions/Discussion";
import Threads from "../pages/discussions/Threads";
import MeetingNotes from "../pages/discussions/MeetingNotes";

// Approvals
import ApprovalList from "../pages/approvals/ApprovalList";
import AssignApproval from "../pages/approvals/AssignApproval";

// Repository
import Repository from "../pages/repository/Repository";

// Teams
import Teams from "../pages/teams/Teams";

// Audit
import Audit from "../pages/audit/Audit";

// Reports
import Reports from "../pages/reports/Reports";


// ============================================================
// ROLE PROTECTION COMPONENT
// ============================================================

const RoleRoute = ({ allowedRoles, children }) => {
  const { role } = useAuth();

  if (!allowedRoles.includes(role)) {
    return (
      <Navigate
        to="/dashboard"
        replace
      />
    );
  }

  return children;
};


// ============================================================
// APP ROUTER
// ============================================================

const AppRouter = () => {
  const { role } = useAuth();

  return (
    <Routes>

      {/* ======================================================
          PUBLIC ROUTES
      ====================================================== */}

      <Route
        path="/login"
        element={<Login />}
      />

      <Route
        path="/register"
        element={<Register />}
      />


      {/* ======================================================
          PROTECTED ROUTES
      ====================================================== */}

      <Route element={<ProtectedRoute />}>

        <Route element={<MainLayout />}>


          {/* ==================================================
              ROLE-BASED DASHBOARD
          ================================================== */}

          <Route
            path="/dashboard"
            element={
              role === "Employee" ? (
                <EmployeeDashboard />
              ) : role === "Reviewer" ? (
                <ReviewerDashboard />
              ) : role === "Manager" ? (
                <ManagerDashboard />
              ) : role === "Administrator" ? (
                <AdminDashboard />
              ) : (
                <Navigate
                  to="/login"
                  replace
                />
              )
            }
          />


          {/* ==================================================
              DIRECT ROLE DASHBOARD ROUTES
          ================================================== */}

          <Route
            path="/employee-dashboard"
            element={
              <RoleRoute
                allowedRoles={["Employee"]}
              >
                <EmployeeDashboard />
              </RoleRoute>
            }
          />

          <Route
            path="/reviewer-dashboard"
            element={
              <RoleRoute
                allowedRoles={["Reviewer"]}
              >
                <ReviewerDashboard />
              </RoleRoute>
            }
          />

          <Route
            path="/manager-dashboard"
            element={
              <RoleRoute
                allowedRoles={["Manager"]}
              >
                <ManagerDashboard />
              </RoleRoute>
            }
          />

          <Route
            path="/admin-dashboard"
            element={
              <RoleRoute
                allowedRoles={["Administrator"]}
              >
                <AdminDashboard />
              </RoleRoute>
            }
          />


          {/* ==================================================
              DECISION MANAGEMENT
          ================================================== */}

          {/* General Decision Management */}
          <Route
            path="/decisions"
            element={<DecisionList />}
          />

          {/* My Decisions */}
          <Route
            path="/my-decisions"
            element={<MyDecisions />}
          />

          {/* Create Decision */}
          <Route
            path="/decisions/create"
            element={<CreateDecision />}
          />

          {/* Decision Details */}
          <Route
            path="/decisions/:decisionId"
            element={<DecisionDetails />}
          />

          {/* Edit Decision */}
          <Route
            path="/decisions/:decisionId/edit"
            element={<EditDecision />}
          />


          {/* ==================================================
              ALTERNATIVES
          ================================================== */}

          <Route
            path="/decisions/:decisionId/alternatives"
            element={<AlternativeList />}
          />

          <Route
            path="/decisions/:decisionId/alternatives/create"
            element={<AlternativeForm />}
          />

          <Route
            path="/decisions/:decisionId/alternatives/compare"
            element={<AlternativeComparison />}
          />

          <Route
            path="/decisions/:decisionId/alternatives/:alternativeId/edit"
            element={<AlternativeForm />}
          />


          {/* ==================================================
              DISCUSSIONS
          ================================================== */}

          <Route
            path="/decisions/:decisionId/discussion"
            element={<Discussion />}
          />

          <Route
            path="/decisions/:decisionId/threads"
            element={<Threads />}
          />

          <Route
            path="/decisions/:decisionId/meeting-notes"
            element={<MeetingNotes />}
          />


          {/* ==================================================
              APPROVALS
          ================================================== */}

          <Route
            path="/approvals"
            element={<ApprovalList />}
          />

          {/* Manager + Administrator only */}
          <Route
            path="/approvals/assign"
            element={
              <RoleRoute
                allowedRoles={[
                  "Manager",
                  "Administrator",
                ]}
              >
                <AssignApproval />
              </RoleRoute>
            }
          />


          {/* ==================================================
              KNOWLEDGE REPOSITORY
          ================================================== */}

          <Route
            path="/repository"
            element={<Repository />}
          />


          {/* ==================================================
              TEAMS
          ================================================== */}

          {/* Manager + Administrator only */}

          <Route
            path="/teams"
            element={
              <RoleRoute
                allowedRoles={[
                  "Manager",
                  "Administrator",
                ]}
              >
                <Teams />
              </RoleRoute>
            }
          />


          {/* ==================================================
              AUDIT
          ================================================== */}

          {/* Administrator only */}

          <Route
            path="/audit"
            element={
              <RoleRoute
                allowedRoles={[
                  "Administrator",
                ]}
              >
                <Audit />
              </RoleRoute>
            }
          />


          {/* ==================================================
              REPORTS
          ================================================== */}

          {/* All authenticated users */}

          <Route
            path="/reports"
            element={<Reports />}
          />


          {/* ==================================================
              PROFILE
          ================================================== */}

          <Route
            path="/profile"
            element={<Profile />}
          />

        </Route>

      </Route>


      {/* ======================================================
          DEFAULT ROUTES
      ====================================================== */}

      <Route
        path="/"
        element={
          <Navigate
            to="/login"
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
};


export default AppRouter;