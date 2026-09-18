import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import api from "../services/api";
import { useAuth } from "../context/AuthContext";

import "./Login.css";

function Login() {
  const navigate = useNavigate();
  const { login } = useAuth();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();

    setMessage("");

    if (!email.trim() || !password.trim()) {
      setMessage("Please enter email and password.");
      return;
    }

    setLoading(true);

    try {
      const response = await api.post("/login", null, {
        params: {
          email: email.trim(),
          password: password,
        },
      });

      console.log("Login response:", response.data);

      const accessToken = response.data?.access_token;

      if (!accessToken) {
        setMessage("Login failed: access token not received.");
        return;
      }

      const userData =
        response.data?.user ||
        response.data?.data?.user || {
          email: email.trim(),
        };

      const loginSuccess = login(userData, accessToken);

      if (!loginSuccess) {
        setMessage("Login failed: authentication could not be saved.");
        return;
      }

      const savedToken = localStorage.getItem("token");

      console.log("Saved token:", savedToken);

      if (!savedToken) {
        setMessage("Login failed: token was not saved.");
        return;
      }

      setMessage("Login successful!");

      navigate("/dashboard", { replace: true });
    } catch (error) {
      console.error("Login error:", error);

      if (error.response) {
        const detail = error.response.data?.detail;

        if (Array.isArray(detail)) {
          setMessage(
            detail.map((item) => item.msg).join(", ")
          );
        } else {
          setMessage(detail || "Invalid email or password");
        }
      } else {
        setMessage("Unable to connect to backend");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-page">
      <div className="login-background-shape shape-one"></div>
      <div className="login-background-shape shape-two"></div>

      <div className="login-layout">
        <section className="login-intro">
          <div className="brand-mark">ED</div>

          <p className="intro-label">
            DECISION INTELLIGENCE PLATFORM
          </p>

          <h1>
            Every decision
            <span> has a story.</span>
          </h1>

          <p className="intro-description">
            Capture decisions, understand the reasoning, review approvals,
            and replay important outcomes from one secure workspace.
          </p>

          <div className="decision-flow">
            <div className="flow-item">
              <div className="flow-number">01</div>

              <div>
                <h3>Create</h3>
                <p>Record the decision</p>
              </div>
            </div>

            <div className="flow-line"></div>

            <div className="flow-item">
              <div className="flow-number">02</div>

              <div>
                <h3>Review</h3>
                <p>Understand the reasoning</p>
              </div>
            </div>

            <div className="flow-line"></div>

            <div className="flow-item">
              <div className="flow-number">03</div>

              <div>
                <h3>Replay</h3>
                <p>Learn from the outcome</p>
              </div>
            </div>
          </div>

          <div className="intro-footer">
            <span className="footer-dot"></span>
            Secure decision history and audit tracking
          </div>
        </section>

        <section className="login-section">
          <div className="login-card">
            <div className="card-top">
              <div>
                <p className="card-eyebrow">WELCOME BACK</p>

                <h2>Sign in to continue</h2>

                <p className="card-description">
                  Access your decision workspace.
                </p>
              </div>

              <div className="mini-logo">↗</div>
            </div>

            <form onSubmit={handleSubmit} className="login-form">
              <div className="input-group">
                <label htmlFor="email">Email address</label>

                <div className="input-wrapper">
                  <span className="input-icon">@</span>

                  <input
                    id="email"
                    type="email"
                    placeholder="you@example.com"
                    value={email}
                    onChange={(event) => setEmail(event.target.value)}
                    required
                  />
                </div>
              </div>

              <div className="input-group">
                <label htmlFor="password">Password</label>

                <div className="input-wrapper">
                  <span className="input-icon">＊</span>

                  <input
                    id="password"
                    type="password"
                    placeholder="Enter your password"
                    value={password}
                    onChange={(event) => setPassword(event.target.value)}
                    required
                  />
                </div>
              </div>

              <div className="login-options">
                <span className="secure-text">
                  🔒 Secure authentication
                </span>

                <span className="forgot-text">
                  Password protected
                </span>
              </div>

              <button
                type="submit"
                className="login-button"
                disabled={loading}
              >
                {loading ? (
                  "Signing in..."
                ) : (
                  <>
                    Sign in
                    <span className="button-arrow">→</span>
                  </>
                )}
              </button>
            </form>

            {message && (
              <p
                className={
                  message === "Login successful!"
                    ? "login-message success-message"
                    : "login-message error-message"
                }
              >
                {message}
              </p>
            )}

            <div className="register-area">
              <span>New to the platform?</span>

              <Link to="/register">
                Create an account
                <span>↗</span>
              </Link>
            </div>

            <div className="card-bottom">
              <span>Expert Decision Replay Platform</span>
              <span>v1.0</span>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}

export default Login;