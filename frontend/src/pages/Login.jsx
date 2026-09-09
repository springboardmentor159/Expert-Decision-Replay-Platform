import { useContext, useEffect, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";

import { AuthContext } from "../context/AuthContext";


function Login() {
  const navigate = useNavigate();
  const location = useLocation();

  const { login, user, loading } = useContext(AuthContext);

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);


  useEffect(() => {
    if (!loading && user) {
      navigate("/dashboard", {
        replace: true,
      });
    }
  }, [user, loading, navigate]);


  const getLoginErrorMessage = (requestError) => {
    const status = requestError?.response?.status;
    const detail = requestError?.response?.data?.detail;

    if (status === 400) {
      return (
        detail ||
        "Invalid email or password."
      );
    }

    if (status === 401) {
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

    return "Unable to log in. Please try again.";
  };


  const handleSubmit = async (event) => {
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
      <div className="auth-page">
        <div className="auth-card">
          <div className="loading-state">
            <p>Checking your session...</p>
          </div>
        </div>
      </div>
    );
  }


  return (
    <div className="auth-page">

      <div className="auth-card">

        <div className="auth-header">

          <h1>
            Expert Decision Replay
          </h1>

          <p>
            Sign in to continue to your
            decision management workspace.
          </p>

        </div>


        {error && (
          <div className="error-message">
            <strong>
              Login failed
            </strong>

            <p>
              {error}
            </p>
          </div>
        )}


        <form
          onSubmit={handleSubmit}
          className="auth-form"
        >

          <div className="form-group">

            <label htmlFor="login-email">
              Email Address
            </label>

            <input
              id="login-email"
              type="email"
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


          <div className="form-group">

            <label htmlFor="login-password">
              Password
            </label>

            <input
              id="login-password"
              type="password"
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


          <button
            type="submit"
            className="primary-button auth-submit-button"
            disabled={submitting}
          >
            {submitting
              ? "Signing in..."
              : "Sign In"}
          </button>

        </form>


        <div className="auth-footer">

          <p>
            Don't have an account?
          </p>

          <Link
            to="/register"
            className="secondary-button"
          >
            Create Account
          </Link>

        </div>

      </div>

    </div>
  );
}


export default Login;