import {
  BarChart3,
  ClipboardCheck,
  FileText,
  LayoutDashboard,
  LogOut,
  Menu,
  ShieldCheck,
  X,
} from "lucide-react";
import { useState } from "react";
import { NavLink, Outlet } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function AppLayout() {
  const { user, logout } = useAuth();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const role = user?.role;

  const navigation = [
    {
      name: "Dashboard",
      path: "/dashboard",
      icon: LayoutDashboard,
      show: true,
    },
    {
      name: "Decisions",
      path: "/decisions",
      icon: FileText,
      show: true,
    },
    {
      name: "Approvals",
      path: "/approvals",
      icon: ClipboardCheck,
      show:
        role === "Reviewer" ||
        role === "Manager" ||
        role === "Administrator",
    },
    {
      name: "Reports",
      path: "/reports",
      icon: BarChart3,
      show: role === "Administrator",
    },
    {
      name: "Audit",
      path: "/audit",
      icon: ShieldCheck,
      show: role === "Administrator",
    },
  ];

  const visibleNavigation = navigation.filter(
    (item) => item.show,
  );

  return (
    <div className="min-h-screen bg-slate-50">

      {/* =========================
          MOBILE HEADER
      ========================= */}

      <header className="fixed left-0 right-0 top-0 z-40 flex h-16 items-center justify-between border-b border-slate-200 bg-white px-4 lg:hidden">

        <button
          type="button"
          onClick={() => setSidebarOpen(true)}
          className="rounded-lg p-2 text-slate-600 transition hover:bg-slate-100"
          aria-label="Open navigation"
        >
          <Menu size={22} />
        </button>

        <div className="flex items-center gap-2">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-blue-600 text-sm font-bold text-white">
            ED
          </div>

          <span className="font-semibold text-slate-800">
            Expert Decision
          </span>
        </div>

        <div className="w-10" />
      </header>

      {/* =========================
          MOBILE OVERLAY
      ========================= */}

      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-slate-900/40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* =========================
          SIDEBAR
      ========================= */}

      <aside
        className={`fixed left-0 top-0 z-50 flex h-screen w-64 flex-col border-r border-slate-200 bg-white transition-transform duration-300 lg:translate-x-0 ${
          sidebarOpen
            ? "translate-x-0"
            : "-translate-x-full"
        }`}
      >

        {/* Logo */}

        <div className="flex h-16 items-center justify-between border-b border-slate-200 px-5">

          <div className="flex items-center gap-3">

            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-600 font-bold text-white">
              ED
            </div>

            <div>
              <p className="text-sm font-bold text-slate-900">
                Expert Decision
              </p>

              <p className="text-xs text-slate-500">
                Replay Platform
              </p>
            </div>

          </div>

          <button
            type="button"
            onClick={() => setSidebarOpen(false)}
            className="rounded-lg p-2 text-slate-500 transition hover:bg-slate-100 lg:hidden"
            aria-label="Close navigation"
          >
            <X size={20} />
          </button>

        </div>

        {/* Navigation */}

        <nav className="flex-1 space-y-1 overflow-y-auto px-3 py-5">

          {visibleNavigation.map((item) => {
            const Icon = item.icon;

            return (
              <NavLink
                key={item.path}
                to={item.path}
                onClick={() => setSidebarOpen(false)}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-xl px-4 py-3 text-sm font-medium transition ${
                    isActive
                      ? "bg-blue-50 text-blue-700"
                      : "text-slate-600 hover:bg-slate-50 hover:text-slate-900"
                  }`
                }
              >
                <Icon size={19} />

                <span>{item.name}</span>
              </NavLink>
            );
          })}

        </nav>

        {/* User Section */}

        <div className="border-t border-slate-200 p-4">

          <div className="mb-3 rounded-xl bg-slate-50 p-3">

            <p className="truncate text-sm font-semibold text-slate-900">
              {user?.full_name || "User"}
            </p>

            <p className="truncate text-xs text-slate-500">
              {user?.email || ""}
            </p>

            <span className="mt-2 inline-flex rounded-full bg-blue-100 px-2.5 py-1 text-xs font-medium text-blue-700">
              {role || "User"}
            </span>

          </div>

          <button
            type="button"
            onClick={logout}
            className="flex w-full items-center gap-3 rounded-xl px-4 py-3 text-sm font-medium text-red-600 transition hover:bg-red-50"
          >
            <LogOut size={19} />

            <span>Logout</span>
          </button>

        </div>

      </aside>

      {/* =========================
          MAIN CONTENT
      ========================= */}

      <main className="min-h-screen lg:ml-64">

        {/* Desktop Top Bar */}

        <div className="hidden h-16 items-center justify-between border-b border-slate-200 bg-white px-8 lg:flex">

          <div>
            <p className="text-sm text-slate-500">
              Welcome back
            </p>

            <p className="font-semibold text-slate-900">
              {user?.full_name || "User"}
            </p>
          </div>

          <div className="text-right">

            <p className="text-sm font-medium text-slate-700">
              {role || "User"}
            </p>

            <p className="text-xs text-slate-500">
              Expert Decision Replay Platform
            </p>

          </div>

        </div>

        {/* Page */}

        <div className="p-4 pt-20 sm:p-6 lg:p-8 lg:pt-8">
          <Outlet />
        </div>

      </main>

    </div>
  );
}