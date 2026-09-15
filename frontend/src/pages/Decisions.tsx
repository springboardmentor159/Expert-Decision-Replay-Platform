import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  AlertCircle,
  ArrowRight,
  FileText,
  Filter,
  Loader2,
  Plus,
  RefreshCw,
  Search,
  X,
} from "lucide-react";

import {
  getDecisions,
  type Decision,
} from "../services/decisions";

interface StatusConfig {
  label: string;
  className: string;
  dotClassName: string;
}

export default function Decisions() {
  const navigate = useNavigate();

  const [decisions, setDecisions] = useState<Decision[]>([]);
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState("");
  const [category, setCategory] = useState("");

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadDecisions = async () => {
    try {
      setLoading(true);
      setError("");

      const response = await getDecisions({
        search: search.trim() || undefined,
        status: status || undefined,
        category: category.trim() || undefined,
      });

      if (Array.isArray(response)) {
        setDecisions(response);
      } else {
        setDecisions(response.items || []);
      }
    } catch (err: any) {
      console.error("Failed to load decisions:", err);

      setError(
        err?.response?.data?.detail ||
          "Unable to load decisions. Please try again.",
      );

      setDecisions([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDecisions();
  }, []);

  const handleSearch = (event: React.FormEvent) => {
    event.preventDefault();
    loadDecisions();
  };

  const clearFilters = () => {
    setSearch("");
    setStatus("");
    setCategory("");

    setTimeout(() => {
      loadDecisions();
    }, 0);
  };

  const getStatusConfig = (
    value?: string,
  ): StatusConfig => {
    switch (value) {
      case "Approved":
        return {
          label: "Approved",
          className:
            "border-emerald-200 bg-emerald-50 text-emerald-700",
          dotClassName: "bg-emerald-500",
        };

      case "Rejected":
        return {
          label: "Rejected",
          className:
            "border-red-200 bg-red-50 text-red-700",
          dotClassName: "bg-red-500",
        };

      case "Under Review":
        return {
          label: "Under Review",
          className:
            "border-amber-200 bg-amber-50 text-amber-700",
          dotClassName: "bg-amber-500",
        };

      case "Archived":
        return {
          label: "Archived",
          className:
            "border-slate-200 bg-slate-100 text-slate-600",
          dotClassName: "bg-slate-400",
        };

      case "Draft":
      default:
        return {
          label: value || "Draft",
          className:
            "border-blue-200 bg-blue-50 text-blue-700",
          dotClassName: "bg-blue-500",
        };
    }
  };

  const formatDate = (value?: string) => {
    if (!value) {
      return "—";
    }

    const date = new Date(value);

    if (Number.isNaN(date.getTime())) {
      return value;
    }

    return date.toLocaleDateString("en-IN", {
      day: "2-digit",
      month: "short",
      year: "numeric",
    });
  };

  const hasFilters =
    Boolean(search.trim()) ||
    Boolean(status) ||
    Boolean(category.trim());

  return (
    <div className="space-y-7">

      {/* =====================================================
          PAGE HEADER
      ===================================================== */}

      <section className="relative overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-sm">

        <div className="absolute -right-12 -top-16 h-48 w-48 rounded-full bg-blue-50 blur-3xl" />

        <div className="relative flex flex-col gap-6 p-6 sm:p-8 lg:flex-row lg:items-center lg:justify-between">

          <div className="max-w-3xl">

            <div className="flex items-center gap-3">

              <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-blue-600 text-white shadow-sm">
                <FileText className="h-6 w-6" />
              </div>

              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.16em] text-blue-600">
                  Decision Repository
                </p>

                <h1 className="mt-1 text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl">
                  Decisions
                </h1>
              </div>

            </div>

            <p className="mt-4 max-w-2xl text-sm leading-6 text-slate-500 sm:text-base">
              Create, review, compare and manage organizational
              decisions from one centralized workspace.
            </p>

          </div>

          <button
            type="button"
            onClick={() =>
              navigate("/decisions/create")
            }
            className="inline-flex shrink-0 items-center justify-center gap-2 rounded-xl bg-blue-600 px-5 py-3 text-sm font-semibold text-white shadow-sm shadow-blue-600/10 transition hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
          >
            <Plus className="h-4.5 w-4.5" />
            Create Decision
          </button>

        </div>
      </section>

      {/* =====================================================
          SEARCH & FILTERS
      ===================================================== */}

      <section className="rounded-2xl border border-slate-200 bg-white shadow-sm">

        <div className="border-b border-slate-100 px-5 py-4 sm:px-6">

          <div className="flex items-center gap-3">

            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-slate-100">
              <Filter className="h-4 w-4 text-slate-600" />
            </div>

            <div>
              <h2 className="text-sm font-semibold text-slate-900">
                Search & Filter
              </h2>

              <p className="mt-0.5 text-xs text-slate-500">
                Find decisions using keywords, status or category.
              </p>
            </div>

          </div>

        </div>

        <form
          onSubmit={handleSearch}
          className="p-5 sm:p-6"
        >

          <div className="flex flex-col gap-3 lg:flex-row">

            <div className="relative flex-1">

              <Search className="absolute left-4 top-1/2 h-4.5 w-4.5 -translate-y-1/2 text-slate-400" />

              <input
                type="text"
                value={search}
                onChange={(event) =>
                  setSearch(event.target.value)
                }
                placeholder="Search by title or problem statement..."
                aria-label="Search decisions"
                className="w-full rounded-xl border border-slate-200 bg-slate-50 py-3 pl-11 pr-4 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-blue-500 focus:bg-white focus:ring-2 focus:ring-blue-500/20"
              />

            </div>

            <button
              type="submit"
              disabled={loading}
              className="inline-flex items-center justify-center gap-2 rounded-xl bg-slate-900 px-6 py-3 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
            >
              <Search className="h-4 w-4" />
              Search
            </button>

          </div>

          <div className="mt-4 grid gap-3 sm:grid-cols-2">

            <select
              value={status}
              onChange={(event) =>
                setStatus(event.target.value)
              }
              aria-label="Filter by status"
              className="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-700 outline-none transition focus:border-blue-500 focus:bg-white focus:ring-2 focus:ring-blue-500/20"
            >
              <option value="">
                All Statuses
              </option>

              <option value="Draft">
                Draft
              </option>

              <option value="Under Review">
                Under Review
              </option>

              <option value="Approved">
                Approved
              </option>

              <option value="Rejected">
                Rejected
              </option>

              <option value="Archived">
                Archived
              </option>
            </select>

            <input
              type="text"
              value={category}
              onChange={(event) =>
                setCategory(event.target.value)
              }
              placeholder="Filter by category..."
              aria-label="Filter by category"
              className="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-700 outline-none transition placeholder:text-slate-400 focus:border-blue-500 focus:bg-white focus:ring-2 focus:ring-blue-500/20"
            />

          </div>

          {hasFilters && (
            <div className="mt-4 flex flex-col gap-3 border-t border-slate-100 pt-4 sm:flex-row sm:items-center sm:justify-between">

              <div className="flex flex-wrap items-center gap-2">

                <span className="text-xs font-medium text-slate-500">
                  Active filters:
                </span>

                {search.trim() && (
                  <span className="rounded-full bg-blue-50 px-2.5 py-1 text-xs font-medium text-blue-700">
                    Search
                  </span>
                )}

                {status && (
                  <span className="rounded-full bg-amber-50 px-2.5 py-1 text-xs font-medium text-amber-700">
                    {status}
                  </span>
                )}

                {category.trim() && (
                  <span className="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-medium text-slate-600">
                    {category.trim()}
                  </span>
                )}

              </div>

              <button
                type="button"
                onClick={clearFilters}
                className="inline-flex items-center justify-center gap-1.5 self-start text-sm font-medium text-slate-600 transition hover:text-red-600 sm:self-auto"
              >
                <X className="h-4 w-4" />
                Clear filters
              </button>

            </div>
          )}

        </form>
      </section>

      {/* =====================================================
          ERROR
      ===================================================== */}

      {error && (
        <div
          role="alert"
          className="rounded-2xl border border-red-200 bg-red-50 p-4"
        >
          <div className="flex items-start gap-3">

            <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-red-100">
              <AlertCircle className="h-4.5 w-4.5 text-red-600" />
            </div>

            <div>
              <p className="text-sm font-semibold text-red-800">
                Unable to load decisions
              </p>

              <p className="mt-1 text-sm leading-5 text-red-700">
                {error}
              </p>

              <button
                type="button"
                onClick={loadDecisions}
                className="mt-3 inline-flex items-center gap-1.5 text-sm font-semibold text-red-700 hover:text-red-800"
              >
                <RefreshCw className="h-3.5 w-3.5" />
                Try again
              </button>
            </div>

          </div>
        </div>
      )}

      {/* =====================================================
          RESULT SUMMARY
      ===================================================== */}

      {!loading && !error && (
        <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">

          <div>
            <div className="flex items-center gap-2">

              <h2 className="text-lg font-semibold text-slate-900">
                Decision Records
              </h2>

              <span className="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-semibold text-slate-600">
                {decisions.length}
              </span>

            </div>

            <p className="mt-1 text-sm text-slate-500">
              {hasFilters
                ? "Showing decisions matching your current filters."
                : "Showing available decisions in the repository."}
            </p>
          </div>

          <button
            type="button"
            onClick={loadDecisions}
            disabled={loading}
            className="inline-flex items-center justify-center gap-2 self-start rounded-xl border border-slate-200 bg-white px-3.5 py-2.5 text-sm font-medium text-slate-600 shadow-sm transition hover:bg-slate-50 hover:text-slate-800 sm:self-auto"
          >
            <RefreshCw className="h-4 w-4" />
            Refresh
          </button>

        </div>
      )}

      {/* =====================================================
          LOADING
      ===================================================== */}

      {loading ? (
        <div className="flex min-h-[320px] items-center justify-center rounded-2xl border border-slate-200 bg-white shadow-sm">

          <div className="text-center">

            <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-blue-50">
              <Loader2 className="h-6 w-6 animate-spin text-blue-600" />
            </div>

            <p className="mt-4 text-sm font-semibold text-slate-700">
              Loading decisions
            </p>

            <p className="mt-1 text-xs text-slate-400">
              Fetching the latest decision records...
            </p>

          </div>

        </div>
      ) : decisions.length === 0 ? (

        /* =====================================================
            EMPTY STATE
        ===================================================== */

        <div className="rounded-2xl border border-slate-200 bg-white px-6 py-16 text-center shadow-sm">

          <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-blue-50">
            <FileText className="h-7 w-7 text-blue-600" />
          </div>

          <h2 className="mt-5 text-lg font-semibold text-slate-900">
            No decisions found
          </h2>

          <p className="mx-auto mt-2 max-w-lg text-sm leading-6 text-slate-500">
            {hasFilters
              ? "No decisions match your current search or filters. Try adjusting the filters or create a new decision."
              : "There are currently no decision records available. Create a decision to begin the workflow."}
          </p>

          <div className="mt-6 flex flex-wrap justify-center gap-3">

            {hasFilters && (
              <button
                type="button"
                onClick={clearFilters}
                className="inline-flex items-center gap-2 rounded-xl border border-slate-200 bg-white px-5 py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-50"
              >
                <X className="h-4 w-4" />
                Clear Filters
              </button>
            )}

            <button
              type="button"
              onClick={() =>
                navigate("/decisions/create")
              }
              className="inline-flex items-center gap-2 rounded-xl bg-blue-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-blue-700"
            >
              <Plus className="h-4 w-4" />
              Create Decision
            </button>

          </div>

        </div>
      ) : (

        /* =====================================================
            DECISION LIST
        ===================================================== */

        <div className="space-y-4">

          {decisions.map((decision) => {

            const statusConfig =
              getStatusConfig(decision.status);

            return (
              <article
                key={decision.id}
                className="group rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition duration-200 hover:-translate-y-0.5 hover:border-blue-200 hover:shadow-md sm:p-6"
              >

                <div className="flex flex-col gap-5">

                  {/* Decision header */}

                  <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">

                    <div className="min-w-0 flex-1">

                      <div className="flex flex-wrap items-center gap-2.5">

                        <span className="rounded-lg bg-slate-100 px-2.5 py-1 text-xs font-semibold text-slate-500">
                          #{decision.id}
                        </span>

                        <span
                          className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-xs font-semibold ${statusConfig.className}`}
                        >
                          <span
                            className={`h-1.5 w-1.5 rounded-full ${statusConfig.dotClassName}`}
                          />
                          {statusConfig.label}
                        </span>

                      </div>

                      <h2 className="mt-3 break-words text-lg font-semibold leading-7 text-slate-900 sm:text-xl">
                        {decision.title}
                      </h2>

                      {decision.category && (
                        <span className="mt-2 inline-block rounded-md bg-blue-50 px-2.5 py-1 text-xs font-semibold text-blue-700">
                          {decision.category}
                        </span>
                      )}

                    </div>

                  </div>

                  {/* Problem statement */}

                  {decision.problem_statement && (
                    <div className="rounded-xl bg-slate-50 px-4 py-3.5">
                      <p className="line-clamp-3 text-sm leading-6 text-slate-600">
                        {decision.problem_statement}
                      </p>
                    </div>
                  )}

                  {/* Footer */}

                  <div className="flex flex-col gap-4 border-t border-slate-100 pt-4 sm:flex-row sm:items-center sm:justify-between">

                    <div className="flex flex-wrap items-center gap-x-5 gap-y-2 text-xs text-slate-500">

                      <span>
                        Decision ID{" "}
                        <strong className="font-semibold text-slate-700">
                          #{decision.id}
                        </strong>
                      </span>

                      {decision.created_at && (
                        <span>
                          Created{" "}
                          <strong className="font-semibold text-slate-700">
                            {formatDate(
                              decision.created_at,
                            )}
                          </strong>
                        </span>
                      )}

                      {decision.updated_at && (
                        <span>
                          Updated{" "}
                          <strong className="font-semibold text-slate-700">
                            {formatDate(
                              decision.updated_at,
                            )}
                          </strong>
                        </span>
                      )}

                    </div>

                    <button
                      type="button"
                      onClick={() =>
                        navigate(
                          `/decisions/${decision.id}`,
                        )
                      }
                      className="inline-flex items-center justify-center gap-2 rounded-xl border border-slate-200 px-4 py-2.5 text-sm font-semibold text-slate-700 transition group-hover:border-blue-200 hover:bg-blue-50 hover:text-blue-700"
                    >
                      View Details
                      <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
                    </button>

                  </div>

                </div>

              </article>
            );
          })}

        </div>
      )}

    </div>
  );
}