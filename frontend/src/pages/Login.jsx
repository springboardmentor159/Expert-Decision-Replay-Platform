import { useContext, useEffect, useState } from "react";
import {
  Link,
  useLocation,
  useNavigate,
} from "react-router-dom";

import {
  AuthContext,
} from "../context/AuthContext";

import {
  ArrowRight,
  LockKeyhole,
  LogIn,
  Mail,
  ShieldCheck,
  UserPlus,
} from "lucide-react";


function Login() {
  const navigate = useNavigate();
  const location = useLocation();

  const {
    login,
    user,
    loading,
  } = useContext(AuthContext);

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [error, setError] = useState("");
  const [submitting, setSubmitting] =
    useState(false);


  useEffect(() => {
    if (!loading && user) {
      navigate("/dashboard", {
        replace: true,
      });
    }
  }, [
    user,
    loading,
    navigate,
  ]);


  const getLoginErrorMessage = (
    requestError
  ) => {
    const status =
      requestError?.response?.status;

    const detail =
      requestError?.response?.data?.detail;

    if (
      status === 400 ||
      status === 401
    ) {
      return (
        detail ||
        "Invalid email or password."
      );
    }

    if (status === 403) {
      return (
        detail ||
        "You do not have permission to log in."
      );
    }

    if (status === 404) {
      return (
        detail ||
        "The login service could not be found."
      );
    }

    if (status === 422) {
      return (
        detail ||
        "Please enter a valid email and password."
      );
    }

    if (status >= 500) {
      return (
        "The server is currently unavailable. " +
        "Please try again later."
      );
    }

    if (requestError?.message) {
      return requestError.message;
    }

    return (
      "Unable to log in. Please try again."
    );
  };


  const handleSubmit = async (event) => {
    event.preventDefault();

    setError("");

    const trimmedEmail =
      email.trim();

    if (!trimmedEmail) {
      setError(
        "Please enter your email address."
      );
      return;
    }

    const emailPattern =
      /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (!emailPattern.test(trimmedEmail)) {
      setError(
        "Please enter a valid email address."
      );
      return;
    }

    if (!password) {
      setError(
        "Please enter your password."
      );
      return;
    }

    setSubmitting(true);

    try {
      await login(
        trimmedEmail,
        password
      );

      const destination =
        location.state?.from?.pathname ||
        "/dashboard";

      navigate(destination, {
        replace: true,
      });

    } catch (requestError) {
      console.error(
        "Login failed:",
        requestError
      );

      setError(
        getLoginErrorMessage(
          requestError
        )
      );

    } finally {
      setSubmitting(false);
    }
  };


  if (loading) {
    return (
      <div className="login-page">

        <div className="login-loading-card">

          <div className="login-logo">
            <ShieldCheck size={26} />
          </div>

          <div className="login-spinner" />

          <h2>
            Checking your session
          </h2>

          <p>
            Please wait while we verify
            your authentication.
          </p>

        </div>

        <style>{`
          .login-page {
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 25px;
            background:
              radial-gradient(
                circle at top left,
                #e0ecff 0,
                transparent 34%
              ),
              #f8fafc;
          }

          .login-loading-card {
            width: 100%;
            max-width: 420px;
            padding: 42px 32px;
            border: 1px solid #e2e8f0;
            border-radius: 20px;
            background: #fff;
            box-shadow:
              0 18px 50px
              rgba(15, 23, 42, .08);
            text-align: center;
          }

          .login-logo {
            width: 54px;
            height: 54px;
            margin: 0 auto 22px;
            border-radius: 15px;
            background: #dbeafe;
            color: #2563eb;
            display: flex;
            align-items: center;
            justify-content: center;
          }

          .login-loading-card h2 {
            margin: 0 0 7px;
            color: #0f172a;
            font-size: 19px;
          }

          .login-loading-card p {
            margin: 0;
            color: #64748b;
            font-size: 13px;
          }

          .login-spinner {
            width: 24px;
            height: 24px;
            margin: 0 auto 17px;
            border: 3px solid #dbeafe;
            border-top-color: #2563eb;
            border-radius: 50%;
            animation:
              loginSpin .8s linear infinite;
          }

          @keyframes loginSpin {
            to {
              transform: rotate(360deg);
            }
          }
        `}</style>

      </div>
    );
  }


  return (
    <div className="login-page">

      <style>{`
        .login-page {
          min-height: 100vh;
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 30px 20px;
          background:
            radial-gradient(
              circle at 10% 10%,
              #dbeafe 0,
              transparent 30%
            ),
            radial-gradient(
              circle at 90% 90%,
              #e0e7ff 0,
              transparent 28%
            ),
            #f8fafc;
        }

        .login-layout {
          width: 100%;
          max-width: 980px;
          display: grid;
          grid-template-columns: 1.05fr .95fr;
          overflow: hidden;
          border: 1px solid #e2e8f0;
          border-radius: 22px;
          background: #fff;
          box-shadow:
            0 25px 70px
            rgba(15, 23, 42, .10);
        }

        .login-brand-panel {
          position: relative;
          padding: 48px;
          background: #0f172a;
          color: #fff;
          overflow: hidden;
        }

        .login-brand-panel::before {
          content: "";
          position: absolute;
          width: 280px;
          height: 280px;
          right: -100px;
          top: -100px;
          border-radius: 50%;
          background: rgba(59, 130, 246, .18);
        }

        .login-brand-panel::after {
          content: "";
          position: absolute;
          width: 220px;
          height: 220px;
          left: -100px;
          bottom: -100px;
          border-radius: 50%;
          background: rgba(99, 102, 241, .13);
        }

        .login-brand-content {
          position: relative;
          z-index: 1;
          height: 100%;
          display: flex;
          flex-direction: column;
          justify-content: space-between;
        }

        .login-brand-icon {
          width: 58px;
          height: 58px;
          margin-bottom: 25px;
          border-radius: 16px;
          background: rgba(255,255,255,.1);
          border: 1px solid rgba(255,255,255,.14);
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .login-brand-eyebrow {
          margin-bottom: 10px;
          color: #93c5fd;
          font-size: 11px;
          font-weight: 800;
          letter-spacing: .12em;
          text-transform: uppercase;
        }

        .login-brand-panel h1 {
          max-width: 430px;
          margin: 0;
          font-size: 34px;
          line-height: 1.15;
          letter-spacing: -.02em;
        }

        .login-brand-description {
          max-width: 420px;
          margin: 17px 0 0;
          color: #cbd5e1;
          font-size: 14px;
          line-height: 1.7;
        }

        .login-feature-list {
          display: grid;
          gap: 12px;
          margin-top: 38px;
        }

        .login-feature {
          display: flex;
          align-items: center;
          gap: 10px;
          color: #e2e8f0;
          font-size: 12px;
        }

        .login-feature-icon {
          width: 27px;
          height: 27px;
          border-radius: 8px;
          background: rgba(59,130,246,.16);
          color: #93c5fd;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .login-form-panel {
          padding: 48px 45px;
          background: #fff;
        }

        .login-form-header {
          margin-bottom: 27px;
        }

        .login-form-header h2 {
          margin: 0;
          color: #0f172a;
          font-size: 25px;
        }

        .login-form-header p {
          margin: 7px 0 0;
          color: #64748b;
          font-size: 13px;
          line-height: 1.5;
        }

        .login-error {
          display: flex;
          align-items: flex-start;
          gap: 10px;
          margin-bottom: 19px;
          padding: 12px 13px;
          border: 1px solid #fecaca;
          border-radius: 9px;
          background: #fef2f2;
          color: #991b1b;
        }

        .login-error strong {
          display: block;
          margin-bottom: 3px;
          font-size: 12px;
        }

        .login-error p {
          margin: 0;
          font-size: 11px;
          line-height: 1.45;
        }

        .login-field {
          margin-bottom: 18px;
        }

        .login-field label {
          display: block;
          margin-bottom: 7px;
          color: #334155;
          font-size: 12px;
          font-weight: 750;
        }

        .login-input-wrapper {
          position: relative;
        }

        .login-input-icon {
          position: absolute;
          left: 13px;
          top: 50%;
          transform: translateY(-50%);
          color: #94a3b8;
          pointer-events: none;
        }

        .login-input {
          width: 100%;
          box-sizing: border-box;
          min-height: 45px;
          padding: 0 13px 0 41px;
          border: 1px solid #cbd5e1;
          border-radius: 9px;
          outline: none;
          background: #fff;
          color: #0f172a;
          font-family: inherit;
          font-size: 13px;
          transition: .15s ease;
        }

        .login-input::placeholder {
          color: #94a3b8;
        }

        .login-input:focus {
          border-color: #2563eb;
          box-shadow:
            0 0 0 3px
            rgba(37,99,235,.10);
        }

        .login-input:disabled {
          background: #f8fafc;
          cursor: not-allowed;
        }

        .login-submit {
          width: 100%;
          min-height: 46px;
          margin-top: 7px;
          border: none;
          border-radius: 9px;
          background: #2563eb;
          color: #fff;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 8px;
          font-family: inherit;
          font-size: 13px;
          font-weight: 750;
          cursor: pointer;
          transition: .15s ease;
        }

        .login-submit:hover:not(:disabled) {
          background: #1d4ed8;
          box-shadow:
            0 7px 18px
            rgba(37,99,235,.20);
        }

        .login-submit:disabled {
          opacity: .65;
          cursor: not-allowed;
        }

        .login-submit-spinner {
          width: 15px;
          height: 15px;
          border: 2px solid rgba(255,255,255,.35);
          border-top-color: #fff;
          border-radius: 50%;
          animation:
            loginSpin .7s linear infinite;
        }

        .login-divider {
          display: flex;
          align-items: center;
          gap: 10px;
          margin: 25px 0 20px;
          color: #94a3b8;
          font-size: 10px;
          text-transform: uppercase;
          letter-spacing: .08em;
          font-weight: 700;
        }

        .login-divider::before,
        .login-divider::after {
          content: "";
          height: 1px;
          flex: 1;
          background: #e2e8f0;
        }

        .login-register {
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 12px;
          padding: 13px;
          border: 1px solid #e2e8f0;
          border-radius: 10px;
          background: #f8fafc;
        }

        .login-register-text {
          display: flex;
          flex-direction: column;
          gap: 2px;
        }

        .login-register-text strong {
          color: #334155;
          font-size: 11px;
        }

        .login-register-text span {
          color: #94a3b8;
          font-size: 10px;
        }

        .login-register-link {
          min-height: 34px;
          padding: 0 11px;
          border: 1px solid #cbd5e1;
          border-radius: 7px;
          background: #fff;
          color: #2563eb;
          display: inline-flex;
          align-items: center;
          gap: 5px;
          text-decoration: none;
          font-size: 11px;
          font-weight: 750;
          white-space: nowrap;
        }

        .login-register-link:hover {
          background: #eff6ff;
          border-color: #93c5fd;
        }

        .login-security-note {
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 5px;
          margin-top: 19px;
          color: #94a3b8;
          font-size: 10px;
        }

        @media (max-width: 800px) {
          .login-layout {
            grid-template-columns: 1fr;
            max-width: 500px;
          }

          .login-brand-panel {
            padding: 32px;
          }

          .login-brand-panel h1 {
            font-size: 27px;
          }

          .login-feature-list {
            display: none;
          }

          .login-form-panel {
            padding: 35px 30px;
          }
        }

        @media (max-width: 500px) {
          .login-page {
            padding: 15px;
          }

          .login-brand-panel {
            padding: 27px;
          }

          .login-form-panel {
            padding: 30px 23px;
          }

          .login-register {
            align-items: flex-start;
            flex-direction: column;
          }

          .login-register-link {
            width: 100%;
            justify-content: center;
          }
        }
      `}</style>


      <div className="login-layout">

        {/* BRAND PANEL */}
        <div className="login-brand-panel">

          <div className="login-brand-content">

            <div>

              <div className="login-brand-icon">
                <ShieldCheck size={29} />
              </div>

              <div className="login-brand-eyebrow">
                Decision Management Platform
              </div>

              <h1>
                Expert Decision
                <br />
                Replay Platform
              </h1>

              <p className="login-brand-description">
                Make structured decisions,
                compare alternatives,
                collaborate with experts,
                and preserve the complete
                history of how decisions were made.
              </p>

              <div className="login-feature-list">

                <div className="login-feature">
                  <div className="login-feature-icon">
                    <ShieldCheck size={14} />
                  </div>

                  Secure role-based access
                </div>

                <div className="login-feature">
                  <div className="login-feature-icon">
                    <LogIn size={14} />
                  </div>

                  Decision review and approval
                </div>

                <div className="login-feature">
                  <div className="login-feature-icon">
                    <ArrowRight size={14} />
                  </div>

                  Complete decision history
                </div>

              </div>

            </div>

          </div>

        </div>


        {/* LOGIN FORM */}
        <div className="login-form-panel">

          <div className="login-form-header">

            <h2>
              Welcome back
            </h2>

            <p>
              Sign in to continue to your
              decision management workspace.
            </p>

          </div>


          {error && (
            <div className="login-error">

              <ShieldCheck size={17} />

              <div>
                <strong>
                  Login failed
                </strong>

                <p>
                  {error}
                </p>
              </div>

            </div>
          )}


          <form
            onSubmit={handleSubmit}
          >

            {/* EMAIL */}
            <div className="login-field">

              <label htmlFor="login-email">
                Email Address
              </label>

              <div className="login-input-wrapper">

                <Mail
                  size={16}
                  className="login-input-icon"
                />

                <input
                  id="login-email"
                  type="email"
                  className="login-input"
                  value={email}
                  onChange={(event) =>
                    setEmail(
                      event.target.value
                    )
                  }
                  placeholder="Enter your email"
                  autoComplete="email"
                  disabled={submitting}
                  required
                />

              </div>

            </div>


            {/* PASSWORD */}
            <div className="login-field">

              <label htmlFor="login-password">
                Password
              </label>

              <div className="login-input-wrapper">

                <LockKeyhole
                  size={16}
                  className="login-input-icon"
                />

                <input
                  id="login-password"
                  type="password"
                  className="login-input"
                  value={password}
                  onChange={(event) =>
                    setPassword(
                      event.target.value
                    )
                  }
                  placeholder="Enter your password"
                  autoComplete="current-password"
                  disabled={submitting}
                  required
                />

              </div>

            </div>


            {/* SUBMIT */}
            <button
              type="submit"
              className="login-submit"
              disabled={submitting}
            >

              {submitting ? (
                <>
                  <span className="login-submit-spinner" />
                  Signing in...
                </>
              ) : (
                <>
                  <LogIn size={16} />
                  Sign In
                  <ArrowRight size={15} />
                </>
              )}

            </button>

          </form>


          <div className="login-divider">
            New to the platform?
          </div>


          {/* REGISTER */}
          <div className="login-register">

            <div className="login-register-text">

              <strong>
                Create your account
              </strong>

              <span>
                Get started with Expert Decision Replay.
              </span>

            </div>

            <Link
              to="/register"
              className="login-register-link"
            >
              <UserPlus size={13} />
              Create Account
            </Link>

          </div>


          <div className="login-security-note">
            <LockKeyhole size={11} />
            Secure authentication enabled
          </div>

        </div>

      </div>

    </div>
  );
}


export default Login;