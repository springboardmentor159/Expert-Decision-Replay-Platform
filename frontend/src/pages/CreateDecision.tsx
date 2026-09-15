import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  AlertCircle,
  ArrowLeft,
  FileText,
  Info,
  Loader2,
} from "lucide-react";

import { createDecision } from "../services/decisions";

export default function CreateDecision() {
  const navigate = useNavigate();

  const [title, setTitle] = useState("");
  const [problemStatement, setProblemStatement] =
    useState("");
  const [category, setCategory] = useState("");
  const [rationale, setRationale] = useState("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (
    event: React.FormEvent,
  ) => {
    event.preventDefault();

    setError("");

    const trimmedTitle = title.trim();
    const trimmedProblem = problemStatement.trim();
    const trimmedCategory = category.trim();
    const trimmedRationale = rationale.trim();

    if (!trimmedTitle) {
      setError("Decision title is required.");
      return;
    }

    if (!trimmedProblem) {
      setError("Problem statement is required.");
      return;
    }

    if (!trimmedCategory) {
      setError("Category is required.");
      return;
    }

    try {
      setLoading(true);

      const decision = await createDecision({
        title: trimmedTitle,
        problem_statement: trimmedProblem,
        category: trimmedCategory,
        rationale:
          trimmedRationale || undefined,
      });

      navigate(`/decisions/${decision.id}`);
    } catch (err: any) {
      console.error(
        "Failed to create decision:",
        err,
      );

      setError(
        err?.response?.data?.detail ||
          "Unable to create decision. Please try again.",
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-7">

      {/* =====================================================
          BACK NAVIGATION
      ===================================================== */}

      <Link
        to="/decisions"
        className="inline-flex items-center gap-2 text-sm font-semibold text-slate-600 transition hover:text-blue-600"
      >
        <ArrowLeft className="h-4 w-4" />
        Back to Decisions
      </Link>

      {/* =====================================================
          HEADER
      ===================================================== */}

      <section className="relative overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-sm">

        <div className="absolute -right-12 -top-16 h-48 w-48 rounded-full bg-blue-50 blur-3xl" />

        <div className="relative p-6 sm:p-8">

          <div className="flex items-start gap-4">

            <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-blue-600 text-white shadow-sm">
              <FileText className="h-6 w-6" />
            </div>

            <div className="min-w-0">
              <p className="text-xs font-semibold uppercase tracking-[0.16em] text-blue-600">
                Decision Workspace
              </p>

              <h1 className="mt-1 text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl">
                Create Decision
              </h1>

              <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-500 sm:text-base">
                Capture the problem, category and reasoning
                behind a new organizational decision.
              </p>
            </div>

          </div>

        </div>
      </section>

      {/* =====================================================
          FORM
      ===================================================== */}

      <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_280px]">

        {/* Main form */}

        <section className="rounded-2xl border border-slate-200 bg-white shadow-sm">

          <div className="border-b border-slate-100 px-6 py-5">
            <h2 className="text-lg font-semibold text-slate-900">
              Decision Information
            </h2>

            <p className="mt-1 text-sm text-slate-500">
              Provide the information needed to begin the
              decision workflow.
            </p>
          </div>

          <form
            onSubmit={handleSubmit}
            className="p-6 sm:p-7"
          >

            <div className="space-y-6">

              {/* Title */}

              <div>
                <label
                  htmlFor="title"
                  className="mb-2 block text-sm font-semibold text-slate-700"
                >
                  Decision Title
                  <span className="ml-1 text-red-500">
                    *
                  </span>
                </label>

                <input
                  id="title"
                  type="text"
                  value={title}
                  onChange={(event) =>
                    setTitle(event.target.value)
                  }
                  placeholder="Enter a clear, concise decision title"
                  maxLength={200}
                  autoComplete="off"
                  className="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-blue-500 focus:bg-white focus:ring-2 focus:ring-blue-500/20"
                />

                <p className="mt-1.5 text-right text-xs text-slate-400">
                  {title.length}/200
                </p>
              </div>

              {/* Problem Statement */}

              <div>
                <label
                  htmlFor="problem"
                  className="mb-2 block text-sm font-semibold text-slate-700"
                >
                  Problem Statement
                  <span className="ml-1 text-red-500">
                    *
                  </span>
                </label>

                <textarea
                  id="problem"
                  value={problemStatement}
                  onChange={(event) =>
                    setProblemStatement(
                      event.target.value,
                    )
                  }
                  placeholder="Describe the problem, challenge or situation that requires a decision..."
                  rows={7}
                  maxLength={2000}
                  className="w-full resize-y rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm leading-6 text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-blue-500 focus:bg-white focus:ring-2 focus:ring-blue-500/20"
                />

                <p className="mt-1.5 text-right text-xs text-slate-400">
                  {problemStatement.length}/2000
                </p>
              </div>

              {/* Category */}

              <div>
                <label
                  htmlFor="category"
                  className="mb-2 block text-sm font-semibold text-slate-700"
                >
                  Category
                  <span className="ml-1 text-red-500">
                    *
                  </span>
                </label>

                <input
                  id="category"
                  type="text"
                  value={category}
                  onChange={(event) =>
                    setCategory(event.target.value)
                  }
                  placeholder="e.g. Technology, Operations, Finance"
                  maxLength={100}
                  autoComplete="off"
                  className="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-blue-500 focus:bg-white focus:ring-2 focus:ring-blue-500/20"
                />

                <p className="mt-1.5 text-xs text-slate-400">
                  Use a meaningful category to make decisions
                  easier to search and analyze.
                </p>
              </div>

              {/* Rationale */}

              <div>
                <div className="flex items-center justify-between gap-3">
                  <label
                    htmlFor="rationale"
                    className="text-sm font-semibold text-slate-700"
                  >
                    Rationale
                    <span className="ml-2 rounded-full bg-slate-100 px-2 py-0.5 text-[10px] font-medium uppercase tracking-wide text-slate-500">
                      Optional
                    </span>
                  </label>
                </div>

                <textarea
                  id="rationale"
                  value={rationale}
                  onChange={(event) =>
                    setRationale(
                      event.target.value,
                    )
                  }
                  placeholder="Explain the reasoning, assumptions or context behind this decision..."
                  rows={7}
                  maxLength={2000}
                  className="mt-2 w-full resize-y rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm leading-6 text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-blue-500 focus:bg-white focus:ring-2 focus:ring-blue-500/20"
                />

                <p className="mt-1.5 text-right text-xs text-slate-400">
                  {rationale.length}/2000
                </p>
              </div>

            </div>

            {/* Error */}

            {error && (
              <div
                role="alert"
                className="mt-6 rounded-xl border border-red-200 bg-red-50 p-4"
              >
                <div className="flex items-start gap-3">

                  <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-red-100">
                    <AlertCircle className="h-4 w-4 text-red-600" />
                  </div>

                  <div>
                    <p className="text-sm font-semibold text-red-800">
                      Unable to create decision
                    </p>

                    <p className="mt-1 text-sm leading-5 text-red-700">
                      {error}
                    </p>
                  </div>

                </div>
              </div>
            )}

            {/* Actions */}

            <div className="mt-7 flex flex-col-reverse gap-3 border-t border-slate-100 pt-6 sm:flex-row sm:justify-end">

              <button
                type="button"
                onClick={() =>
                  navigate("/decisions")
                }
                disabled={loading}
                className="rounded-xl border border-slate-200 bg-white px-5 py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-60"
              >
                Cancel
              </button>

              <button
                type="submit"
                disabled={loading}
                className="inline-flex items-center justify-center gap-2 rounded-xl bg-blue-600 px-6 py-3 text-sm font-semibold text-white shadow-sm shadow-blue-600/10 transition hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {loading ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" />
                    Creating decision...
                  </>
                ) : (
                  <>
                    <FileText className="h-4 w-4" />
                    Create Decision
                  </>
                )}
              </button>

            </div>

          </form>
        </section>

        {/* =================================================
            GUIDANCE PANEL
        ================================================= */}

        <aside className="h-fit rounded-2xl border border-slate-200 bg-white shadow-sm">

          <div className="border-b border-slate-100 px-5 py-4">
            <div className="flex items-center gap-2">
              <Info className="h-4 w-4 text-blue-600" />

              <h2 className="text-sm font-semibold text-slate-900">
                Before you create
              </h2>
            </div>
          </div>

          <div className="space-y-5 p-5">

            <div>
              <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">
                01
              </p>

              <p className="mt-1.5 text-sm font-semibold text-slate-800">
                State the problem clearly
              </p>

              <p className="mt-1 text-xs leading-5 text-slate-500">
                Describe what needs to be solved or decided
                and provide enough context for reviewers.
              </p>
            </div>

            <div>
              <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">
                02
              </p>

              <p className="mt-1.5 text-sm font-semibold text-slate-800">
                Choose a useful category
              </p>

              <p className="mt-1 text-xs leading-5 text-slate-500">
                Categories help organize decisions and make
                repository searches more effective.
              </p>
            </div>

            <div>
              <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">
                03
              </p>

              <p className="mt-1.5 text-sm font-semibold text-slate-800">
                Explain the reasoning
              </p>

              <p className="mt-1 text-xs leading-5 text-slate-500">
                Add assumptions, context or reasoning that
                will help reviewers understand the decision.
              </p>
            </div>

            <div className="rounded-xl bg-blue-50 p-4">
              <p className="text-xs font-semibold text-blue-800">
                Workflow
              </p>

              <p className="mt-1 text-xs leading-5 text-blue-700">
                New decisions begin as drafts. You can add
                alternatives and discussions before submitting
                the decision for review.
              </p>
            </div>

          </div>
        </aside>

      </div>
    </div>
  );
}