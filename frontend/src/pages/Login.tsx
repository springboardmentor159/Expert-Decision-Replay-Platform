import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import api from "../services/api";
import { useAuth } from "../context/AuthContext";

export default function Login() {
  const navigate = useNavigate();
  const { login } = useAuth();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();

    setError("");

    if (!email || !password) {
      setError("Please enter your email and password.");
      return;
    }

    try {
      setLoading(true);

      // Backend expects JSON: { email, password }
      const response = await api.post("/auth/login", {
        email,
        password,
      });

      const token = response.data.access_token;
      const user = response.data.user;

      if (!token) {
        throw new Error("Login token was not returned by the server.");
      }

      if (!user) {
        throw new Error("User information was not returned by the server.");
      }

      // Store JWT and logged-in user information
      login(token, user);

      // Redirect to dashboard
      navigate("/dashboard");
    } catch (err: any) {
      const message =
        err.response?.data?.detail ||
        err.message ||
        "Login failed. Please check your credentials.";

      setError(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-950 px-4">
      <div className="w-full max-w-md">

        {/* Logo / Header */}
        <div className="mb-8 text-center">
          <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-blue-600 text-xl font-bold text-white shadow-lg">
            ED
          </div>

          <h1 className="text-3xl font-bold text-white">
            Expert Decision Replay
          </h1>

          <p className="mt-2 text-sm text-slate-400">
            Sign in to continue to your workspace
          </p>
        </div>

        {/* Login Card */}
        <div className="rounded-2xl border border-slate-800 bg-slate-900 p-8 shadow-2xl">
          <form onSubmit={handleSubmit} className="space-y-5">

            {/* Email */}
            <div>
              <label
                htmlFor="email"
                className="mb-2 block text-sm font-medium text-slate-300"
              >
                Email
              </label>

              <input
                id="email"
                type="email"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                placeholder="you@example.com"
                autoComplete="email"
                className="w-full rounded-xl border border-slate-700 bg-slate-800 px-4 py-3 text-white outline-none transition placeholder:text-slate-500 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20"
              />
            </div>

            {/* Password */}
            <div>
              <label
                htmlFor="password"
                className="mb-2 block text-sm font-medium text-slate-300"
              >
                Password
              </label>

              <input
                id="password"
                type="password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                placeholder="Enter your password"
                autoComplete="current-password"
                className="w-full rounded-xl border border-slate-700 bg-slate-800 px-4 py-3 text-white outline-none transition placeholder:text-slate-500 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20"
              />
            </div>

            {/* Error */}
            {error && (
              <div className="rounded-xl border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-300">
                {error}
              </div>
            )}

            {/* Submit */}
            <button
              type="submit"
              disabled={loading}
              className="w-full rounded-xl bg-blue-600 px-4 py-3 font-semibold text-white transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {loading ? "Signing in..." : "Sign in"}
            </button>
          </form>

          {/* Register */}
          <div className="mt-6 border-t border-slate-800 pt-6 text-center">
            <p className="text-sm text-slate-400">
              Don't have an account?{" "}
              <Link
                to="/register"
                className="font-medium text-blue-400 hover:text-blue-300"
              >
                Create account
              </Link>
            </p>
          </div>
        </div>

        <p className="mt-6 text-center text-xs text-slate-500">
          Expert Decision Replay Platform
        </p>
      </div>
    </div>
  );
}