import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import Alert from "../components/Alert";

const Login = () => {
  const { login } = useAuth();
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();

    setError("");

    if (!email.trim() || !password) {
      setError("Please enter your email and password.");
      return;
    }

    try {
      setLoading(true);

      const user = await login(email.trim(), password);

      if (user.role === "Employee") {
        navigate("/employee-dashboard");
      } else if (user.role === "Reviewer") {
        navigate("/reviewer-dashboard");
      } else if (user.role === "Manager") {
        navigate("/manager-dashboard");
      } else if (user.role === "Administrator") {
        navigate("/admin-dashboard");
      } else {
        navigate("/dashboard");
      }
    } catch (err) {
      console.error("Login error:", err);

      const status = err.response?.status;

      if (status === 401) {
        setError("Invalid email or password.");
      } else if (status === 403) {
        setError("You are not authorized to login.");
      } else if (status === 422) {
        setError("Please enter valid login details.");
      } else if (status >= 500) {
        setError("Server error. Please try again later.");
      } else if (err.request) {
        setError(
          "Unable to connect to the backend. Please make sure FastAPI is running."
        );
      } else {
        setError(err.message || "Login failed. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card">

        <div className="auth-logo">
          ED
        </div>

        <h1>Expert Decision Replay Platform</h1>

        <p className="auth-subtitle">
          Sign in to your account
        </p>

        {error && (
          <Alert
            message={error}
            type="error"
            onClose={() => setError("")}
          />
        )}

        <form onSubmit={handleSubmit}>

          <div className="form-group">
            <label htmlFor="email">
              Email
            </label>

            <input
              id="email"
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              placeholder="Enter your email"
              autoComplete="email"
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">
              Password
            </label>

            <input
              id="password"
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              placeholder="Enter your password"
              autoComplete="current-password"
            />
          </div>

          <button
            type="submit"
            className="auth-submit"
            disabled={loading}
          >
            {loading ? "Signing in..." : "Login"}
          </button>

        </form>

        <div className="auth-register">
          <span>Don't have an account?</span>

          <button
            type="button"
            onClick={() => navigate("/register")}
          >
            Register
          </button>
        </div>

      </div>
    </div>
  );
};

export default Login;