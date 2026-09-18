import { BarChart3, BookOpen, ChevronRight, FileCheck2, FileText, LayoutDashboard, LogOut, ShieldCheck, Activity as ActivityIcon, Users } from "lucide-react";
import { NavLink } from "react-router-dom";
import "./Navigation.css";
import { useAuth } from "../auth/AuthContext";

interface NavigationItem { label: string; path: string; icon: typeof LayoutDashboard; }

const common: NavigationItem[] = [
  { label: "Dashboard", path: "/dashboard", icon: LayoutDashboard },
  { label: "Decisions", path: "/decisions", icon: FileText },
  { label: "Knowledge Repository", path: "/repository", icon: BookOpen },
];

function getNavigation(role: string): NavigationItem[] {
  if (role === "reviewer") return [...common, { label: "Review Queue", path: "/decisions?status=Under%20Review", icon: FileCheck2 }, { label: "Activity", path: "/activity", icon: ActivityIcon }];
  if (role === "manager") return [...common, { label: "Pending Approvals", path: "/decisions?status=Under%20Review", icon: FileCheck2 }, { label: "Reports", path: "/reports", icon: BarChart3 }, { label: "Activity", path: "/activity", icon: ActivityIcon }];
  if (role === "administrator") return [...common, { label: "Reports", path: "/reports", icon: BarChart3 }, { label: "Activity", path: "/activity", icon: ActivityIcon }, { label: "User Management", path: "/admin/users", icon: Users }];
  return [...common, { label: "Create Decision", path: "/decisions/new", icon: FileCheck2 }, { label: "Activity", path: "/activity", icon: ActivityIcon }];
}

function getInitials(name: string) { return name.trim().split(/\s+/).slice(0, 2).map((part) => part.charAt(0).toUpperCase()).join(""); }
function formatRole(role: string) { return role.toLowerCase().replace(/\b\w/g, (character) => character.toUpperCase()); }

export default function Navigation() {
  const { user, logout } = useAuth();
  const items = getNavigation(String(user?.role ?? "").toLowerCase());
  return <aside className="app-sidebar">
    <div className="app-sidebar-brand"><NavLink to="/dashboard" className="app-brand"><span className="app-brand-mark" aria-hidden="true"><ShieldCheck size={20} strokeWidth={2.2} /></span><span className="app-brand-copy"><span className="app-brand-name">Expert Decision</span><span className="app-brand-subtitle">Replay Platform</span></span></NavLink></div>
    <div className="app-sidebar-divider" />
    <nav className="main-navigation" aria-label="Main navigation"><p className="navigation-section-label">{user?.role === "administrator" ? "Administration" : "Workspace"}</p><div className="navigation-items">{items.map((item) => { const Icon=item.icon; return <NavLink key={item.path} to={item.path} className={({isActive}) => `navigation-link ${isActive ? "navigation-link-active" : ""}`}><span className="navigation-link-icon"><Icon size={18} strokeWidth={2}/></span><span className="navigation-link-label">{item.label}</span><ChevronRight className="navigation-link-arrow" size={15} strokeWidth={2}/></NavLink>; })}</div></nav>
    <div className="app-sidebar-spacer" />
    {user && <div className="sidebar-user"><div className="sidebar-user-profile"><div className="sidebar-user-avatar" aria-hidden="true">{getInitials(user.full_name)}</div><div className="sidebar-user-details"><p className="sidebar-user-name">{user.full_name}</p><p className="sidebar-user-role">{formatRole(String(user.role))}</p></div></div><button type="button" className="logout-button" onClick={logout} aria-label="Log out"><LogOut size={17} strokeWidth={2}/><span>Sign out</span></button></div>}
  </aside>;
}
