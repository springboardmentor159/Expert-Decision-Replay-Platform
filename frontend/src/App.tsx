import {
  BrowserRouter,
  Navigate,
  Route,
  Routes,
} from "react-router-dom";

import { AuthProvider } from "./context/AuthProvider";

import ProtectedRoute from "./components/ProtectedRoute";
import RoleRoute from "./components/RoleRoute";

import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";
import DecisionList from "./pages/DecisionList";
import CreateDecision from "./pages/CreateDecision";
import DecisionDetails from "./pages/DecisionDetails";
import EditDecision from "./pages/EditDecision";
import Alternatives from "./pages/Alternatives";
import Discussion from "./pages/Discussion";
import Approval from "./pages/Approval";
import History from "./pages/History";
import AuditActivity from "./pages/AuditActivity";

function Unauthorized() {
  return (
    <main style={{ padding: "40px" }}>
      <h1>Access Denied</h1>

      <p>
        You do not have permission to access this page.
      </p>
    </main>
  );
}

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
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

          <Route
            path="/unauthorized"
            element={<Unauthorized />}
          />

          {/* Protected Routes */}
          <Route element={<ProtectedRoute />}>
            <Route
              path="/dashboard"
              element={<Dashboard />}
            />

            <Route
              path="/audit-activity"
              element={<AuditActivity />}
            />

            <Route
              path="/decisions"
              element={<DecisionList />}
            />

            <Route
              path="/decisions/create"
              element={<CreateDecision />}
            />

            <Route
              path="/decisions/:id"
              element={<DecisionDetails />}
            />

            <Route
              path="/decisions/:id/edit"
              element={<EditDecision />}
            />

            <Route
              path="/decisions/:id/alternatives"
              element={<Alternatives />}
            />

            <Route
              path="/decisions/:id/discussion"
              element={<Discussion />}
            />

            <Route
              path="/decisions/:id/approval"
              element={<Approval />}
            />

            <Route
              path="/decisions/:id/history"
              element={<History />}
            />

            {/* Manager + Administrator Route */}
            <Route
              element={
                <RoleRoute
                  allowedRoles={[
                    "Manager",
                    "Administrator",
                  ]}
                />
              }
            >
              <Route
                path="/management"
                element={
                  <main
                    style={{
                      padding: "40px",
                    }}
                  >
                    <h1>
                      Management
                    </h1>

                    <p>
                      Manager and Administrator
                      area.
                    </p>
                  </main>
                }
              />
            </Route>
          </Route>

          {/* Default Route */}
          <Route
            path="/"
            element={
              <Navigate
                to="/dashboard"
                replace
              />
            }
          />

          {/* Unknown Route */}
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
    </BrowserRouter>
  );
}

export default App;