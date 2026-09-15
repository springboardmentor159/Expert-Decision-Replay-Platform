import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import api from "../services/api";

export default function Register() {
  const navigate = useNavigate();

  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [employeeId, setEmployeeId] = useState("");
  const [department, setDepartment] = useState("");
  const [designation, setDesignation] = useState("");
  const [phoneNumber, setPhoneNumber] = useState("");

  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();

    setError("");
    setSuccess("");

    const trimmedFullName = fullName.trim();
    const trimmedEmail = email.trim();

    if (!trimmedFullName || !trimmedEmail || !password) {
      setError("Please fill in all required fields.");
      return;
    }

    if (password.length < 6) {
      setError("Password must be at least 6 characters.");
      return;
    }

    try {
      setLoading(true);

      await api.post("/auth/register", {
        full_name: trimmedFullName,
        email: trimmedEmail,
        password,
        employee_id: employeeId.trim() || null,
        department: department.trim() || null,
        designation: designation.trim() || null,
        phone_number: phoneNumber.trim() || null,
      });

      setSuccess(
        "Registration successful. Redirecting to login...",
      );

      setTimeout(() => {
        navigate("/login");
      }, 1200);
    } catch (err: any) {
      setError(
        err.response?.data?.detail ||
          "Registration failed. Please try again.",
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 px-4 py-10">
      <div className="mx-auto w-full max-w-lg">

        {/* Header */}
        <div className="mb-8 text-center">
          <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-blue-600 text-xl font-bold text-white shadow-lg">
            ED
          </div>

          <h1 className="text-3xl font-bold text-white">
            Create your account
          </h1>

          <p className="mt-2 text-sm text-slate-400">
            Join the Expert Decision Replay Platform
          </p>
        </div>

        {/* Registration Card */}
        <div className="rounded-2xl border border-slate-800 bg-slate-900 p-8 shadow-2xl">

          <form onSubmit={handleSubmit} className="space-y-5">

            {/* Full Name */}
            <div>
              <label className="mb-2 block text-sm font-medium text-slate-300">
                Full Name *
              </label>

              <input
                type="text"
                value={fullName}
                onChange={(event) =>
                  setFullName(event.target.value)
                }
                placeholder="Enter your full name"
                autoComplete="name"
                className="w-full rounded-xl border border-slate-700 bg-slate-800 px-4 py-3 text-white outline-none transition placeholder:text-slate-500 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20"
              />
            </div>

            {/* Email */}
            <div>
              <label className="mb-2 block text-sm font-medium text-slate-300">
                Email *
              </label>

              <input
                type="email"
                value={email}
                onChange={(event) =>
                  setEmail(event.target.value)
                }
                placeholder="you@example.com"
                autoComplete="email"
                className="w-full rounded-xl border border-slate-700 bg-slate-800 px-4 py-3 text-white outline-none transition placeholder:text-slate-500 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20"
              />
            </div>

            {/* Password */}
            <div>
              <label className="mb-2 block text-sm font-medium text-slate-300">
                Password *
              </label>

              <input
                type="password"
                value={password}
                onChange={(event) =>
                  setPassword(event.target.value)
                }
                placeholder="Minimum 6 characters"
                autoComplete="new-password"
                className="w-full rounded-xl border border-slate-700 bg-slate-800 px-4 py-3 text-white outline-none transition placeholder:text-slate-500 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20"
              />

              <p className="mt-1.5 text-xs text-slate-500">
                Use at least 6 characters.
              </p>
            </div>

            {/* Account Role Notice */}
            <div className="rounded-xl border border-blue-500/20 bg-blue-500/10 px-4 py-3">
              <p className="text-sm font-medium text-blue-300">
                Employee account
              </p>

              <p className="mt-1 text-xs leading-5 text-blue-200/70">
                New accounts are registered as Employee accounts.
                Reviewer, Manager, and Administrator roles are
                assigned by an authorized administrator.
              </p>
            </div>

            {/* Employee ID */}
            <div>
              <label className="mb-2 block text-sm font-medium text-slate-300">
                Employee ID
              </label>

              <input
                type="text"
                value={employeeId}
                onChange={(event) =>
                  setEmployeeId(event.target.value)
                }
                placeholder="Optional"
                autoComplete="off"
                className="w-full rounded-xl border border-slate-700 bg-slate-800 px-4 py-3 text-white outline-none transition placeholder:text-slate-500 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20"
              />
            </div>

            {/* Department */}
            <div>
              <label className="mb-2 block text-sm font-medium text-slate-300">
                Department
              </label>

              <input
                type="text"
                value={department}
                onChange={(event) =>
                  setDepartment(event.target.value)
                }
                placeholder="Optional"
                autoComplete="organization"
                className="w-full rounded-xl border border-slate-700 bg-slate-800 px-4 py-3 text-white outline-none transition placeholder:text-slate-500 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20"
              />
            </div>

            {/* Designation */}
            <div>
              <label className="mb-2 block text-sm font-medium text-slate-300">
                Designation
              </label>

              <input
                type="text"
                value={designation}
                onChange={(event) =>
                  setDesignation(event.target.value)
                }
                placeholder="Optional"
                className="w-full rounded-xl border border-slate-700 bg-slate-800 px-4 py-3 text-white outline-none transition placeholder:text-slate-500 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20"
              />
            </div>

            {/* Phone */}
            <div>
              <label className="mb-2 block text-sm font-medium text-slate-300">
                Phone Number
              </label>

              <input
                type="tel"
                value={phoneNumber}
                onChange={(event) =>
                  setPhoneNumber(event.target.value)
                }
                placeholder="Optional"
                autoComplete="tel"
                className="w-full rounded-xl border border-slate-700 bg-slate-800 px-4 py-3 text-white outline-none transition placeholder:text-slate-500 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20"
              />
            </div>

            {/* Error */}
            {error && (
              <div
                role="alert"
                className="rounded-xl border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-300"
              >
                {error}
              </div>
            )}

            {/* Success */}
            {success && (
              <div
                role="status"
                className="rounded-xl border border-green-500/30 bg-green-500/10 px-4 py-3 text-sm text-green-300"
              >
                {success}
              </div>
            )}

            {/* Submit */}
            <button
              type="submit"
              disabled={loading}
              className="w-full rounded-xl bg-blue-600 px-4 py-3 font-semibold text-white shadow-lg shadow-blue-600/10 transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {loading
                ? "Creating account..."
                : "Create account"}
            </button>
          </form>

          {/* Login Link */}
          <div className="mt-6 border-t border-slate-800 pt-6 text-center">
            <p className="text-sm text-slate-400">
              Already have an account?{" "}
              <Link
                to="/login"
                className="font-medium text-blue-400 transition hover:text-blue-300"
              >
                Sign in
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}