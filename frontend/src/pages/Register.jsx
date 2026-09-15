import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import api from "../services/api";

function Register() {
  const navigate = useNavigate();

  const [form, setForm] = useState({
    full_name: "",
    email: "",
    password: "",
    role: "Employee",
    employee_id: "",
    department: "",
    designation: "",
    phone_number: "",
  });

  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setForm({
      ...form,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    setError("");
    setSuccess("");

    if (
      !form.full_name.trim() ||
      !form.email.trim() ||
      !form.password.trim() ||
      !form.employee_id.trim()
    ) {
      setError("Please fill in all required fields.");
      return;
    }

    try {
      setLoading(true);

      await api.post("/users/", form);

      setSuccess("Registration successful! Redirecting to login...");

      setTimeout(() => {
        navigate("/login");
      }, 1500);
    } catch (err) {
      if (err.response?.status === 400) {
        setError(err.response.data.detail || "Registration failed.");
      } else if (err.response?.status === 422) {
        setError("Please enter valid registration details.");
      } else if (err.response?.status >= 500) {
        setError("Server error. Please try again later.");
      } else {
        setError("Registration failed. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page register-auth-page">
      {/* Left panel */}
      <div className="auth-brand-panel">
        <div className="auth-brand-content">
          <div className="auth-logo">ED</div>

          <h1>Expert Decision</h1>
          <h1>Replay Platform</h1>

          <p>
            Create your account and join a centralized workspace for
            structured decision management and expert collaboration.
          </p>

          <div className="auth-feature-list">
            <div>
              <span>✓</span>
              Centralized decision management
            </div>

            <div>
              <span>✓</span>
              Role-based access control
            </div>

            <div>
              <span>✓</span>
              Approval and review workflows
            </div>

            <div>
              <span>✓</span>
              Secure audit and reporting
            </div>
          </div>
        </div>

        <div className="auth-brand-footer">
          Expert Decision Replay Platform
        </div>
      </div>

      {/* Registration panel */}
      <div className="auth-form-panel register-form-panel">
        <div className="auth-form-container register-form-container">
          <div className="mobile-auth-logo">ED</div>

          <div className="auth-form-header">
            <span className="auth-eyebrow">ACCOUNT SETUP</span>

            <h2>Create your account</h2>

            <p>
              Enter your details to create an account on the decision
              management platform.
            </p>
          </div>

          <form className="auth-form register-form" onSubmit={handleSubmit}>
            <div className="register-fields-grid">
              {/* Full Name */}
              <div className="auth-field register-full-width">
                <label htmlFor="full_name">
                  Full Name <span>*</span>
                </label>

                <input
                  id="full_name"
                  name="full_name"
                  value={form.full_name}
                  onChange={handleChange}
                  placeholder="Enter full name"
                  autoComplete="name"
                />
              </div>

              {/* Email */}
              <div className="auth-field">
                <label htmlFor="email">
                  Email <span>*</span>
                </label>

                <input
                  id="email"
                  type="email"
                  name="email"
                  value={form.email}
                  onChange={handleChange}
                  placeholder="Enter email"
                  autoComplete="email"
                />
              </div>

              {/* Password */}
              <div className="auth-field">
                <label htmlFor="password">
                  Password <span>*</span>
                </label>

                <input
                  id="password"
                  type="password"
                  name="password"
                  value={form.password}
                  onChange={handleChange}
                  placeholder="Create password"
                  autoComplete="new-password"
                />
              </div>

              {/* Role */}
              <div className="auth-field">
                <label htmlFor="role">Role</label>

                <select
                  id="role"
                  name="role"
                  value={form.role}
                  onChange={handleChange}
                >
                  <option value="Employee">Employee</option>
                  <option value="Reviewer">Reviewer</option>
                  <option value="Manager">Manager</option>
                  <option value="Administrator">Administrator</option>
                </select>
              </div>

              {/* Employee ID */}
              <div className="auth-field">
                <label htmlFor="employee_id">
                  Employee ID <span>*</span>
                </label>

                <input
                  id="employee_id"
                  name="employee_id"
                  value={form.employee_id}
                  onChange={handleChange}
                  placeholder="Enter employee ID"
                />
              </div>

              {/* Department */}
              <div className="auth-field">
                <label htmlFor="department">Department</label>

                <input
                  id="department"
                  name="department"
                  value={form.department}
                  onChange={handleChange}
                  placeholder="Enter department"
                />
              </div>

              {/* Designation */}
              <div className="auth-field">
                <label htmlFor="designation">Designation</label>

                <input
                  id="designation"
                  name="designation"
                  value={form.designation}
                  onChange={handleChange}
                  placeholder="Enter designation"
                />
              </div>

              {/* Phone */}
              <div className="auth-field">
                <label htmlFor="phone_number">Phone Number</label>

                <input
                  id="phone_number"
                  name="phone_number"
                  value={form.phone_number}
                  onChange={handleChange}
                  placeholder="Enter phone number"
                  autoComplete="tel"
                />
              </div>
            </div>

            {error && (
              <div className="auth-error">
                <span>!</span>
                <p>{error}</p>
              </div>
            )}

            {success && (
              <div className="auth-success">
                <span>✓</span>
                <p>{success}</p>
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
                  Creating account...
                </>
              ) : (
                "Create Account"
              )}
            </button>
          </form>

          <div className="auth-divider">
            <span>OR</span>
          </div>

          <div className="auth-register-prompt">
            <span>Already have an account?</span>
            <Link to="/login">Sign in</Link>
          </div>

          <div className="auth-security-note">
            <span>🔒</span>
            <p>
              Your account information is protected by secure authentication.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Register;