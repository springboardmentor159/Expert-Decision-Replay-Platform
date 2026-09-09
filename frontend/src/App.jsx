import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import ProtectedRoute from "./components/ProtectedRoute";
import RoleRoute from "./components/RoleRoute";
import AppLayout from "./components/layout/AppLayout";

import Login from "./pages/auth/Login";
import Register from "./pages/auth/Register";
import DashboardRouter from "./pages/dashboard/DashboardRouter";
import DecisionList from "./pages/decisions/DecisionList";
import DecisionCreate from "./pages/decisions/DecisionCreate";
import DecisionDetail from "./pages/decisions/DecisionDetail";
import Approvals from "./pages/approvals/Approvals";
import KnowledgeRepository from "./pages/repository/KnowledgeRepository";
import AuditLogs from "./pages/audit/AuditLogs";
import Reports from "./pages/reports/Reports";
import UserManagement from "./pages/users/UserManagement";
import NotFound from "./pages/NotFound";

import { ROLES } from "./utils/roles";

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />

          <Route
            element={
              <ProtectedRoute>
                <AppLayout />
              </ProtectedRoute>
            }
          >
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/dashboard" element={<DashboardRouter />} />

            <Route path="/decisions" element={<DecisionList />} />
            <Route path="/decisions/new" element={<DecisionCreate />} />
            <Route path="/decisions/:id" element={<DecisionDetail />} />

            <Route
              path="/approvals"
              element={
                <RoleRoute allow={[ROLES.REVIEWER, ROLES.MANAGER, ROLES.ADMINISTRATOR]}>
                  <Approvals />
                </RoleRoute>
              }
            />

            <Route path="/repository" element={<KnowledgeRepository />} />

            <Route
              path="/reports"
              element={
                <RoleRoute allow={[ROLES.MANAGER, ROLES.ADMINISTRATOR]}>
                  <Reports />
                </RoleRoute>
              }
            />

            <Route
              path="/audit"
              element={
                <RoleRoute allow={[ROLES.ADMINISTRATOR]}>
                  <AuditLogs />
                </RoleRoute>
              }
            />

            <Route
              path="/users"
              element={
                <RoleRoute allow={[ROLES.ADMINISTRATOR]}>
                  <UserManagement />
                </RoleRoute>
              }
            />

            <Route path="*" element={<NotFound />} />
          </Route>
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}
