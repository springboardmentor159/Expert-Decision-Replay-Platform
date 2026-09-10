import { Navigate, Route, Routes } from "react-router-dom";

import { useAuth } from "./auth/AuthContext";
import ProtectedRoute from "./components/ProtectedRoute";
import AppLayout from "./layouts/AppLayout";

import DashboardPage from "./pages/DashboardPage";
import DecisionListPage from "./pages/DecisionListPage";
import DecisionDetailsPage from "./pages/DecisionDetailsPage";
import DecisionHistoryPage from "./pages/DecisionHistoryPage";
import CreateDecisionPage from "./pages/CreateDecisionPage";
import EditDecisionPage from "./pages/EditDecisionPage";
import AlternativesPage from "./pages/AlternativesPage";
import CommentsPage from "./pages/CommentsPage";
import ApprovalWorkflowPage from "./pages/ApprovalWorkflowPage";
import RepositoryPage from "./pages/RepositoryPage";
import ActivityPage from "./pages/ActivityPage";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import ReportsPage from "./pages/ReportsPage";

function App() {
  const { isAuthenticated } = useAuth();

  return (
    <Routes>
      {/* =====================================================
          PUBLIC ROUTES
         ===================================================== */}

      <Route
        path="/"
        element={
          <Navigate
            to={
              isAuthenticated
                ? "/dashboard"
                : "/login"
            }
            replace
          />
        }
      />

      <Route
        path="/login"
        element={<LoginPage />}
      />

      <Route
        path="/register"
        element={<RegisterPage />}
      />

      {/* =====================================================
          PROTECTED APPLICATION
         ===================================================== */}

      <Route element={<ProtectedRoute />}>
        {/* Dashboard */}
        <Route
          path="/dashboard"
          element={
            <AppLayout>
              <DashboardPage />
            </AppLayout>
          }
        />

        {/* =================================================
            DECISION MANAGEMENT
           ================================================= */}

        <Route
          path="/decisions"
          element={
            <AppLayout>
              <DecisionListPage />
            </AppLayout>
          }
        />

        <Route
          path="/decisions/new"
          element={
            <AppLayout>
              <CreateDecisionPage />
            </AppLayout>
          }
        />

        <Route
          path="/decisions/:decisionId"
          element={
            <AppLayout>
              <DecisionDetailsPage />
            </AppLayout>
          }
        />

        <Route
          path="/decisions/:decisionId/edit"
          element={
            <AppLayout>
              <EditDecisionPage />
            </AppLayout>
          }
        />

        <Route
          path="/decisions/:decisionId/history"
          element={
            <AppLayout>
              <DecisionHistoryPage />
            </AppLayout>
          }
        />

        <Route
          path="/decisions/:decisionId/alternatives"
          element={
            <AppLayout>
              <AlternativesPage />
            </AppLayout>
          }
        />

        <Route
          path="/decisions/:decisionId/comments"
          element={
            <AppLayout>
              <CommentsPage />
            </AppLayout>
          }
        />

        <Route
          path="/decisions/:decisionId/approvals"
          element={
            <AppLayout>
              <ApprovalWorkflowPage />
            </AppLayout>
          }
        />

        {/* =================================================
            KNOWLEDGE REPOSITORY
           ================================================= */}

        <Route
          path="/repository"
          element={
            <AppLayout>
              <RepositoryPage />
            </AppLayout>
          }
        />

        {/* =================================================
            ACTIVITY / AUDIT
           ================================================= */}

        <Route
          path="/activity"
          element={
            <AppLayout>
              <ActivityPage />
            </AppLayout>
          }
        />

        {/* =================================================
            REPORTS
           ================================================= */}

        <Route
          path="/reports"
          element={
            <AppLayout>
              <ReportsPage />
            </AppLayout>
          }
        />
      </Route>

      {/* =====================================================
          FALLBACK
         ===================================================== */}

      <Route
        path="*"
        element={
          <Navigate
            to={
              isAuthenticated
                ? "/dashboard"
                : "/login"
            }
            replace
          />
        }
      />
    </Routes>
  );
}

export default App;