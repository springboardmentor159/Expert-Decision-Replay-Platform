import { Navigate, Route, Routes } from 'react-router-dom';
import { useAuth } from './context/AuthContext';
import Layout from './components/Layout';
import AuthPage from './pages/AuthPage';
import Dashboard from './pages/Dashboard';
import DecisionListPage from './pages/DecisionListPage';
import DecisionEditor from './pages/DecisionEditor';
import DecisionWorkspace from './pages/DecisionWorkspace';
import ReportCenter from './pages/ReportCenter';
import AuditCenter from './pages/AuditCenter';
import { LoadingState } from './components/ui';

function Protected() { const { isAuthenticated, initializing } = useAuth(); if (initializing) return <LoadingState />; return isAuthenticated ? <Layout /> : <Navigate to="/login" replace />; }
function AdminOnly({ children }) { const { role } = useAuth(); return ['admin', 'administrator'].includes(role) ? children : <Navigate to="/dashboard" replace />; }
export default function App() { return <Routes><Route path="/login" element={<AuthPage />} /><Route path="/register" element={<AuthPage />} /><Route element={<Protected />}><Route path="/dashboard" element={<Dashboard />} /><Route path="/decisions" element={<DecisionListPage />} /><Route path="/decisions/new" element={<DecisionEditor />} /><Route path="/decisions/:id/edit" element={<DecisionEditor />} /><Route path="/decisions/:id" element={<DecisionWorkspace />} /><Route path="/repository" element={<DecisionListPage />} /><Route path="/reports" element={<ReportCenter />} /><Route path="/audit" element={<AdminOnly><AuditCenter /></AdminOnly>} /></Route><Route path="*" element={<Navigate to="/dashboard" replace />} /></Routes>; }