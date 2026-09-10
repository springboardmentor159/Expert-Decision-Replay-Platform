import { useState, type FormEvent } from "react";
import {
  ArrowRight,
  Check,
  Eye,
  EyeOff,
  LockKeyhole,
  Mail,
  ShieldCheck,
} from "lucide-react";
import { Link, useLocation, useNavigate } from "react-router-dom";

import { useAuth } from "../auth/AuthContext";
import "./LoginPage.css";

interface LocationState {
  from?: {
    pathname?: string;
  };
}

export default function LoginPage() {
  const { login, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const locationState = location.state as LocationState | null;
  const redirectPath = locationState?.from?.pathname ?? "/dashboard";

  if (isAuthenticated) {
    navigate("/dashboard", { replace: true });
    return null;
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setErrorMessage("");

    const trimmedEmail = email.trim();

    if (!trimmedEmail || !password) {
      setErrorMessage("Please enter your email and password.");
      return;
    }

    setIsSubmitting(true);

    try {
      await login(trimmedEmail, password);
      navigate(redirectPath, { replace: true });
        } catch (error: unknown) {
      console.error("LOGIN ERROR:", error);

      const axiosError = error as {
        response?: {
          status?: number;
          data?: {
            detail?: string;
          };
        };
        message?: string;
      };

      const status = axiosError.response?.status;
      const detail = axiosError.response?.data?.detail;

      if (status === 401) {
        setErrorMessage("Invalid email or password.");
      } else if (status === 422) {
        setErrorMessage(
          detail || "Please enter a valid email address and password.",
        );
      } else if (detail) {
        setErrorMessage(detail);
      } else if (axiosError.message) {
        setErrorMessage(axiosError.message);
      } else {
        setErrorMessage(
          "Login failed. Check the browser console for the exact error.",
        );
      }
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className="login-page">
      <div
        className="login-background-orb login-background-orb-one"
        aria-hidden="true"
      />

      <div
        className="login-background-orb login-background-orb-two"
        aria-hidden="true"
      />

      <section className="login-shell">
        <aside className="login-brand-panel">
          <div className="brand-grid-pattern" aria-hidden="true" />

          <div className="login-brand-content">
            <div className="brand-top">
              <div className="brand-mark" aria-hidden="true">
                <span>ED</span>
              </div>

              <div>
                <p className="brand-product-name">
                  Expert Decision
                </p>

                <p className="brand-product-subtitle">
                  Replay Platform
                </p>
              </div>
            </div>

            <div className="brand-main">
              <p className="brand-overline">
                DECISION INTELLIGENCE PLATFORM
              </p>

              <h1>
                <span>Expert</span>
                <span>Decision</span>
                <span>Replay</span>
              </h1>

              <p className="brand-description">
                Capture the thinking behind important decisions.
                Preserve expert knowledge. Replay the reasoning when
                it matters most.
              </p>
            </div>

            <div className="brand-benefits">
              <div className="brand-benefit">
                <span className="benefit-icon" aria-hidden="true">
                  <Check size={15} strokeWidth={2.5} />
                </span>

                <div>
                  <strong>Capture expert decisions</strong>
                  <span>
                    Keep critical reasoning documented.
                  </span>
                </div>
              </div>

              <div className="brand-benefit">
                <span className="benefit-icon" aria-hidden="true">
                  <Check size={15} strokeWidth={2.5} />
                </span>

                <div>
                  <strong>Replay organizational knowledge</strong>
                  <span>
                    Learn from decisions that came before.
                  </span>
                </div>
              </div>

              <div className="brand-benefit">
                <span className="benefit-icon" aria-hidden="true">
                  <Check size={15} strokeWidth={2.5} />
                </span>

                <div>
                  <strong>Make decisions with confidence</strong>
                  <span>
                    Bring context into every new decision.
                  </span>
                </div>
              </div>
            </div>

            <div className="brand-footer">
              <div className="brand-footer-line" />

              <span>
                Built for teams that value better decisions.
              </span>
            </div>
          </div>
        </aside>

        <section className="login-form-panel">
          <div className="login-form-container">
            <div className="mobile-brand">
              <div
                className="brand-mark mobile-brand-mark"
                aria-hidden="true"
              >
                <span>ED</span>
              </div>

              <div>
                <strong>Expert Decision</strong>
                <span>Replay Platform</span>
              </div>
            </div>

            <div className="login-header">
              <p className="login-eyebrow">WELCOME BACK</p>

              <h2>Sign in to continue</h2>

              <p>
                Access your decision workspace and pick up where you
                left off.
              </p>
            </div>

            <form
              className="login-form"
              onSubmit={handleSubmit}
              noValidate
            >
              {errorMessage ? (
                <div
                  className="login-alert"
                  role="alert"
                  aria-live="assertive"
                >
                  <span
                    className="login-alert-icon"
                    aria-hidden="true"
                  >
                    !
                  </span>

                  <span>{errorMessage}</span>
                </div>
              ) : null}

              <div className="login-field">
                <label htmlFor="email">Email address</label>

                <div className="login-input-wrapper">
                  <Mail
                    className="login-input-icon"
                    size={18}
                    strokeWidth={1.9}
                    aria-hidden="true"
                  />

                  <input
                    id="email"
                    name="email"
                    type="email"
                    value={email}
                    onChange={(event) => {
                      setEmail(event.target.value);
                      setErrorMessage("");
                    }}
                    autoComplete="email"
                    placeholder="name@company.com"
                    disabled={isSubmitting}
                    required
                  />
                </div>
              </div>

              <div className="login-field">
                <label htmlFor="password">Password</label>

                <div className="login-input-wrapper">
                  <LockKeyhole
                    className="login-input-icon"
                    size={18}
                    strokeWidth={1.9}
                    aria-hidden="true"
                  />

                  <input
                    id="password"
                    name="password"
                    type={showPassword ? "text" : "password"}
                    value={password}
                    onChange={(event) => {
                      setPassword(event.target.value);
                      setErrorMessage("");
                    }}
                    autoComplete="current-password"
                    placeholder="Enter your password"
                    disabled={isSubmitting}
                    required
                  />

                  <button
                    type="button"
                    className="password-toggle"
                    onClick={() =>
                      setShowPassword((current) => !current)
                    }
                    disabled={isSubmitting}
                    aria-label={
                      showPassword
                        ? "Hide password"
                        : "Show password"
                    }
                    title={
                      showPassword
                        ? "Hide password"
                        : "Show password"
                    }
                  >
                    {showPassword ? (
                      <EyeOff size={18} strokeWidth={1.9} />
                    ) : (
                      <Eye size={18} strokeWidth={1.9} />
                    )}
                  </button>
                </div>
              </div>

              <button
                type="submit"
                className="login-submit"
                disabled={isSubmitting}
              >
                {isSubmitting ? (
                  <>
                    <span
                      className="login-spinner"
                      aria-hidden="true"
                    />
                    <span>Signing in...</span>
                  </>
                ) : (
                  <>
                    <span>Sign in</span>

                    <ArrowRight
                      size={17}
                      strokeWidth={2.2}
                      aria-hidden="true"
                    />
                  </>
                )}
              </button>
            </form>

            <div className="login-divider" aria-hidden="true">
              <span />
              <span>SECURE ACCESS</span>
              <span />
            </div>

            <div className="security-message">
              <ShieldCheck
                size={16}
                strokeWidth={1.8}
                aria-hidden="true"
              />

              <span>
                Your account is protected with secure token-based
                authentication.
              </span>
            </div>

            <p className="login-register">
              New to the platform?{" "}
              <Link to="/register">Create your account</Link>
            </p>

            <p className="login-copyright">
              Expert Decision Replay Platform
            </p>
          </div>
        </section>
      </section>
    </main>
  );
}