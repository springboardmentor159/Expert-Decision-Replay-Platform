import { useEffect, useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import {
  ArrowLeft,
  GitCompare,
  Loader2,
  Plus,
  AlertCircle,
  X,
  DollarSign,
  ShieldAlert,
  Gauge,
  CheckCircle2,
  RefreshCw,
  Edit3,
  Trash2,
  Save,
  Sparkles,
  BarChart3,
  TrendingUp,
} from "lucide-react";

import {
  getAlternatives,
  createAlternative,
  updateAlternative,
  deleteAlternative,
  compareAlternatives,
  type Alternative,
} from "../services/alternatives";

import { getApiErrorMessage } from "../utils/errors";

export default function Alternatives() {
  const { decisionId } = useParams();
  const navigate = useNavigate();

  const numericDecisionId = Number(decisionId);

  const [alternatives, setAlternatives] = useState<
    Alternative[]
  >([]);

  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [comparing, setComparing] = useState(false);
  const [refreshing, setRefreshing] = useState(false);

  const [deletingId, setDeletingId] =
    useState<number | null>(null);

  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const [showForm, setShowForm] = useState(false);
  const [showComparison, setShowComparison] =
    useState(false);

  const [comparisonData, setComparisonData] =
    useState<any>(null);

  const [editingId, setEditingId] =
    useState<number | null>(null);

  const [name, setName] = useState("");
  const [description, setDescription] =
    useState("");
  const [estimatedCost, setEstimatedCost] =
    useState("");
  const [feasibilityScore, setFeasibilityScore] =
    useState("");
  const [riskLevel, setRiskLevel] =
    useState("Low");

  /* =========================
     LOAD
  ========================= */

  async function loadAlternatives(
    showFullLoader = true,
  ) {
    if (
      !Number.isInteger(numericDecisionId) ||
      numericDecisionId <= 0
    ) {
      setError("Invalid decision ID.");
      setLoading(false);
      return;
    }

    try {
      if (showFullLoader) {
        setLoading(true);
      } else {
        setRefreshing(true);
      }

      setError("");

      const response = await getAlternatives(
        numericDecisionId,
      );

      if (Array.isArray(response)) {
        setAlternatives(response);
      } else {
        setAlternatives(response.items || []);
      }
    } catch (err: any) {
      console.error(err);

      setError(
        getApiErrorMessage(
          err,
          "Unable to load alternatives.",
        ),
      );
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }

  useEffect(() => {
    loadAlternatives();
  }, [numericDecisionId]);

  /* =========================
     SUMMARY
  ========================= */

  const summary = useMemo(() => {
    if (alternatives.length === 0) {
      return {
        averageFeasibility: 0,
        highestFeasibility: 0,
        lowestCost: null as number | null,
        highRiskCount: 0,
      };
    }

    const scores = alternatives
      .map((item) => item.feasibility_score)
      .filter(
        (score): score is number =>
          typeof score === "number",
      );

    const costs = alternatives
      .map((item) => item.estimated_cost)
      .filter(
        (cost): cost is number =>
          typeof cost === "number",
      );

    const highRiskCount =
      alternatives.filter(
        (item) =>
          item.risk_level === "High" ||
          item.risk_level === "Critical",
      ).length;

    return {
      averageFeasibility:
        scores.length > 0
          ? scores.reduce(
              (sum, score) => sum + score,
              0,
            ) / scores.length
          : 0,

      highestFeasibility:
        scores.length > 0
          ? Math.max(...scores)
          : 0,

      lowestCost:
        costs.length > 0
          ? Math.min(...costs)
          : null,

      highRiskCount,
    };
  }, [alternatives]);

  /* =========================
     FORM
  ========================= */

  function resetForm() {
    setName("");
    setDescription("");
    setEstimatedCost("");
    setFeasibilityScore("");
    setRiskLevel("Low");
    setEditingId(null);
  }

  function openCreateForm() {
    resetForm();
    setError("");
    setSuccess("");
    setShowForm(true);

    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  }

  function startEditing(
    alternative: Alternative,
  ) {
    setEditingId(alternative.id);

    setName(alternative.name || "");
    setDescription(
      alternative.description || "",
    );

    setEstimatedCost(
      alternative.estimated_cost !== undefined
        ? String(alternative.estimated_cost)
        : "",
    );

    setFeasibilityScore(
      alternative.feasibility_score !== undefined
        ? String(alternative.feasibility_score)
        : "",
    );

    setRiskLevel(
      alternative.risk_level || "Low",
    );

    setError("");
    setSuccess("");
    setShowForm(true);

    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  }

  function closeForm() {
    if (submitting) {
      return;
    }

    resetForm();
    setShowForm(false);
    setError("");
  }

  /* =========================
     CREATE / UPDATE
  ========================= */

  async function handleSubmitAlternative(
    event: React.FormEvent,
  ) {
    event.preventDefault();

    if (
      !Number.isInteger(numericDecisionId) ||
      numericDecisionId <= 0
    ) {
      setError("Invalid decision ID.");
      return;
    }

    if (!name.trim()) {
      setError("Alternative name is required.");
      return;
    }

    if (!description.trim()) {
      setError(
        "Alternative description is required.",
      );
      return;
    }

    if (!estimatedCost) {
      setError("Estimated cost is required.");
      return;
    }

    if (!feasibilityScore) {
      setError("Feasibility score is required.");
      return;
    }

    const cost = Number(estimatedCost);
    const score = Number(feasibilityScore);

    if (!Number.isFinite(cost) || cost < 0) {
      setError(
        "Estimated cost must be a valid non-negative number.",
      );
      return;
    }

    if (
      !Number.isFinite(score) ||
      score < 1 ||
      score > 5
    ) {
      setError(
        "Feasibility score must be between 1 and 5.",
      );
      return;
    }

    try {
      setSubmitting(true);
      setError("");
      setSuccess("");

      if (editingId !== null) {
        await updateAlternative(editingId, {
          name: name.trim(),
          description: description.trim(),
          estimated_cost: cost,
          feasibility_score: score,
          risk_level: riskLevel,
        });

        setSuccess(
          "Alternative updated successfully.",
        );
      } else {
        await createAlternative(
          numericDecisionId,
          {
            name: name.trim(),
            description: description.trim(),
            estimated_cost: cost,
            feasibility_score: score,
            risk_level: riskLevel,
          },
        );

        setSuccess(
          "Alternative added successfully.",
        );
      }

      resetForm();
      setShowForm(false);

      await loadAlternatives(false);

      setTimeout(() => {
        setSuccess("");
      }, 3000);
    } catch (err: any) {
      console.error(err);

      setError(
        getApiErrorMessage(
          err,
          editingId !== null
            ? "Unable to update alternative."
            : "Unable to create alternative.",
        ),
      );
    } finally {
      setSubmitting(false);
    }
  }

  /* =========================
     DELETE
  ========================= */

  async function handleDelete(
    alternative: Alternative,
  ) {
    const confirmed = window.confirm(
      `Are you sure you want to delete "${alternative.name}"? This action cannot be undone.`,
    );

    if (!confirmed) {
      return;
    }

    try {
      setDeletingId(alternative.id);
      setError("");
      setSuccess("");

      await deleteAlternative(
        alternative.id,
      );

      setAlternatives((current) =>
        current.filter(
          (item) => item.id !== alternative.id,
        ),
      );

      setSuccess(
        "Alternative deleted successfully.",
      );

      setTimeout(() => {
        setSuccess("");
      }, 3000);
    } catch (err: any) {
      console.error(err);

      setError(
        getApiErrorMessage(
          err,
          "Unable to delete alternative.",
        ),
      );
    } finally {
      setDeletingId(null);
    }
  }

  /* =========================
     COMPARE
  ========================= */

  async function handleCompare() {
    if (
      !Number.isInteger(numericDecisionId) ||
      numericDecisionId <= 0
    ) {
      setError("Invalid decision ID.");
      return;
    }

    if (alternatives.length < 2) {
      setError(
        "At least two alternatives are required for comparison.",
      );
      return;
    }

    try {
      setComparing(true);
      setError("");

      const data =
        await compareAlternatives(
          numericDecisionId,
        );

      setComparisonData(data);
      setShowComparison(true);

      setTimeout(() => {
        document
          .getElementById("comparison-section")
          ?.scrollIntoView({
            behavior: "smooth",
            block: "start",
          });
      }, 50);
    } catch (err: any) {
      console.error(err);

      setError(
        getApiErrorMessage(
          err,
          "Unable to compare alternatives.",
        ),
      );
    } finally {
      setComparing(false);
    }
  }

  /* =========================
     STYLES
  ========================= */

  function getRiskClass(risk?: string) {
    switch (risk) {
      case "Low":
        return "border-emerald-200 bg-emerald-50 text-emerald-700";

      case "Medium":
        return "border-amber-200 bg-amber-50 text-amber-700";

      case "High":
        return "border-orange-200 bg-orange-50 text-orange-700";

      case "Critical":
        return "border-red-200 bg-red-50 text-red-700";

      default:
        return "border-slate-200 bg-slate-50 text-slate-600";
    }
  }

  function getRiskDot(risk?: string) {
    switch (risk) {
      case "Low":
        return "bg-emerald-500";

      case "Medium":
        return "bg-amber-500";

      case "High":
        return "bg-orange-500";

      case "Critical":
        return "bg-red-500";

      default:
        return "bg-slate-400";
    }
  }

  function getFeasibilityClass(
    score?: number,
  ) {
    if (score === undefined) {
      return "text-slate-500";
    }

    if (score >= 4) {
      return "text-emerald-600";
    }

    if (score >= 3) {
      return "text-amber-600";
    }

    return "text-red-600";
  }

  function getFeasibilityLabel(
    score?: number,
  ) {
    if (score === undefined) {
      return "Not rated";
    }

    if (score >= 4) {
      return "Strong";
    }

    if (score >= 3) {
      return "Moderate";
    }

    return "Low";
  }

  /* =========================
     INVALID ID
  ========================= */

  if (
    !Number.isInteger(numericDecisionId) ||
    numericDecisionId <= 0
  ) {
    return (
      <div className="mx-auto max-w-6xl">
        <button
          type="button"
          onClick={() =>
            navigate("/decisions")
          }
          className="mb-6 inline-flex items-center gap-2 text-sm font-medium text-slate-600 transition hover:text-blue-600"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to Decisions
        </button>

        <div className="flex items-center gap-3 rounded-2xl border border-red-200 bg-red-50 p-6 text-sm font-medium text-red-700">
          <AlertCircle className="h-5 w-5" />
          Invalid decision ID.
        </div>
      </div>
    );
  }

  /* =========================
     LOADING
  ========================= */

  if (loading) {
    return (
      <div className="flex min-h-[500px] items-center justify-center">
        <div className="text-center">
          <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-blue-50">
            <Loader2 className="h-6 w-6 animate-spin text-blue-600" />
          </div>

          <p className="mt-4 text-sm font-medium text-slate-600">
            Loading alternatives...
          </p>

          <p className="mt-1 text-xs text-slate-400">
            Preparing the decision analysis workspace
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-7xl space-y-6">

      {/* =========================
          BACK
      ========================= */}

      <button
        type="button"
        onClick={() =>
          navigate(
            `/decisions/${numericDecisionId}`,
          )
        }
        className="inline-flex items-center gap-2 text-sm font-medium text-slate-600 transition hover:text-blue-600"
      >
        <ArrowLeft className="h-4 w-4" />
        Back to Decision
      </button>

      {/* =========================
          HERO HEADER
      ========================= */}

      <section className="overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-sm">

        <div className="relative overflow-hidden bg-gradient-to-br from-blue-50 via-white to-indigo-50 px-6 py-8 sm:px-8">

          <div className="absolute -right-20 -top-20 h-48 w-48 rounded-full bg-blue-100/50 blur-3xl" />

          <div className="relative flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">

            <div className="flex items-start gap-4">

              <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-2xl bg-blue-600 text-white shadow-lg shadow-blue-600/20">
                <GitCompare className="h-7 w-7" />
              </div>

              <div>
                <div className="mb-2 inline-flex items-center gap-2 rounded-full border border-blue-100 bg-white/80 px-3 py-1 text-xs font-semibold text-blue-700">
                  <Sparkles className="h-3.5 w-3.5" />
                  Decision Analysis
                </div>

                <h1 className="text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl">
                  Alternatives
                </h1>

                <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-500">
                  Evaluate possible solutions using
                  cost, feasibility and risk before
                  selecting a direction.
                </p>
              </div>

            </div>

            <div className="flex flex-wrap gap-3">

              <button
                type="button"
                onClick={() =>
                  loadAlternatives(false)
                }
                disabled={refreshing}
                className="inline-flex items-center justify-center gap-2 rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm font-semibold text-slate-700 shadow-sm transition hover:border-blue-200 hover:bg-blue-50 hover:text-blue-700 disabled:cursor-not-allowed disabled:opacity-60"
              >
                <RefreshCw
                  className={`h-4 w-4 ${
                    refreshing
                      ? "animate-spin"
                      : ""
                  }`}
                />
                Refresh
              </button>

              {alternatives.length > 1 && (
                <button
                  type="button"
                  onClick={handleCompare}
                  disabled={comparing}
                  className="inline-flex items-center justify-center gap-2 rounded-xl border border-blue-200 bg-blue-50 px-5 py-3 text-sm font-semibold text-blue-700 transition hover:bg-blue-100 disabled:cursor-not-allowed disabled:opacity-60"
                >
                  {comparing ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <GitCompare className="h-4 w-4" />
                  )}

                  {comparing
                    ? "Comparing..."
                    : "Compare Alternatives"}
                </button>
              )}

              <button
                type="button"
                onClick={openCreateForm}
                className="inline-flex items-center justify-center gap-2 rounded-xl bg-blue-600 px-5 py-3 text-sm font-semibold text-white shadow-sm shadow-blue-600/20 transition hover:bg-blue-700"
              >
                <Plus className="h-5 w-5" />
                Add Alternative
              </button>

            </div>

          </div>
        </div>

        {/* QUICK STATS */}

        <div className="grid border-t border-slate-100 sm:grid-cols-2 lg:grid-cols-4">

          <div className="border-b border-slate-100 p-5 sm:border-r lg:border-b-0">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold uppercase tracking-wide text-slate-400">
                Alternatives
              </span>

              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-50 text-blue-600">
                <GitCompare className="h-4 w-4" />
              </div>
            </div>

            <p className="mt-3 text-2xl font-bold text-slate-900">
              {alternatives.length}
            </p>

            <p className="mt-1 text-xs text-slate-500">
              Possible solutions
            </p>
          </div>

          <div className="border-b border-slate-100 p-5 lg:border-b-0 lg:border-r">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold uppercase tracking-wide text-slate-400">
                Avg. Feasibility
              </span>

              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-emerald-50 text-emerald-600">
                <Gauge className="h-4 w-4" />
              </div>
            </div>

            <p className="mt-3 text-2xl font-bold text-slate-900">
              {summary.averageFeasibility
                ? `${summary.averageFeasibility.toFixed(1)}/5`
                : "—"}
            </p>

            <p
              className={`mt-1 text-xs font-medium ${getFeasibilityClass(
                summary.averageFeasibility,
              )}`}
            >
              {summary.averageFeasibility
                ? getFeasibilityLabel(
                    summary.averageFeasibility,
                  )
                : "No ratings yet"}
            </p>
          </div>

          <div className="border-b border-slate-100 p-5 sm:border-r lg:border-b-0">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold uppercase tracking-wide text-slate-400">
                Lowest Cost
              </span>

              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-violet-50 text-violet-600">
                <DollarSign className="h-4 w-4" />
              </div>
            </div>

            <p className="mt-3 text-2xl font-bold text-slate-900">
              {summary.lowestCost !== null
                ? summary.lowestCost.toLocaleString()
                : "—"}
            </p>

            <p className="mt-1 text-xs text-slate-500">
              Among available alternatives
            </p>
          </div>

          <div className="p-5">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold uppercase tracking-wide text-slate-400">
                Higher Risk
              </span>

              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-orange-50 text-orange-600">
                <ShieldAlert className="h-4 w-4" />
              </div>
            </div>

            <p className="mt-3 text-2xl font-bold text-slate-900">
              {summary.highRiskCount}
            </p>

            <p className="mt-1 text-xs text-slate-500">
              High or Critical risk
            </p>
          </div>

        </div>
      </section>

      {/* =========================
          ERROR
      ========================= */}

      {error && (
        <div className="flex items-start gap-3 rounded-2xl border border-red-200 bg-red-50 px-5 py-4 text-sm font-medium text-red-700">
          <AlertCircle className="mt-0.5 h-5 w-5 shrink-0" />
          <div className="min-w-0">
            <p>{error}</p>
          </div>
        </div>
      )}

      {/* =========================
          SUCCESS
      ========================= */}

      {success && (
        <div className="flex items-start gap-3 rounded-2xl border border-emerald-200 bg-emerald-50 px-5 py-4 text-sm font-medium text-emerald-700">
          <CheckCircle2 className="mt-0.5 h-5 w-5 shrink-0" />
          <span>{success}</span>
        </div>
      )}

      {/* =========================
          FORM
      ========================= */}

      {showForm && (
        <section className="overflow-hidden rounded-3xl border border-blue-100 bg-white shadow-sm">

          <div className="border-b border-slate-100 bg-gradient-to-r from-blue-50 to-white px-6 py-6 sm:px-8">

            <div className="flex items-start justify-between gap-4">

              <div className="flex items-start gap-3">

                <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-600 text-white">
                  {editingId !== null ? (
                    <Edit3 className="h-5 w-5" />
                  ) : (
                    <Plus className="h-5 w-5" />
                  )}
                </div>

                <div>
                  <h2 className="text-lg font-bold text-slate-900">
                    {editingId !== null
                      ? "Edit Alternative"
                      : "Add Alternative"}
                  </h2>

                  <p className="mt-1 text-sm text-slate-500">
                    {editingId !== null
                      ? "Update the solution and its evaluation metrics."
                      : "Record a possible solution for this decision."}
                  </p>
                </div>

              </div>

              <button
                type="button"
                onClick={closeForm}
                disabled={submitting}
                className="rounded-xl p-2 text-slate-400 transition hover:bg-white hover:text-slate-700 disabled:cursor-not-allowed disabled:opacity-50"
                aria-label="Close form"
              >
                <X className="h-5 w-5" />
              </button>

            </div>
          </div>

          <form
            onSubmit={handleSubmitAlternative}
            className="space-y-6 p-6 sm:p-8"
          >

            {/* NAME */}

            <div>
              <label
                htmlFor="alternative-name"
                className="mb-2 block text-sm font-semibold text-slate-700"
              >
                Alternative Name *
              </label>

              <input
                id="alternative-name"
                type="text"
                value={name}
                onChange={(event) =>
                  setName(event.target.value)
                }
                placeholder="e.g. Build an internal platform"
                className="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-blue-500 focus:bg-white focus:ring-4 focus:ring-blue-500/10"
              />
            </div>

            {/* DESCRIPTION */}

            <div>
              <label
                htmlFor="alternative-description"
                className="mb-2 block text-sm font-semibold text-slate-700"
              >
                Description *
              </label>

              <textarea
                id="alternative-description"
                value={description}
                onChange={(event) =>
                  setDescription(
                    event.target.value,
                  )
                }
                placeholder="Describe how this alternative would solve the problem..."
                rows={5}
                className="w-full resize-y rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm leading-7 text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-blue-500 focus:bg-white focus:ring-4 focus:ring-blue-500/10"
              />
            </div>

            {/* METRICS */}

            <div>

              <div className="mb-3">
                <h3 className="text-sm font-bold text-slate-800">
                  Evaluation Metrics
                </h3>

                <p className="mt-1 text-xs text-slate-400">
                  These values are used to compare
                  possible solutions.
                </p>
              </div>

              <div className="grid gap-4 md:grid-cols-3">

                {/* COST */}

                <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">

                  <div className="mb-3 flex items-center gap-2">
                    <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-white text-slate-500 shadow-sm">
                      <DollarSign className="h-4 w-4" />
                    </div>

                    <label
                      htmlFor="estimated-cost"
                      className="text-sm font-semibold text-slate-700"
                    >
                      Estimated Cost
                    </label>
                  </div>

                  <input
                    id="estimated-cost"
                    type="number"
                    min="0"
                    step="0.01"
                    value={estimatedCost}
                    onChange={(event) =>
                      setEstimatedCost(
                        event.target.value,
                      )
                    }
                    placeholder="5000"
                    className="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10"
                  />

                  <p className="mt-2 text-xs text-slate-400">
                    Enter the estimated numeric cost.
                  </p>
                </div>

                {/* FEASIBILITY */}

                <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">

                  <div className="mb-3 flex items-center gap-2">
                    <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-white text-slate-500 shadow-sm">
                      <Gauge className="h-4 w-4" />
                    </div>

                    <label
                      htmlFor="feasibility-score"
                      className="text-sm font-semibold text-slate-700"
                    >
                      Feasibility Score
                    </label>
                  </div>

                  <select
                    id="feasibility-score"
                    value={feasibilityScore}
                    onChange={(event) =>
                      setFeasibilityScore(
                        event.target.value,
                      )
                    }
                    className="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10"
                  >
                    <option value="">
                      Select score
                    </option>

                    <option value="1">
                      1 / 5 — Low
                    </option>

                    <option value="2">
                      2 / 5 — Below average
                    </option>

                    <option value="3">
                      3 / 5 — Moderate
                    </option>

                    <option value="4">
                      4 / 5 — Strong
                    </option>

                    <option value="5">
                      5 / 5 — Excellent
                    </option>
                  </select>

                  <p className="mt-2 text-xs text-slate-400">
                    Rate practical feasibility from
                    1 to 5.
                  </p>
                </div>

                {/* RISK */}

                <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">

                  <div className="mb-3 flex items-center gap-2">
                    <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-white text-slate-500 shadow-sm">
                      <ShieldAlert className="h-4 w-4" />
                    </div>

                    <label
                      htmlFor="risk-level"
                      className="text-sm font-semibold text-slate-700"
                    >
                      Risk Level
                    </label>
                  </div>

                  <select
                    id="risk-level"
                    value={riskLevel}
                    onChange={(event) =>
                      setRiskLevel(
                        event.target.value,
                      )
                    }
                    className="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10"
                  >
                    <option value="Low">
                      Low
                    </option>

                    <option value="Medium">
                      Medium
                    </option>

                    <option value="High">
                      High
                    </option>

                    <option value="Critical">
                      Critical
                    </option>
                  </select>

                  <p className="mt-2 text-xs text-slate-400">
                    Consider implementation and
                    operational risk.
                  </p>
                </div>

              </div>
            </div>

            {/* ACTIONS */}

            <div className="flex flex-col-reverse gap-3 border-t border-slate-100 pt-6 sm:flex-row sm:justify-end">

              <button
                type="button"
                onClick={closeForm}
                disabled={submitting}
                className="rounded-xl border border-slate-200 px-5 py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-60"
              >
                Cancel
              </button>

              <button
                type="submit"
                disabled={submitting}
                className="inline-flex items-center justify-center gap-2 rounded-xl bg-blue-600 px-6 py-3 text-sm font-semibold text-white shadow-sm shadow-blue-600/20 transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {submitting ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" />
                    {editingId !== null
                      ? "Saving..."
                      : "Adding..."}
                  </>
                ) : editingId !== null ? (
                  <>
                    <Save className="h-4 w-4" />
                    Save Changes
                  </>
                ) : (
                  <>
                    <Plus className="h-4 w-4" />
                    Add Alternative
                  </>
                )}
              </button>

            </div>
          </form>
        </section>
      )}

      {/* =========================
          COMPARISON
      ========================= */}

      {showComparison &&
        comparisonData && (
          <section
            id="comparison-section"
            className="overflow-hidden rounded-3xl border border-blue-100 bg-white shadow-sm"
          >

            <div className="border-b border-slate-100 bg-gradient-to-r from-indigo-50 via-white to-blue-50 px-6 py-6 sm:px-8">

              <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">

                <div className="flex items-start gap-3">

                  <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-indigo-600 text-white shadow-sm">
                    <BarChart3 className="h-5 w-5" />
                  </div>

                  <div>
                    <div className="flex items-center gap-2">
                      <h2 className="text-lg font-bold text-slate-900">
                        Alternative Comparison
                      </h2>

                      <span className="rounded-full bg-blue-100 px-2.5 py-1 text-[11px] font-bold text-blue-700">
                        BACKEND ANALYSIS
                      </span>
                    </div>

                    <p className="mt-1 text-sm text-slate-500">
                      Compare the available alternatives
                      using the backend evaluation.
                    </p>
                  </div>

                </div>

                <button
                  type="button"
                  onClick={() =>
                    setShowComparison(false)
                  }
                  className="inline-flex w-fit items-center gap-2 rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm font-semibold text-slate-600 transition hover:bg-slate-50 hover:text-slate-900"
                >
                  <X className="h-4 w-4" />
                  Close
                </button>

              </div>
            </div>

            <div className="p-6 sm:p-8">

              {/* READABLE ALTERNATIVE COMPARISON */}

              <div className="mb-6 overflow-hidden rounded-2xl border border-slate-200">

                <div className="hidden overflow-x-auto md:block">

                  <table className="w-full min-w-[700px] border-collapse text-left">

                    <thead className="bg-slate-50">
                      <tr>
                        <th className="px-5 py-4 text-xs font-bold uppercase tracking-wide text-slate-500">
                          Alternative
                        </th>

                        <th className="px-5 py-4 text-xs font-bold uppercase tracking-wide text-slate-500">
                          Cost
                        </th>

                        <th className="px-5 py-4 text-xs font-bold uppercase tracking-wide text-slate-500">
                          Feasibility
                        </th>

                        <th className="px-5 py-4 text-xs font-bold uppercase tracking-wide text-slate-500">
                          Risk
                        </th>
                      </tr>
                    </thead>

                    <tbody className="divide-y divide-slate-100">

                      {alternatives.map(
                        (alternative) => (
                          <tr
                            key={alternative.id}
                            className="transition hover:bg-slate-50"
                          >

                            <td className="px-5 py-4">
                              <p className="font-semibold text-slate-900">
                                {alternative.name}
                              </p>

                              <p className="mt-1 text-xs text-slate-400">
                                #{alternative.id}
                              </p>
                            </td>

                            <td className="px-5 py-4">
                              <span className="font-semibold text-slate-800">
                                {alternative.estimated_cost !==
                                undefined
                                  ? alternative.estimated_cost.toLocaleString()
                                  : "—"}
                              </span>
                            </td>

                            <td className="px-5 py-4">

                              <div className="flex items-center gap-3">

                                <div className="h-2 w-24 overflow-hidden rounded-full bg-slate-100">
                                  <div
                                    className="h-full rounded-full bg-blue-600"
                                    style={{
                                      width: `${
                                        ((alternative.feasibility_score ??
                                          0) /
                                          5) *
                                        100
                                      }%`,
                                    }}
                                  />
                                </div>

                                <span
                                  className={`font-bold ${getFeasibilityClass(
                                    alternative.feasibility_score,
                                  )}`}
                                >
                                  {alternative.feasibility_score !==
                                  undefined
                                    ? `${alternative.feasibility_score}/5`
                                    : "—"}
                                </span>

                              </div>

                            </td>

                            <td className="px-5 py-4">
                              {alternative.risk_level ? (
                                <span
                                  className={`inline-flex items-center gap-2 rounded-full border px-3 py-1 text-xs font-semibold ${getRiskClass(
                                    alternative.risk_level,
                                  )}`}
                                >
                                  <span
                                    className={`h-1.5 w-1.5 rounded-full ${getRiskDot(
                                      alternative.risk_level,
                                    )}`}
                                  />

                                  {
                                    alternative.risk_level
                                  }
                                </span>
                              ) : (
                                "—"
                              )}
                            </td>

                          </tr>
                        ),
                      )}

                    </tbody>
                  </table>

                </div>

                {/* MOBILE */}

                <div className="divide-y divide-slate-100 md:hidden">

                  {alternatives.map(
                    (alternative) => (
                      <div
                        key={alternative.id}
                        className="p-4"
                      >

                        <div className="flex items-start justify-between gap-3">

                          <div>
                            <p className="font-semibold text-slate-900">
                              {alternative.name}
                            </p>

                            <p className="mt-1 text-xs text-slate-400">
                              Alternative #
                              {alternative.id}
                            </p>
                          </div>

                          {alternative.risk_level && (
                            <span
                              className={`rounded-full border px-2.5 py-1 text-[11px] font-semibold ${getRiskClass(
                                alternative.risk_level,
                              )}`}
                            >
                              {alternative.risk_level}
                            </span>
                          )}

                        </div>

                        <div className="mt-4 grid grid-cols-2 gap-3">

                          <div className="rounded-xl bg-slate-50 p-3">
                            <p className="text-[11px] font-medium uppercase tracking-wide text-slate-400">
                              Cost
                            </p>

                            <p className="mt-1 text-sm font-bold text-slate-800">
                              {alternative.estimated_cost !==
                              undefined
                                ? alternative.estimated_cost.toLocaleString()
                                : "—"}
                            </p>
                          </div>

                          <div className="rounded-xl bg-slate-50 p-3">
                            <p className="text-[11px] font-medium uppercase tracking-wide text-slate-400">
                              Feasibility
                            </p>

                            <p
                              className={`mt-1 text-sm font-bold ${getFeasibilityClass(
                                alternative.feasibility_score,
                              )}`}
                            >
                              {alternative.feasibility_score !==
                              undefined
                                ? `${alternative.feasibility_score}/5`
                                : "—"}
                            </p>
                          </div>

                        </div>

                      </div>
                    ),
                  )}

                </div>
              </div>

              {/* RAW BACKEND RESPONSE */}

              <details className="group rounded-2xl border border-slate-200 bg-slate-50">

                <summary className="flex cursor-pointer list-none items-center justify-between px-5 py-4 text-sm font-semibold text-slate-700">
                  <span>
                    View backend comparison response
                  </span>

                  <span className="text-xs font-medium text-slate-400 group-open:hidden">
                    Expand
                  </span>

                  <span className="hidden text-xs font-medium text-slate-400 group-open:block">
                    Collapse
                  </span>
                </summary>

                <div className="border-t border-slate-200 p-5">

                  <pre className="max-h-[420px] overflow-auto rounded-xl bg-slate-900 p-5 text-xs leading-6 text-slate-200">
                    {JSON.stringify(
                      comparisonData,
                      null,
                      2,
                    )}
                  </pre>

                </div>

              </details>

            </div>
          </section>
        )}

      {/* =========================
          EMPTY STATE
      ========================= */}

      {!error &&
        alternatives.length === 0 && (
          <section className="overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-sm">

            <div className="px-6 py-16 text-center sm:px-8">

              <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-blue-50 text-blue-600">
                <GitCompare className="h-8 w-8" />
              </div>

              <h2 className="mt-6 text-xl font-bold text-slate-900">
                No alternatives yet
              </h2>

              <p className="mx-auto mt-2 max-w-lg text-sm leading-7 text-slate-500">
                Add possible solutions to this
                decision. Once you have at least
                two, you can compare them using
                cost, feasibility and risk.
              </p>

              <button
                type="button"
                onClick={openCreateForm}
                className="mt-7 inline-flex items-center gap-2 rounded-xl bg-blue-600 px-5 py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-blue-700"
              >
                <Plus className="h-4 w-4" />
                Add First Alternative
              </button>

            </div>

            <div className="grid border-t border-slate-100 sm:grid-cols-3">

              <div className="p-5 text-center sm:border-r sm:border-slate-100">
                <DollarSign className="mx-auto h-5 w-5 text-slate-400" />

                <p className="mt-2 text-xs font-semibold text-slate-500">
                  Cost
                </p>
              </div>

              <div className="border-t border-slate-100 p-5 text-center sm:border-r sm:border-t-0 sm:border-slate-100">
                <Gauge className="mx-auto h-5 w-5 text-slate-400" />

                <p className="mt-2 text-xs font-semibold text-slate-500">
                  Feasibility
                </p>
              </div>

              <div className="border-t border-slate-100 p-5 text-center sm:border-t-0">
                <ShieldAlert className="mx-auto h-5 w-5 text-slate-400" />

                <p className="mt-2 text-xs font-semibold text-slate-500">
                  Risk
                </p>
              </div>

            </div>

          </section>
        )}

      {/* =========================
          ALTERNATIVE LIST
      ========================= */}

      {alternatives.length > 0 && (
        <section>

          <div className="mb-5 flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">

            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-xl font-bold text-slate-900">
                  Available Alternatives
                </h2>

                <span className="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-bold text-slate-600">
                  {alternatives.length}
                </span>
              </div>

              <p className="mt-1 text-sm text-slate-500">
                Review each option before comparing
                or selecting a direction.
              </p>
            </div>

            {alternatives.length > 1 && (
              <button
                type="button"
                onClick={handleCompare}
                disabled={comparing}
                className="inline-flex w-fit items-center gap-2 rounded-xl border border-blue-200 bg-blue-50 px-4 py-2.5 text-sm font-semibold text-blue-700 transition hover:bg-blue-100 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {comparing ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <TrendingUp className="h-4 w-4" />
                )}

                Compare
              </button>
            )}

          </div>

          <div className="grid gap-5 lg:grid-cols-2">

            {alternatives.map(
              (alternative) => {
                const feasibility =
                  alternative.feasibility_score ??
                  0;

                return (
                  <article
                    key={alternative.id}
                    className="group overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-sm transition duration-200 hover:-translate-y-0.5 hover:border-blue-200 hover:shadow-lg"
                  >

                    {/* CARD TOP */}

                    <div className="border-b border-slate-100 p-6">

                      <div className="flex items-start justify-between gap-4">

                        <div className="flex min-w-0 items-start gap-3">

                          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-blue-50 text-blue-600">
                            <GitCompare className="h-5 w-5" />
                          </div>

                          <div className="min-w-0">

                            <h3 className="truncate text-lg font-bold text-slate-900">
                              {alternative.name}
                            </h3>

                            <p className="mt-1 text-xs font-medium text-slate-400">
                              Alternative #
                              {alternative.id}
                            </p>

                          </div>

                        </div>

                        {alternative.risk_level && (
                          <span
                            className={`inline-flex shrink-0 items-center gap-1.5 rounded-full border px-3 py-1.5 text-xs font-bold ${getRiskClass(
                              alternative.risk_level,
                            )}`}
                          >
                            <span
                              className={`h-1.5 w-1.5 rounded-full ${getRiskDot(
                                alternative.risk_level,
                              )}`}
                            />

                            {alternative.risk_level}
                          </span>
                        )}

                      </div>

                      <p className="mt-5 text-sm leading-7 text-slate-600">
                        {alternative.description ||
                          "No description provided."}
                      </p>

                    </div>

                    {/* METRICS */}

                    <div className="grid border-b border-slate-100 sm:grid-cols-3">

                      {/* COST */}

                      <div className="p-5 sm:border-r sm:border-slate-100">

                        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-slate-50 text-slate-500">
                          <DollarSign className="h-4 w-4" />
                        </div>

                        <p className="mt-3 text-xs font-medium text-slate-400">
                          Estimated Cost
                        </p>

                        <p className="mt-1 text-base font-bold text-slate-800">
                          {alternative.estimated_cost !==
                          undefined
                            ? alternative.estimated_cost.toLocaleString()
                            : "—"}
                        </p>

                      </div>

                      {/* FEASIBILITY */}

                      <div className="border-t border-slate-100 p-5 sm:border-r sm:border-t-0 sm:border-slate-100">

                        <div className="flex items-center justify-between">

                          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-slate-50 text-slate-500">
                            <Gauge className="h-4 w-4" />
                          </div>

                          <span
                            className={`text-xs font-bold ${getFeasibilityClass(
                              alternative.feasibility_score,
                            )}`}
                          >
                            {getFeasibilityLabel(
                              alternative.feasibility_score,
                            )}
                          </span>

                        </div>

                        <p className="mt-3 text-xs font-medium text-slate-400">
                          Feasibility
                        </p>

                        <div className="mt-2 flex items-center gap-2">

                          <div className="h-2 flex-1 overflow-hidden rounded-full bg-slate-100">
                            <div
                              className="h-full rounded-full bg-blue-600 transition-all"
                              style={{
                                width: `${
                                  (feasibility /
                                    5) *
                                  100
                                }%`,
                              }}
                            />
                          </div>

                          <span
                            className={`text-sm font-bold ${getFeasibilityClass(
                              alternative.feasibility_score,
                            )}`}
                          >
                            {alternative.feasibility_score !==
                            undefined
                              ? `${alternative.feasibility_score}/5`
                              : "—"}
                          </span>

                        </div>

                      </div>

                      {/* RISK */}

                      <div className="border-t border-slate-100 p-5 sm:border-t-0">

                        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-slate-50 text-slate-500">
                          <ShieldAlert className="h-4 w-4" />
                        </div>

                        <p className="mt-3 text-xs font-medium text-slate-400">
                          Risk Level
                        </p>

                        <p className="mt-1 text-base font-bold text-slate-800">
                          {alternative.risk_level ||
                            "—"}
                        </p>

                      </div>

                    </div>

                    {/* FOOTER */}

                    <div className="flex flex-col gap-4 p-5 sm:flex-row sm:items-center sm:justify-between">

                      <div className="inline-flex items-center gap-2 text-xs font-semibold text-emerald-600">
                        <CheckCircle2 className="h-4 w-4" />
                        Included in analysis
                      </div>

                      <div className="flex items-center gap-2">

                        <button
                          type="button"
                          onClick={() =>
                            startEditing(
                              alternative,
                            )
                          }
                          disabled={
                            deletingId ===
                            alternative.id
                          }
                          className="inline-flex items-center gap-2 rounded-xl border border-blue-200 bg-blue-50 px-3.5 py-2.5 text-xs font-bold text-blue-700 transition hover:bg-blue-100 disabled:cursor-not-allowed disabled:opacity-50"
                        >
                          <Edit3 className="h-4 w-4" />
                          Edit
                        </button>

                        <button
                          type="button"
                          onClick={() =>
                            handleDelete(
                              alternative,
                            )
                          }
                          disabled={
                            deletingId ===
                            alternative.id
                          }
                          className="inline-flex items-center gap-2 rounded-xl border border-red-200 bg-red-50 px-3.5 py-2.5 text-xs font-bold text-red-700 transition hover:bg-red-100 disabled:cursor-not-allowed disabled:opacity-50"
                        >
                          {deletingId ===
                          alternative.id ? (
                            <Loader2 className="h-4 w-4 animate-spin" />
                          ) : (
                            <Trash2 className="h-4 w-4" />
                          )}

                          {deletingId ===
                          alternative.id
                            ? "Deleting..."
                            : "Delete"}
                        </button>

                      </div>

                    </div>

                  </article>
                );
              },
            )}

          </div>
        </section>
      )}

    </div>
  );
}