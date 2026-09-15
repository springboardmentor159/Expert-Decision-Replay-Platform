import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    if (!username.trim() || !password.trim()) {
      setError("Please enter username and password.");
      return;
    }

    try {
      setLoading(true);

      const result = await login(username, password);

      console.log("LOGIN SUCCESS:", result);

      navigate("/dashboard");
    } catch (err) {
      if (err.response?.status === 401) {
        setError("Invalid username or password.");
      } else if (err.response?.status === 422) {
        setError("Please enter valid login details.");
      } else if (err.response?.status >= 500) {
        setError("Server error. Please try again later.");
      } else {
        setError("Login failed. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-brand-panel">
        <div className="auth-brand-content">
          <div className="auth-logo">ED</div>

          <h1>Expert Decision</h1>
          <h1>Replay Platform</h1>

          <p>
            A centralized platform for capturing, reviewing and replaying
            expert decisions with confidence.
          </p>

          <div className="auth-feature-list">
            <div>
              <span>✓</span>
              Decision management
            </div>

            <div>
              <span>✓</span>
              Expert review workflows
            </div>

            <div>
              <span>✓</span>
              Complete decision history
            </div>

            <div>
              <span>✓</span>
              Audit and reporting
            </div>
          </div>
        </div>

        <div className="auth-brand-footer">
          Expert Decision Replay Platform
        </div>
      </div>

      <div className="auth-form-panel">
        <div className="auth-form-container">
          <div className="mobile-auth-logo">ED</div>

          <div className="auth-form-header">
            <span className="auth-eyebrow">SECURE ACCESS</span>
            <h2>Welcome back</h2>
            <p>
              Sign in to access your decision management workspace.
            </p>
          </div>

          <form className="auth-form" onSubmit={handleSubmit}>
            <div className="auth-field">
              <label htmlFor="username">Username</label>

              <input
                id="username"
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Enter your username"
                autoComplete="username"
              />
            </div>

            <div className="auth-field">
              <div className="auth-label-row">
                <label htmlFor="password">Password</label>
              </div>

              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter your password"
                autoComplete="current-password"
              />
            </div>

            {error && (
              <div className="auth-error">
                <span>!</span>
                <p>{error}</p>
              </div>
            )}

            <button
              className="auth-submit-button"
              type="submit"
              disabled={loading}
            >
              {loading ? (
                <>
                  <span className="auth-button-spinner"></span>
                  Logging in...
                </>
              ) : (
                "Sign In"
              )}
            </button>
          </form>

          <div className="auth-divider">
            <span>OR</span>
          </div>

          <div className="auth-register-prompt">
            <span>Don't have an account?</span>
            <Link to="/register">Create an account</Link>
          </div>

          <div className="auth-security-note">
            <span>🔒</span>
            <p>Your session is protected using secure authentication.</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Login;