import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { loginUser, saveAuthData } from "../auth/authService";

function Login() {
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    email: "",
    password: "",
  });

  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleChange = (event) => {
    const { name, value } = event.target;

    setFormData((previous) => ({
      ...previous,
      [name]: value,
    }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    setError("");

    if (!formData.email.trim() || !formData.password) {
      setError("Please enter both email and password.");
      return;
    }

    try {
      setLoading(true);

      const data = await loginUser(
        formData.email.trim(),
        formData.password
      );

      saveAuthData(data);

      navigate("/dashboard");
    } catch (error) {
      if (error.response?.status === 401) {
        setError("Invalid email or password.");
      } else if (error.response?.status === 422) {
        setError("Please check the entered information.");
      } else if (error.response?.status >= 500) {
        setError("Server error. Please try again later.");
      } else {
        setError(
          error.response?.data?.detail ||
            "Unable to login. Please try again."
        );
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-page">
      <div className="login-card">

        <div className="login-brand">
          <div className="brand-icon">ED</div>

          <h1>Expert Decision Replay</h1>

          <p>
            Make better decisions with knowledge,
            collaboration and expert insights.
          </p>
        </div>

        <div className="login-form-section">
          <h2>Welcome back</h2>

          <p className="login-subtitle">
            Sign in to continue to your account
          </p>

          {error && (
            <div className="error-message">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit}>

            <div className="form-group">
              <label htmlFor="email">
                Email address
              </label>

              <input
                id="email"
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
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
                name="password"
                value={formData.password}
                onChange={handleChange}
                placeholder="Enter your password"
                autoComplete="current-password"
              />
            </div>

            <button
              type="submit"
              className="login-button"
              disabled={loading}
            >
              {loading ? "Signing in..." : "Sign In"}
            </button>

          </form>

          <div className="register-section">
            <span>Don't have an account?</span>{" "}
            <Link to="/register">
              Create an account
            </Link>
          </div>
        </div>

        <div className="login-footer">
          Expert Decision Replay Platform
        </div>

      </div>
    </div>
  );
}

export default Login;