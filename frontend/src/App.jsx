import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";
import MyDecisions from "./pages/MyDecisions";
import CreateDecision from "./pages/CreateDecision";
import EditDecision from "./pages/EditDecision";
import DecisionDetails from "./pages/DecisionDetails";
import AlternativeAnalysis from "./pages/AlternativeAnalysis";
import Discussions from "./pages/Discussions";
import Reports from "./pages/Reports";
import Profile from "./pages/Profile";
import KnowledgeRepository from "./pages/KnowledgeRepository";

import ProtectedRoute from "./auth/ProtectedRoute";
import MainLayout from "./layouts/MainLayout";

function App() {
  return (
    <BrowserRouter>
      <Routes>

        {/* =========================
            Public Routes
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
            Protected Routes
        ========================= */}

        <Route element={<ProtectedRoute />}>
          <Route element={<MainLayout />}>

            {/* Dashboard */}
            <Route
              path="/dashboard"
              element={<Dashboard />}
            />

            {/* My Decisions */}
            <Route
              path="/decisions"
              element={<MyDecisions />}
            />
            
            <Route
              path="/create-decision"
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
              element={<AlternativeAnalysis />}
            />

            <Route path="/discussions" element={<Discussions />} />

            <Route path="/reports" element={<Reports />} />

            <Route path="/profile" element={<Profile />} />

            <Route path="/knowledge" element={<KnowledgeRepository />} />
          </Route>
        </Route>

        {/* =========================
            Default Route
        ========================= */}

        <Route
          path="/"
          element={<Navigate to="/dashboard" replace />}
        />

        {/* =========================
            Unknown Routes
        ========================= */}

        <Route
          path="*"
          element={<Navigate to="/dashboard" replace />}
        />

      </Routes>
    </BrowserRouter>
  );
}

export default App;