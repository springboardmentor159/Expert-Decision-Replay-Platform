import { ShieldAlert, ArrowLeft } from "lucide-react";
import { useNavigate } from "react-router-dom";

export default function Forbidden() {
  const navigate = useNavigate();

  return (
    <div className="flex min-h-[70vh] items-center justify-center px-4">
      <div className="w-full max-w-lg text-center">

        {/* Icon */}
        <div className="mx-auto flex h-20 w-20 items-center justify-center rounded-2xl bg-red-50">
          <ShieldAlert
            size={42}
            className="text-red-500"
          />
        </div>

        {/* Title */}
        <h1 className="mt-6 text-3xl font-bold text-slate-900">
          Access Denied
        </h1>

        {/* Description */}
        <p className="mx-auto mt-3 max-w-md text-sm leading-6 text-slate-500">
          You do not have permission to access this page.
          Your account role does not provide the required
          authorization.
        </p>

        {/* Status */}
        <div className="mx-auto mt-6 inline-flex items-center rounded-full border border-red-200 bg-red-50 px-4 py-2 text-sm font-semibold text-red-700">
          HTTP 403 — Forbidden
        </div>

        {/* Button */}
        <div className="mt-8">
          <button
            type="button"
            onClick={() => navigate("/dashboard")}
            className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-5 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-blue-700"
          >
            <ArrowLeft size={17} />
            Back to Dashboard
          </button>
        </div>

      </div>
    </div>
  );
}