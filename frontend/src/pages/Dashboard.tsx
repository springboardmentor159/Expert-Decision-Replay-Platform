import { useEffect, useState } from "react";
import {
  Activity,
  CheckCircle2,
  Clock3,
  FileText,
  Loader2,
  RefreshCw,
  ShieldCheck,
  Users,
} from "lucide-react";

import api from "../services/api";
import { useAuth } from "../context/AuthContext";

interface DashboardData {
  [key: string]: any;
}

interface StatCardProps {
  label: string;
  value: string | number;
  description: string;
  icon: React.ElementType;
  iconClass: string;
  iconBackground: string;
}

function StatCard({
  label,
  value,
  description,
  icon: Icon,
  iconClass,
  iconBackground,
}: StatCardProps) {
  return (
    <div className="group rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition duration-200 hover:-translate-y-0.5 hover:shadow-md">
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0">
          <p className="text-sm font-medium text-slate-500">
            {label}
          </p>

          <p className="mt-3 text-3xl font-bold tracking-tight text-slate-900">
            {value}
          </p>

          <p className="mt-2 text-xs text-slate-400">
            {description}
          </p>
        </div>

        <div
          className={`flex h-11 w-11 shrink-0 items-center justify-center rounded-xl ${iconBackground}`}
        >
          <Icon className={`h-5 w-5 ${iconClass}`} />
        </div>
      </div>
    </div>
  );
}

