import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { registerUser } from "../auth/authService";

function Register() {
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    full_name: "",
    email: "",
    password: "",
    confirm_password: "",
    role: "Employee",
    employee_id: "",
    department: "",
    designation: "",
    phone_number: "",
  });

  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
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
    setSuccess("");

    if (
      !formData.full_name.trim() ||
      !formData.email.trim() ||
      !formData.password
    ) {
      setError("Please fill in all required fields.");
      return;
    }

    if (formData.password !== formData.confirm_password) {
      setError("Passwords do not match.");
      return;
    }

    if (formData.password.length < 6) {
      setError("Password must contain at least 6 characters.");
      return;
    }

    try {
      setLoading(true);

      const userData = {
        full_name: formData.full_name.trim(),
        email: formData.email.trim(),
        password: formData.password,
        role: formData.role,
        employee_id: formData.employee_id.trim() || null,
        department: formData.department.trim() || null,
        designation: formData.designation.trim() || null,
        phone_number: formData.phone_number.trim() || null,
      };

      await registerUser(userData);

      setSuccess(
        "Account created successfully. Redirecting to login..."
      );

      setTimeout(() => {
        navigate("/login");
      }, 1500);
    } catch (error) {
      if (error.response?.status === 400) {
        setError(
          error.response?.data?.detail ||
            "Unable to create account."
        );
      } else if (error.response?.status === 422) {
        setError(
          "Please check the information entered."
        );
      } else if (error.response?.status >= 500) {
        setError(
          "Server error. Please try again later."
        );
      } else {
        setError(
          error.response?.data?.detail ||
            "Registration failed. Please try again."
        );
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="register-page">
      <div className="register-card">

        <div className="register-brand">
          <div className="brand-icon">ED</div>

          <h1>Expert Decision Replay</h1>

          <p>
            Create your account and start collaborating
            on better decisions.
          </p>
        </div>

        <div className="register-form-section">
          <h2>Create an account</h2>

          <p className="register-subtitle">
            Enter your details to get started
          </p>

          {error && (
            <div className="error-message">
              {error}
            </div>
          )}

          {success && (
            <div className="success-message">
              {success}
            </div>
          )}

          <form onSubmit={handleSubmit}>

            <div className="form-group">
              <label htmlFor="full_name">
                Full name *
              </label>

              <input
                id="full_name"
                name="full_name"
                type="text"
                value={formData.full_name}
                onChange={handleChange}
                placeholder="Enter your full name"
              />
            </div>

            <div className="form-group">
              <label htmlFor="email">
                Email address *
              </label>

              <input
                id="email"
                name="email"
                type="email"
                value={formData.email}
                onChange={handleChange}
                placeholder="Enter your email"
              />
            </div>

            <div className="form-row">

              <div className="form-group">
                <label htmlFor="employee_id">
                  Employee ID
                </label>

                <input
                  id="employee_id"
                  name="employee_id"
                  type="text"
                  value={formData.employee_id}
                  onChange={handleChange}
                  placeholder="Employee ID"
                />
              </div>

              <div className="form-group">
                <label htmlFor="role">
                  Role
                </label>

                <select
                  id="role"
                  name="role"
                  value={formData.role}
                  onChange={handleChange}
                >
                  <option value="Employee">Employee</option>
                  <option value="Reviewer">Reviewer</option>
                  <option value="Manager">Manager</option>
                  <option value="Administrator">
                    Administrator
                  </option>
                  <option value="HR">HR</option>
                </select>
              </div>

            </div>

            <div className="form-row">

              <div className="form-group">
                <label htmlFor="department">
                  Department
                </label>

                <input
                  id="department"
                  name="department"
                  type="text"
                  value={formData.department}
                  onChange={handleChange}
                  placeholder="Department"
                />
              </div>

              <div className="form-group">
                <label htmlFor="designation">
                  Designation
                </label>

                <input
                  id="designation"
                  name="designation"
                  type="text"
                  value={formData.designation}
                  onChange={handleChange}
                  placeholder="Designation"
                />
              </div>

            </div>

            <div className="form-group">
              <label htmlFor="phone_number">
                Phone number
              </label>

              <input
                id="phone_number"
                name="phone_number"
                type="tel"
                value={formData.phone_number}
                onChange={handleChange}
                placeholder="Phone number"
              />
            </div>

            <div className="form-row">

              <div className="form-group">
                <label htmlFor="password">
                  Password *
                </label>

                <input
                  id="password"
                  name="password"
                  type="password"
                  value={formData.password}
                  onChange={handleChange}
                  placeholder="Minimum 6 characters"
                />
              </div>

              <div className="form-group">
                <label htmlFor="confirm_password">
                  Confirm password *
                </label>

                <input
                  id="confirm_password"
                  name="confirm_password"
                  type="password"
                  value={formData.confirm_password}
                  onChange={handleChange}
                  placeholder="Confirm password"
                />
              </div>

            </div>

            <button
              type="submit"
              className="login-button"
              disabled={loading}
            >
              {loading
                ? "Creating account..."
                : "Create Account"}
            </button>

          </form>

          <div className="register-section">
            <span>Already have an account?</span>{" "}
            <Link to="/login">
              Sign in
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

export default Register;