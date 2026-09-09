import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import apiClient from "../api/apiClient";

const roles = [
  "Employee",
  "Reviewer",
  "Manager",
  "Administrator",
];

const initialForm = {
  full_name: "",
  email: "",
  password: "",
  confirm_password: "",
  role: "Employee",
  employee_id: "",
  department: "",
  designation: "",
  phone_number: "",
};

function Register() {
  const navigate = useNavigate();

  const [form, setForm] = useState(initialForm);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);

  const handleChange = (event) => {
    const { name, value } = event.target;

    setForm((previous) => ({
      ...previous,
      [name]: value,
    }));

    setError("");
    setSuccess("");
  };

  const validateForm = () => {
    if (!form.full_name.trim()) {
      return "Full name is required.";
    }

    if (form.full_name.trim().length < 2) {
      return "Full name must contain at least 2 characters.";
    }

    if (!form.email.trim()) {
      return "Email is required.";
    }

    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (!emailPattern.test(form.email.trim())) {
      return "Please enter a valid email address.";
    }

    if (!form.password) {
      return "Password is required.";
    }

    if (form.password.length < 8) {
      return "Password must contain at least 8 characters.";
    }

    if (form.password !== form.confirm_password) {
      return "Passwords do not match.";
    }

    if (!form.role) {
      return "Please select a role.";
    }

    return null;
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    setError("");
    setSuccess("");

    const validationError = validateForm();

    if (validationError) {
      setError(validationError);
      return;
    }

    setLoading(true);

    const payload = {
      full_name: form.full_name.trim(),
      email: form.email.trim(),
      role: form.role,
      password: form.password,
      employee_id: form.employee_id.trim() || null,
      department: form.department.trim() || null,
      designation: form.designation.trim() || null,
      phone_number: form.phone_number.trim() || null,
    };

    try {
      await apiClient.post("/users", payload);

      setSuccess(
        "Registration successful. Redirecting to login..."
      );

      setForm(initialForm);

      setTimeout(() => {
        navigate("/login", { replace: true });
      }, 1200);
    } catch (err) {
      if (err.response?.status === 422) {
        const detail = err.response?.data?.detail;

        if (Array.isArray(detail)) {
          setError(
            detail
              .map((item) => item.msg)
              .join(" ")
          );
        } else {
          setError(
            detail || "Please check the entered information."
          );
        }
      } else if (err.response?.status === 400) {
        setError(
          err.response?.data?.detail ||
            "Unable to create the account."
        );
      } else if (err.response?.status === 409) {
        setError(
          err.response?.data?.detail ||
            "An account with this email already exists."
        );
      } else {
        setError(
          "Unable to connect to the server. Please try again."
        );
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card register-card">
        <div className="auth-header">
          <h1>Create Account</h1>
          <p>Join the Expert Decision Replay Platform</p>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="full_name">
              Full Name <span className="required">*</span>
            </label>

            <input
              id="full_name"
              name="full_name"
              type="text"
              value={form.full_name}
              onChange={handleChange}
              placeholder="Enter your full name"
              autoComplete="name"
            />
          </div>

          <div className="form-group">
            <label htmlFor="email">
              Email <span className="required">*</span>
            </label>

            <input
              id="email"
              name="email"
              type="email"
              value={form.email}
              onChange={handleChange}
              placeholder="Enter your email"
              autoComplete="email"
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">
              Password <span className="required">*</span>
            </label>

            <input
              id="password"
              name="password"
              type="password"
              value={form.password}
              onChange={handleChange}
              placeholder="Minimum 8 characters"
              autoComplete="new-password"
            />
          </div>

          <div className="form-group">
            <label htmlFor="confirm_password">
              Confirm Password <span className="required">*</span>
            </label>

            <input
              id="confirm_password"
              name="confirm_password"
              type="password"
              value={form.confirm_password}
              onChange={handleChange}
              placeholder="Re-enter your password"
              autoComplete="new-password"
            />
          </div>

          <div className="form-group">
            <label htmlFor="role">
              Role <span className="required">*</span>
            </label>

            <select
              id="role"
              name="role"
              value={form.role}
              onChange={handleChange}
            >
              {roles.map((role) => (
                <option key={role} value={role}>
                  {role}
                </option>
              ))}
            </select>
          </div>

          <div className="form-section-title">
            Additional Information
          </div>

          <div className="form-group">
            <label htmlFor="employee_id">Employee ID</label>

            <input
              id="employee_id"
              name="employee_id"
              type="text"
              value={form.employee_id}
              onChange={handleChange}
              placeholder="Optional"
            />
          </div>

          <div className="form-group">
            <label htmlFor="department">Department</label>

            <input
              id="department"
              name="department"
              type="text"
              value={form.department}
              onChange={handleChange}
              placeholder="Optional"
            />
          </div>

          <div className="form-group">
            <label htmlFor="designation">Designation</label>

            <input
              id="designation"
              name="designation"
              type="text"
              value={form.designation}
              onChange={handleChange}
              placeholder="Optional"
            />
          </div>

          <div className="form-group">
            <label htmlFor="phone_number">Phone Number</label>

            <input
              id="phone_number"
              name="phone_number"
              type="tel"
              value={form.phone_number}
              onChange={handleChange}
              placeholder="Optional"
            />
          </div>

          {error && (
            <div className="form-error" role="alert">
              {error}
            </div>
          )}

          {success && (
            <div className="form-success" role="status">
              {success}
            </div>
          )}

          <button type="submit" disabled={loading}>
            {loading ? "Creating Account..." : "Create Account"}
          </button>
        </form>

        <p className="auth-footer">
          Already have an account?{" "}
          <Link to="/login">Sign in</Link>
        </p>
      </div>
    </div>
  );
}

export default Register;