export default function Dashboard() {
  const { user } = useAuth();

  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const role = user?.role;

  async function loadDashboard() {
    try {
      setLoading(true);
      setError("");

      let endpoint = "/dashboard/employee";

      if (role === "Manager") {
        endpoint = "/dashboard/manager";
      } else if (role === "Administrator") {
        endpoint = "/dashboard/admin";
      } else if (role === "Reviewer") {
        endpoint = "/dashboard/employee";
      }

      const response = await api.get(endpoint);

      setData(response.data);
    } catch (err: any) {
      console.error("Failed to load dashboard:", err);

      setError(
        err?.response?.data?.detail ||
          "Unable to load dashboard data. Please try again.",
      );

      setData(null);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (user?.role) {
      loadDashboard();
    }
  }, [user?.role]);

  const getValue = (...keys: string[]) => {
    if (!data) {
      return "—";
    }

    for (const key of keys) {
      if (
        data[key] !== undefined &&
        data[key] !== null
      ) {
        if (Array.isArray(data[key])) {
          return data[key].length;
        }

        return data[key];
      }
    }

    return "—";
  };

  const getRoleTitle = () => {
    switch (role) {
      case "Employee":
        return "Employee Dashboard";

      case "Reviewer":
        return "Reviewer Dashboard";

      case "Manager":
        return "Manager Dashboard";

      case "Administrator":
        return "Administrator Dashboard";

      default:
        return "Dashboard";
    }
  };

  const getRoleDescription = () => {
    switch (role) {
      case "Employee":
        return "Create, manage and track your organizational decisions.";

      case "Reviewer":
        return "Review decision activity and monitor approval workflows.";

      case "Manager":
        return "Monitor team decisions, approvals and organizational activity.";

      case "Administrator":
        return "Monitor platform-wide decisions, users, compliance and reports.";

      default:
        return "Monitor your activity across the platform.";
    }
  };

  const getOverviewLabel = () => {
    switch (role) {
      case "Administrator":
        return "System Overview";

      case "Manager":
        return "Team Overview";

      case "Reviewer":
        return "Review Overview";

      default:
        return "Decision Overview";
    }
  };

  if (loading) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <div className="flex flex-col items-center">
          <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-blue-50">
            <Loader2 className="h-6 w-6 animate-spin text-blue-600" />
          </div>

          <p className="mt-4 text-sm font-semibold text-slate-700">
            Loading your dashboard
          </p>

          <p className="mt-1 text-xs text-slate-400">
            Fetching the latest platform data...
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">

      {/* Header */}
      <section className="relative overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-sm">
        <div className="absolute right-0 top-0 h-40 w-40 rounded-full bg-blue-50 blur-3xl" />

        <div className="relative flex flex-col gap-6 p-6 sm:p-8 lg:flex-row lg:items-center lg:justify-between">
          <div className="max-w-2xl">
            <div className="flex items-center gap-2">
              <span className="rounded-full bg-blue-50 px-3 py-1 text-xs font-semibold text-blue-700">
                {role || "User"}
              </span>

              {role === "Administrator" && (
                <span className="inline-flex items-center gap-1 rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600">
                  <ShieldCheck className="h-3.5 w-3.5" />
                  System Access
                </span>
              )}
            </div>

            <h1 className="mt-4 text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl">
              {getRoleTitle()}
            </h1>

            <p className="mt-3 text-sm leading-6 text-slate-500 sm:text-base">
              {getRoleDescription()}
            </p>

            <p className="mt-2 text-sm text-slate-500">
              Welcome back,{" "}
              <span className="font-semibold text-slate-700">
                {user?.full_name || "User"}
              </span>
              .
            </p>
          </div>

          <button
            type="button"
            onClick={loadDashboard}
            disabled={loading}
            className="inline-flex shrink-0 items-center justify-center gap-2 rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 shadow-sm transition hover:border-slate-300 hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-60"
          >
            <RefreshCw
              className={`h-4 w-4 ${
                loading ? "animate-spin" : ""
              }`}
            />
            Refresh
          </button>
        </div>
      </section>

      {/* Error */}
      {error && (
        <div
          role="alert"
          className="rounded-2xl border border-red-200 bg-red-50 p-4"
        >
          <div className="flex items-start gap-3">
            <div className="mt-0.5 rounded-lg bg-red-100 p-2">
              <Activity className="h-4 w-4 text-red-600" />
            </div>

            <div>
              <p className="text-sm font-semibold text-red-800">
                Unable to load dashboard
              </p>

              <p className="mt-1 text-sm text-red-700">
                {error}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Statistics */}
      <section>
        <div className="mb-4">
          <h2 className="text-lg font-semibold text-slate-900">
            At a glance
          </h2>

          <p className="mt-1 text-sm text-slate-500">
            Key metrics from your current platform activity.
          </p>
        </div>

        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">

          <StatCard
            label="Total Decisions"
            value={getValue(
              "total_decisions",
              "total",
            )}
            description="Decisions available to you"
            icon={FileText}
            iconClass="text-blue-600"
            iconBackground="bg-blue-50"
          />

          <StatCard
            label="Pending Approvals"
            value={getValue(
              "pending_approvals",
            )}
            description="Awaiting review or action"
            icon={Clock3}
            iconClass="text-amber-600"
            iconBackground="bg-amber-50"
          />

          <StatCard
            label="Approved"
            value={getValue(
              "approved_decisions",
              "approved",
            )}
            description="Decisions approved"
            icon={CheckCircle2}
            iconClass="text-emerald-600"
            iconBackground="bg-emerald-50"
          />

          <StatCard
            label="Recent Activity"
            value={getValue(
              "recent_activity",
              "activity",
            )}
            description="Recent platform activity"
            icon={Activity}
            iconClass="text-violet-600"
            iconBackground="bg-violet-50"
          />
        </div>
      </section>

      {/* Backend Overview */}
      <section className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">

        <div className="border-b border-slate-200 px-6 py-5">
          <div className="flex items-start justify-between gap-4">

            <div className="flex items-start gap-3">
              <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-blue-50">
                {role === "Manager" ? (
                  <Users className="h-5 w-5 text-blue-600" />
                ) : role === "Administrator" ? (
                  <ShieldCheck className="h-5 w-5 text-blue-600" />
                ) : (
                  <Activity className="h-5 w-5 text-blue-600" />
                )}
              </div>

              <div>
                <h2 className="text-lg font-semibold text-slate-900">
                  {getOverviewLabel()}
                </h2>

                <p className="mt-1 text-sm text-slate-500">
                  Live information returned by the platform backend.
                </p>
              </div>
            </div>

            <span className="hidden rounded-full bg-emerald-50 px-3 py-1 text-xs font-medium text-emerald-700 sm:inline-flex">
              Live data
            </span>
          </div>
        </div>

        <div className="p-6">

          {data && Object.keys(data).length > 0 ? (
            <div className="grid gap-4 md:grid-cols-2">

              {Object.entries(data).map(
                ([key, value]) => (
                  <div
                    key={key}
                    className="rounded-xl border border-slate-200 bg-slate-50 p-4 transition hover:border-slate-300 hover:bg-white"
                  >
                    <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">
                      {key.replace(/_/g, " ")}
                    </p>

                    <div className="mt-2">
                      {Array.isArray(value) ? (
                        <div>
                          <p className="text-xl font-bold text-slate-800">
                            {value.length}
                          </p>

                          <p className="mt-0.5 text-xs text-slate-500">
                            items
                          </p>
                        </div>
                      ) : typeof value === "object" &&
                        value !== null ? (
                        <p className="break-words text-sm font-medium leading-6 text-slate-700">
                          {JSON.stringify(value)}
                        </p>
                      ) : (
                        <p className="break-words text-xl font-bold text-slate-800">
                          {String(value)}
                        </p>
                      )}
                    </div>
                  </div>
                ),
              )}

            </div>
          ) : (
            <div className="py-12 text-center">
              <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-slate-100">
                <Activity className="h-5 w-5 text-slate-400" />
              </div>

              <p className="mt-4 text-sm font-semibold text-slate-700">
                No dashboard data available
              </p>

              <p className="mt-1 text-sm text-slate-500">
                There is currently no additional information to display.
              </p>
            </div>
          )}

        </div>
      </section>

    </div>
  );
}