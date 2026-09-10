import { useState, type FormEvent } from "react";
import {
  ArrowRight,
  BriefcaseBusiness,
  Building2,
  Eye,
  EyeOff,
  IdCard,
  LockKeyhole,
  Mail,
  Phone,
  ShieldCheck,
  UserRound,
} from "lucide-react";
import { Link, useNavigate } from "react-router-dom";

import api from "../services/api";
import "./RegisterPage.css";

type UserRole =
  | "employee"
  | "reviewer"
  | "manager"
  | "administrator";

interface RegisterForm {
  full_name: string;
  email: string;
  role: UserRole;
  password: string;
  confirmPassword: string;
  employee_id: string;
  department: string;
  designation: string;
  phone_number: string;
}

const ROLE_OPTIONS: Array<{
  value: UserRole;
  label: string;
  description: string;
}> = [
  {
    value: "employee",
    label: "Employee",
    description: "Create and manage decisions.",
  },
  {
    value: "reviewer",
    label: "Reviewer",
    description: "Review decisions and provide feedback.",
  },
  {
    value: "manager",
    label: "Manager",
    description: "Oversee decisions and approvals.",
  },
  {
    value: "administrator",
    label: "Administrator",
    description: "Manage the platform and users.",
  },
];

export default function RegisterPage() {
  const navigate = useNavigate();

  const [form, setForm] = useState<RegisterForm>({
    full_name: "",
    email: "",
    role: "employee",
    password: "",
    confirmPassword: "",
    employee_id: "",
    department: "",
    designation: "",
    phone_number: "",
  });

  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] =
    useState(false);

  const [errorMessage, setErrorMessage] = useState("");
  const [successMessage, setSuccessMessage] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  function handleChange(
    field: keyof RegisterForm,
    value: string,
  ) {
    setForm((current) => ({
      ...current,
      [field]: value,
    }));

    setErrorMessage("");
    setSuccessMessage("");
  }

  async function handleSubmit(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    setErrorMessage("");
    setSuccessMessage("");

    const fullName = form.full_name.trim();
    const email = form.email.trim();
    const employeeId = form.employee_id.trim();
    const department = form.department.trim();
    const designation = form.designation.trim();
    const phoneNumber = form.phone_number.trim();

    if (
      !fullName ||
      !email ||
      !form.role ||
      !form.password ||
      !form.confirmPassword ||
      !employeeId ||
      !department ||
      !designation ||
      !phoneNumber
    ) {
      setErrorMessage("Please complete all required fields.");
      return;
    }

    if (form.password.length < 8) {
      setErrorMessage(
        "Password must contain at least 8 characters.",
      );
      return;
    }

    if (form.password !== form.confirmPassword) {
      setErrorMessage("Passwords do not match.");
      return;
    }

    setIsSubmitting(true);

    try {
      await api.post("/users", {
        full_name: fullName,
        email,
        role: form.role,
        password: form.password,
        employee_id: employeeId,
        department,
        designation,
        phone_number: phoneNumber,
      });

      setSuccessMessage(
        "Account created successfully. Redirecting to sign in...",
      );

      window.setTimeout(() => {
        navigate("/login", { replace: true });
      }, 1200);
    } catch (error: unknown) {
      const response = (
        error as {
          response?: {
            status?: number;
            data?: {
              detail?: string;
            };
          };
        }
      )?.response;

      if (response?.status === 409) {
        setErrorMessage(
          response.data?.detail ||
            "The email or employee ID is already registered.",
        );
      } else if (response?.status === 422) {
        setErrorMessage(
          "Please check the information you entered and try again.",
        );
      } else if (
        response?.status &&
        response.status >= 500
      ) {
        setErrorMessage(
          "The server is temporarily unavailable. Please try again.",
        );
      } else {
        setErrorMessage(
          "Unable to create your account right now. Please try again later.",
        );
      }
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className="register-page">
      <section className="register-shell">
        <aside className="register-brand-panel">
          <div className="register-brand-content">
            <Link to="/login" className="register-brand">
              <span className="register-brand-mark">ED</span>

              <span className="register-brand-copy">
                <strong>Expert Decision</strong>
                <span>Replay Platform</span>
              </span>
            </Link>

            <div className="register-brand-main">
              <p className="register-eyebrow">
                DECISION KNOWLEDGE PLATFORM
              </p>

              <h1>
                Build the
                <br />
                knowledge
                <br />
                behind decisions.
              </h1>

              <p className="register-description">
                Create your platform account and become part of
                the decision lifecycle across your organization.
              </p>

              <div className="register-points">
                <div className="register-point">
                  <span className="register-point-icon">
                    <BriefcaseBusiness
                      size={15}
                      strokeWidth={1.8}
                    />
                  </span>

                  <div>
                    <strong>Structured decisions</strong>
                    <span>
                      Keep decision context and reasoning organized.
                    </span>
                  </div>
                </div>

                <div className="register-point">
                  <span className="register-point-icon">
                    <ShieldCheck
                      size={15}
                      strokeWidth={1.8}
                    />
                  </span>

                  <div>
                    <strong>Role-based access</strong>
                    <span>
                      Work according to your responsibilities.
                    </span>
                  </div>
                </div>

                <div className="register-point">
                  <span className="register-point-icon">
                    <IdCard
                      size={15}
                      strokeWidth={1.8}
                    />
                  </span>

                  <div>
                    <strong>Decision history</strong>
                    <span>
                      Preserve the knowledge behind organizational
                      decisions.
                    </span>
                  </div>
                </div>
              </div>
            </div>

            <div className="register-brand-footer">
              <span className="register-footer-line" />
              <span>One platform. One decision history.</span>
            </div>
          </div>
        </aside>

        <section className="register-form-panel">
          <div className="register-form-wrapper">
            <div className="register-form-header">
              <span className="register-form-kicker">
                CREATE ACCOUNT
              </span>

              <h2>Join the platform</h2>

              <p>
                Enter your details to create your Expert Decision
                Replay account.
              </p>
            </div>

            <form
              className="register-form"
              onSubmit={handleSubmit}
              noValidate
            >
              {errorMessage && (
                <div className="register-alert" role="alert">
                  {errorMessage}
                </div>
              )}

              {successMessage && (
                <div
                  className="register-success"
                  role="status"
                  aria-live="polite"
                >
                  {successMessage}
                </div>
              )}

              <div className="register-section-label">
                PERSONAL INFORMATION
              </div>

              <div className="register-grid">
                <div className="register-field register-field-full">
                  <label htmlFor="full_name">Full name</label>

                  <div className="register-input-wrapper">
                    <UserRound
                      className="register-input-icon"
                      size={18}
                      strokeWidth={1.8}
                      aria-hidden="true"
                    />

                    <input
                      id="full_name"
                      name="full_name"
                      type="text"
                      value={form.full_name}
                      onChange={(event) =>
                        handleChange(
                          "full_name",
                          event.target.value,
                        )
                      }
                      autoComplete="name"
                      placeholder="Your full name"
                      disabled={isSubmitting}
                      required
                    />
                  </div>
                </div>

                <div className="register-field">
                  <label htmlFor="email">Email address</label>

                  <div className="register-input-wrapper">
                    <Mail
                      className="register-input-icon"
                      size={18}
                      strokeWidth={1.8}
                      aria-hidden="true"
                    />

                    <input
                      id="email"
                      name="email"
                      type="email"
                      value={form.email}
                      onChange={(event) =>
                        handleChange(
                          "email",
                          event.target.value,
                        )
                      }
                      autoComplete="email"
                      placeholder="name@company.com"
                      disabled={isSubmitting}
                      required
                    />
                  </div>
                </div>

                <div className="register-field">
                  <label htmlFor="phone_number">Phone number</label>

                  <div className="register-input-wrapper">
                    <Phone
                      className="register-input-icon"
                      size={18}
                      strokeWidth={1.8}
                      aria-hidden="true"
                    />

                    <input
                      id="phone_number"
                      name="phone_number"
                      type="tel"
                      value={form.phone_number}
                      onChange={(event) =>
                        handleChange(
                          "phone_number",
                          event.target.value,
                        )
                      }
                      autoComplete="tel"
                      placeholder="Phone number"
                      disabled={isSubmitting}
                      required
                    />
                  </div>
                </div>
              </div>

              <div className="register-section-label">
                ORGANIZATION DETAILS
              </div>

              <div className="register-grid">
                <div className="register-field">
                  <label htmlFor="employee_id">
                    Employee ID
                  </label>

                  <div className="register-input-wrapper">
                    <IdCard
                      className="register-input-icon"
                      size={18}
                      strokeWidth={1.8}
                      aria-hidden="true"
                    />

                    <input
                      id="employee_id"
                      name="employee_id"
                      type="text"
                      value={form.employee_id}
                      onChange={(event) =>
                        handleChange(
                          "employee_id",
                          event.target.value,
                        )
                      }
                      placeholder="Employee ID"
                      disabled={isSubmitting}
                      required
                    />
                  </div>
                </div>

                <div className="register-field">
                  <label htmlFor="department">
                    Department
                  </label>

                  <div className="register-input-wrapper">
                    <Building2
                      className="register-input-icon"
                      size={18}
                      strokeWidth={1.8}
                      aria-hidden="true"
                    />

                    <input
                      id="department"
                      name="department"
                      type="text"
                      value={form.department}
                      onChange={(event) =>
                        handleChange(
                          "department",
                          event.target.value,
                        )
                      }
                      placeholder="Department"
                      disabled={isSubmitting}
                      required
                    />
                  </div>
                </div>

                <div className="register-field">
                  <label htmlFor="designation">
                    Designation
                  </label>

                  <div className="register-input-wrapper">
                    <BriefcaseBusiness
                      className="register-input-icon"
                      size={18}
                      strokeWidth={1.8}
                      aria-hidden="true"
                    />

                    <input
                      id="designation"
                      name="designation"
                      type="text"
                      value={form.designation}
                      onChange={(event) =>
                        handleChange(
                          "designation",
                          event.target.value,
                        )
                      }
                      placeholder="Designation"
                      disabled={isSubmitting}
                      required
                    />
                  </div>
                </div>

                <div className="register-field">
                  <label htmlFor="role">Platform role</label>

                  <div className="register-input-wrapper">
                    <ShieldCheck
                      className="register-input-icon"
                      size={18}
                      strokeWidth={1.8}
                      aria-hidden="true"
                    />

                    <select
                      id="role"
                      name="role"
                      value={form.role}
                      onChange={(event) =>
                        handleChange(
                          "role",
                          event.target.value,
                        )
                      }
                      disabled={isSubmitting}
                      required
                    >
                      {ROLE_OPTIONS.map((option) => (
                        <option
                          key={option.value}
                          value={option.value}
                        >
                          {option.label}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>
              </div>

              <div className="register-role-description">
                {
                  ROLE_OPTIONS.find(
                    (option) => option.value === form.role,
                  )?.description
                }
              </div>

              <div className="register-section-label">
                ACCOUNT SECURITY
              </div>

              <div className="register-grid">
                <div className="register-field">
                  <label htmlFor="password">Password</label>

                  <div className="register-input-wrapper">
                    <LockKeyhole
                      className="register-input-icon"
                      size={18}
                      strokeWidth={1.8}
                      aria-hidden="true"
                    />

                    <input
                      id="password"
                      name="password"
                      type={showPassword ? "text" : "password"}
                      value={form.password}
                      onChange={(event) =>
                        handleChange(
                          "password",
                          event.target.value,
                        )
                      }
                      autoComplete="new-password"
                      placeholder="Minimum 8 characters"
                      minLength={8}
                      disabled={isSubmitting}
                      required
                    />

                    <button
                      type="button"
                      className="register-password-toggle"
                      onClick={() =>
                        setShowPassword(
                          (current) => !current,
                        )
                      }
                      aria-label={
                        showPassword
                          ? "Hide password"
                          : "Show password"
                      }
                      disabled={isSubmitting}
                    >
                      {showPassword ? (
                        <EyeOff
                          size={18}
                          strokeWidth={1.8}
                          aria-hidden="true"
                        />
                      ) : (
                        <Eye
                          size={18}
                          strokeWidth={1.8}
                          aria-hidden="true"
                        />
                      )}
                    </button>
                  </div>
                </div>

                <div className="register-field">
                  <label htmlFor="confirmPassword">
                    Confirm password
                  </label>

                  <div className="register-input-wrapper">
                    <LockKeyhole
                      className="register-input-icon"
                      size={18}
                      strokeWidth={1.8}
                      aria-hidden="true"
                    />

                    <input
                      id="confirmPassword"
                      name="confirmPassword"
                      type={
                        showConfirmPassword
                          ? "text"
                          : "password"
                      }
                      value={form.confirmPassword}
                      onChange={(event) =>
                        handleChange(
                          "confirmPassword",
                          event.target.value,
                        )
                      }
                      autoComplete="new-password"
                      placeholder="Repeat your password"
                      minLength={8}
                      disabled={isSubmitting}
                      required
                    />

                    <button
                      type="button"
                      className="register-password-toggle"
                      onClick={() =>
                        setShowConfirmPassword(
                          (current) => !current,
                        )
                      }
                      aria-label={
                        showConfirmPassword
                          ? "Hide password"
                          : "Show password"
                      }
                      disabled={isSubmitting}
                    >
                      {showConfirmPassword ? (
                        <EyeOff
                          size={18}
                          strokeWidth={1.8}
                          aria-hidden="true"
                        />
                      ) : (
                        <Eye
                          size={18}
                          strokeWidth={1.8}
                          aria-hidden="true"
                        />
                      )}
                    </button>
                  </div>
                </div>
              </div>

              <button
                type="submit"
                className="register-submit"
                disabled={isSubmitting}
              >
                <span>
                  {isSubmitting
                    ? "Creating account..."
                    : "Create account"}
                </span>

                {!isSubmitting && (
                  <ArrowRight
                    size={19}
                    strokeWidth={2}
                    aria-hidden="true"
                  />
                )}
              </button>
            </form>

            <div className="register-security">
              <ShieldCheck
                size={17}
                strokeWidth={1.8}
                aria-hidden="true"
              />

              <span>
                Your account uses secure token-based
                authentication.
              </span>
            </div>

            <p className="register-login">
              Already have an account?{" "}
              <Link to="/login">Sign in</Link>
            </p>

            <p className="register-copyright">
              Expert Decision Replay Platform
            </p>
          </div>
        </section>
      </section>
    </main>
  );
}