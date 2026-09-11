import { useState, type FormEvent, type ChangeEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  UserPlus,
  User,
  Mail,
  Lock,
  Phone,
  Briefcase,
} from "lucide-react";
import { isAxiosError } from "axios";
import api from "../services/api";

type UserRole = "Employee" | "Reviewer";

export default function Register() {
  const navigate = useNavigate();

  const [form, setForm] = useState({
    full_name: "",
    email: "",
    password: "",
    confirm_password: "",
    role: "Employee" as UserRole,
    employee_id: "",
    department: "",
    designation: "",
    phone_number: "",
  });

  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleChange = (
    event: ChangeEvent<HTMLInputElement | HTMLSelectElement>,
  ) => {
    const { name, value } = event.target;

    setForm((current) => ({
      ...current,
      [name]: value,
    }));
  };

  const handleSubmit = async (
    event: FormEvent<HTMLFormElement>,
  ) => {
    event.preventDefault();

    setError("");
    setSuccess("");

    if (!form.full_name.trim()) {
      setError("Please enter your full name.");
      return;
    }

    if (!form.email.trim()) {
      setError("Please enter your email address.");
      return;
    }

    if (!form.password) {
      setError("Please enter a password.");
      return;
    }

    if (form.password.length < 6) {
      setError(
        "Password must contain at least 6 characters.",
      );
      return;
    }

    if (form.password !== form.confirm_password) {
      setError("Passwords do not match.");
      return;
    }

    try {
      setIsSubmitting(true);

      await api.post("/users", {
        full_name: form.full_name.trim(),
        email: form.email.trim(),
        role: form.role,
        password: form.password,
        employee_id: form.employee_id.trim() || null,
        department: form.department.trim() || null,
        designation: form.designation.trim() || null,
        phone_number: form.phone_number.trim() || null,
      });

      setSuccess(
        "Registration successful. Redirecting to login...",
      );

      setTimeout(() => {
        navigate("/login", { replace: true });
      }, 1200);
    } catch (err: unknown) {
      if (isAxiosError(err)) {
        const status = err.response?.status;
        const detail = err.response?.data?.detail;

        if (status === 409) {
          setError(
            typeof detail === "string"
              ? detail
              : "Email or Employee ID already exists.",
          );
        } else if (status === 422) {
          setError(
            "Please check the entered information.",
          );
        } else if (status && status >= 500) {
          setError(
            "Server error. Please try again later.",
          );
        } else if (err.request) {
          setError(
            "Unable to connect to the server. Make sure the FastAPI backend is running.",
          );
        } else {
          setError(
            "Registration failed. Please try again.",
          );
        }
      } else {
        setError(
          "Registration failed. Please try again.",
        );
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <main className="auth-page">
      <section className="auth-card register-card">
        <div className="auth-header">
          <div className="auth-logo">
            <UserPlus size={24} />
          </div>

          <h1>Create Account</h1>

          <p>
            Register for the Expert Decision Replay Platform
          </p>
        </div>

        <form
          onSubmit={handleSubmit}
          className="auth-form"
        >
          <div className="form-group">
            <label htmlFor="full_name">
              Full Name
            </label>

            <div className="input-wrapper">
              <User size={18} />

              <input
                id="full_name"
                name="full_name"
                type="text"
                value={form.full_name}
                onChange={handleChange}
                placeholder="Enter your full name"
                autoComplete="name"
                disabled={isSubmitting}
              />
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="email">
              Email Address
            </label>

            <div className="input-wrapper">
              <Mail size={18} />

              <input
                id="email"
                name="email"
                type="email"
                value={form.email}
                onChange={handleChange}
                placeholder="Enter your email"
                autoComplete="email"
                disabled={isSubmitting}
              />
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="password">
              Password
            </label>

            <div className="input-wrapper">
              <Lock size={18} />

              <input
                id="password"
                name="password"
                type="password"
                value={form.password}
                onChange={handleChange}
                placeholder="Create a password"
                autoComplete="new-password"
                disabled={isSubmitting}
              />
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="confirm_password">
              Confirm Password
            </label>

            <div className="input-wrapper">
              <Lock size={18} />

              <input
                id="confirm_password"
                name="confirm_password"
                type="password"
                value={form.confirm_password}
                onChange={handleChange}
                placeholder="Confirm your password"
                autoComplete="new-password"
                disabled={isSubmitting}
              />
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="role">
              Role
            </label>

            <div className="input-wrapper">
              <Briefcase size={18} />

              <select
                id="role"
                name="role"
                value={form.role}
                onChange={handleChange}
                disabled={isSubmitting}
              >
                <option value="Employee">
                  Employee
                </option>

                <option value="Reviewer">
                  Reviewer
                </option>
              </select>
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="employee_id">
              Employee ID
            </label>

            <div className="input-wrapper">
              <User size={18} />

              <input
                id="employee_id"
                name="employee_id"
                type="text"
                value={form.employee_id}
                onChange={handleChange}
                placeholder="Enter employee ID"
                disabled={isSubmitting}
              />
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="department">
              Department
            </label>

            <div className="input-wrapper">
              <Briefcase size={18} />

              <input
                id="department"
                name="department"
                type="text"
                value={form.department}
                onChange={handleChange}
                placeholder="Enter department"
                disabled={isSubmitting}
              />
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="designation">
              Designation
            </label>

            <div className="input-wrapper">
              <Briefcase size={18} />

              <input
                id="designation"
                name="designation"
                type="text"
                value={form.designation}
                onChange={handleChange}
                placeholder="Enter designation"
                disabled={isSubmitting}
              />
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="phone_number">
              Phone Number
            </label>

            <div className="input-wrapper">
              <Phone size={18} />

              <input
                id="phone_number"
                name="phone_number"
                type="tel"
                value={form.phone_number}
                onChange={handleChange}
                placeholder="Enter phone number"
                autoComplete="tel"
                disabled={isSubmitting}
              />
            </div>
          </div>

          {error && (
            <div
              className="auth-error"
              role="alert"
            >
              {error}
            </div>
          )}

          {success && (
            <div
              className="auth-success"
              role="status"
            >
              {success}
            </div>
          )}

          <button
            type="submit"
            className="auth-submit"
            disabled={isSubmitting}
          >
            {isSubmitting
              ? "Creating Account..."
              : "Create Account"}
          </button>
        </form>

        <div className="auth-footer">
          <span>
            Already have an account?
          </span>

          <Link to="/login">
            Sign in
          </Link>
        </div>
      </section>
    </main>
  );
}