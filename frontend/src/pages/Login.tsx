import { useState, type FormEvent } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { Eye, EyeOff, Lock, Mail, LogIn } from "lucide-react";
import { useAuth } from "../context/useAuth";

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const from =
    (location.state as { from?: { pathname?: string } } | null)?.from
      ?.pathname || "/dashboard";

  const handleSubmit = async (
    event: FormEvent<HTMLFormElement>,
  ) => {
    event.preventDefault();
    setError("");

    const trimmedEmail = email.trim();

    if (!trimmedEmail) {
      setError("Please enter your email address.");
      return;
    }

    if (!password) {
      setError("Please enter your password.");
      return;
    }

    try {
      setIsSubmitting(true);

      await login(trimmedEmail, password);

      navigate(from, { replace: true });
    } catch (err: any) {
      console.error("Login error:", err);

      const status = err?.response?.status;

      if (status === 401) {
        setError("Invalid email or password.");
      } else if (status === 403) {
        setError("You do not have permission to log in.");
      } else if (status === 404) {
        setError("User account could not be found.");
      } else if (status === 422) {
        setError("Please check the entered information.");
      } else if (status >= 500) {
        setError("Server error. Please try again later.");
      } else if (err?.request) {
        setError(
          "Unable to connect to the server. Make sure the FastAPI backend is running.",
        );
      } else if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Login failed. Please try again.");
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <main className="auth-page">
      <section className="auth-card">
        <div className="auth-header">
          <div className="auth-logo">
            <LogIn size={24} />
          </div>

          <h1>Welcome Back</h1>

          <p>
            Sign in to the Expert Decision Replay Platform
          </p>
        </div>

        <form
          onSubmit={handleSubmit}
          className="auth-form"
        >
          <div className="form-group">
            <label htmlFor="email">
              Email Address
            </label>

            <div className="input-wrapper">
              <Mail size={18} />

              <input
                id="email"
                type="email"
                value={email}
                onChange={(event) =>
                  setEmail(event.target.value)
                }
                placeholder="Enter your email"
                autoComplete="email"
                disabled={isSubmitting}
              />
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="password">
              Password
            </label>

            <div className="input-wrapper">
              <Lock size={18} />

              <input
                id="password"
                type={
                  showPassword
                    ? "text"
                    : "password"
                }
                value={password}
                onChange={(event) =>
                  setPassword(event.target.value)
                }
                placeholder="Enter your password"
                autoComplete="current-password"
                disabled={isSubmitting}
              />

              <button
                type="button"
                className="password-toggle"
                onClick={() =>
                  setShowPassword(
                    (current) => !current,
                  )
                }
                aria-label={
                  showPassword
                    ? "Hide password"
                    : "Show password"
                }
                disabled={isSubmitting}
              >
                {showPassword ? (
                  <EyeOff size={18} />
                ) : (
                  <Eye size={18} />
                )}
              </button>
            </div>
          </div>

          {error && (
            <div
              className="auth-error"
              role="alert"
            >
              {error}
            </div>
          )}

          <button
            type="submit"
            className="auth-submit"
            disabled={isSubmitting}
          >
            {isSubmitting
              ? "Signing in..."
              : "Sign In"}
          </button>
        </form>

        <div className="auth-footer">
          <span>
            Don't have an account?
          </span>

          <Link to="/register">
            Create an account
          </Link>
        </div>
      </section>
    </main>
  );
}