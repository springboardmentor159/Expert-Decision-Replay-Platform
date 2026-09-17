import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const Register = () => {
  const { register } = useAuth();
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

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    setError("");
    setSuccess("");

    if (!formData.full_name.trim()) {
      setError("Full name is required.");
      return;
    }

    if (!formData.email.trim()) {
      setError("Email is required.");
      return;
    }

    if (formData.password.length < 6) {
      setError("Password must contain at least 6 characters.");
      return;
    }

    if (formData.password !== formData.confirm_password) {
      setError("Passwords do not match.");
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

      await register(userData);

      setSuccess("Registration successful. You can now login.");

      setTimeout(() => {
        navigate("/login");
      }, 1000);
    } catch (err) {
      const status = err.response?.status;

      if (status === 400) {
        setError(
          err.response?.data?.detail || "Registration failed."
        );
      } else if (status === 422) {
        setError("Please check the entered information.");
      } else if (status >= 500) {
        setError("Server error. Please try again later.");
      } else if (!err.response) {
        setError("Cannot connect to the backend server.");
      } else {
        setError("Registration failed.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="register-card">

        {/* Header */}
        <div className="register-header">
          <div className="register-logo">
            EDR
          </div>

          <div>
            <h1>Expert Decision Replay Platform</h1>
            <p>Create your account to get started</p>
          </div>
        </div>

        {/* Title */}
        <div className="register-title">
          <h2>Create Account</h2>
          <p>Enter your details to register</p>
        </div>

        {/* Messages */}
        {error && (
          <div className="register-message register-error">
            {error}
          </div>
        )}

        {success && (
          <div className="register-message register-success">
            {success}
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit}>

          {/* Personal Information */}
          <div className="register-section">
            <h3>Personal Information</h3>

            <div className="register-grid">

              <div className="register-field">
                <label htmlFor="full_name">
                  Full Name <span>*</span>
                </label>

                <input
                  id="full_name"
                  type="text"
                  name="full_name"
                  value={formData.full_name}
                  onChange={handleChange}
                  placeholder="Enter full name"
                  autoComplete="name"
                />
              </div>

              <div className="register-field">
                <label htmlFor="email">
                  Email <span>*</span>
                </label>

                <input
                  id="email"
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  placeholder="Enter email address"
                  autoComplete="email"
                />
              </div>

            </div>
          </div>

          {/* Account Information */}
          <div className="register-section">
            <h3>Account Information</h3>

            <div className="register-grid">

              <div className="register-field">
                <label htmlFor="password">
                  Password <span>*</span>
                </label>

                <input
                  id="password"
                  type="password"
                  name="password"
                  value={formData.password}
                  onChange={handleChange}
                  placeholder="Minimum 6 characters"
                  autoComplete="new-password"
                />
              </div>

              <div className="register-field">
                <label htmlFor="confirm_password">
                  Confirm Password <span>*</span>
                </label>

                <input
                  id="confirm_password"
                  type="password"
                  name="confirm_password"
                  value={formData.confirm_password}
                  onChange={handleChange}
                  placeholder="Confirm your password"
                  autoComplete="new-password"
                />
              </div>

              <div className="register-field register-full-width">
                <label htmlFor="role">
                  Role <span>*</span>
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
                </select>
              </div>

            </div>
          </div>

          {/* Professional Information */}
          <div className="register-section">
            <h3>Professional Information</h3>

            <div className="register-grid">

              <div className="register-field">
                <label htmlFor="employee_id">
                  Employee ID
                </label>

                <input
                  id="employee_id"
                  type="text"
                  name="employee_id"
                  value={formData.employee_id}
                  onChange={handleChange}
                  placeholder="Enter employee ID"
                />
              </div>

              <div className="register-field">
                <label htmlFor="department">
                  Department
                </label>

                <input
                  id="department"
                  type="text"
                  name="department"
                  value={formData.department}
                  onChange={handleChange}
                  placeholder="Enter department"
                />
              </div>

              <div className="register-field">
                <label htmlFor="designation">
                  Designation
                </label>

                <input
                  id="designation"
                  type="text"
                  name="designation"
                  value={formData.designation}
                  onChange={handleChange}
                  placeholder="Enter designation"
                />
              </div>

              <div className="register-field">
                <label htmlFor="phone_number">
                  Phone Number
                </label>

                <input
                  id="phone_number"
                  type="tel"
                  name="phone_number"
                  value={formData.phone_number}
                  onChange={handleChange}
                  placeholder="Enter phone number"
                />
              </div>

            </div>
          </div>

          {/* Submit */}
          <button
            type="submit"
            className="register-submit"
            disabled={loading}
          >
            {loading ? "Creating Account..." : "Create Account"}
          </button>

        </form>

        {/* Login Link */}
        <div className="register-login">
          <span>Already have an account?</span>

          <button
            type="button"
            onClick={() => navigate("/login")}
          >
            Login
          </button>
        </div>

      </div>
    </div>
  );
};

export default Register;