import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import {
  AlertCircle,
  ArrowRight,
  Building2,
  CheckCircle2,
  IdCard,
  LockKeyhole,
  Mail,
  Phone,
  ShieldCheck,
  UserPlus,
  UserRound,
} from "lucide-react";

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

  const [form, setForm] =
    useState(initialForm);

  const [error, setError] =
    useState("");

  const [success, setSuccess] =
    useState("");

  const [loading, setLoading] =
    useState(false);


  const handleChange = (event) => {
    const {
      name,
      value,
    } = event.target;

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

    if (
      form.full_name.trim().length < 2
    ) {
      return (
        "Full name must contain at least 2 characters."
      );
    }

    if (!form.email.trim()) {
      return "Email is required.";
    }

    const emailPattern =
      /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (
      !emailPattern.test(
        form.email.trim()
      )
    ) {
      return (
        "Please enter a valid email address."
      );
    }

    if (!form.password) {
      return "Password is required.";
    }

    if (form.password.length < 8) {
      return (
        "Password must contain at least 8 characters."
      );
    }

    if (
      form.password !==
      form.confirm_password
    ) {
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

    const validationError =
      validateForm();

    if (validationError) {
      setError(validationError);
      return;
    }

    setLoading(true);

    const payload = {
      full_name:
        form.full_name.trim(),

      email:
        form.email.trim(),

      role:
        form.role,

      password:
        form.password,

      employee_id:
        form.employee_id.trim() ||
        null,

      department:
        form.department.trim() ||
        null,

      designation:
        form.designation.trim() ||
        null,

      phone_number:
        form.phone_number.trim() ||
        null,
    };


    try {
      await apiClient.post(
        "/users",
        payload
      );

      setSuccess(
        "Registration successful. Redirecting to login..."
      );

      setForm(initialForm);

      setTimeout(() => {
        navigate("/login", {
          replace: true,
        });
      }, 1200);

    } catch (err) {
      const status =
        err?.response?.status;

      const detail =
        err?.response?.data?.detail;

      if (status === 422) {
        if (Array.isArray(detail)) {
          setError(
            detail
              .map(
                (item) =>
                  item.msg
              )
              .join(" ")
          );
        } else {
          setError(
            detail ||
              "Please check the entered information."
          );
        }

      } else if (status === 400) {
        setError(
          detail ||
            "Unable to create the account."
        );

      } else if (status === 401) {
        setError(
          detail ||
            "You are not authorized to perform this action."
        );

      } else if (status === 403) {
        setError(
          detail ||
            "You do not have permission to create this account."
        );

      } else if (status === 409) {
        setError(
          detail ||
            "An account with this email already exists."
        );

      } else if (status >= 500) {
        setError(
          "The server is currently unavailable. Please try again later."
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
    <div className="register-page">

      <style>{`
        .register-page {
          min-height: 100vh;
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 30px 20px;
          background:
            radial-gradient(
              circle at 10% 10%,
              #dbeafe 0,
              transparent 30%
            ),
            radial-gradient(
              circle at 90% 90%,
              #e0e7ff 0,
              transparent 28%
            ),
            #f8fafc;
        }

        .register-layout {
          width: 100%;
          max-width: 1000px;
          display: grid;
          grid-template-columns: .85fr 1.15fr;
          overflow: hidden;
          border: 1px solid #e2e8f0;
          border-radius: 22px;
          background: #fff;
          box-shadow:
            0 25px 70px
            rgba(15, 23, 42, .10);
        }

        .register-brand {
          position: relative;
          padding: 45px;
          background: #0f172a;
          color: #fff;
          overflow: hidden;
        }

        .register-brand::before {
          content: "";
          position: absolute;
          width: 290px;
          height: 290px;
          right: -130px;
          top: -110px;
          border-radius: 50%;
          background: rgba(59, 130, 246, .18);
        }

        .register-brand::after {
          content: "";
          position: absolute;
          width: 220px;
          height: 220px;
          left: -110px;
          bottom: -100px;
          border-radius: 50%;
          background: rgba(99, 102, 241, .13);
        }

        .register-brand-content {
          position: relative;
          z-index: 1;
          height: 100%;
          display: flex;
          flex-direction: column;
          justify-content: space-between;
        }

        .register-brand-icon {
          width: 57px;
          height: 57px;
          margin-bottom: 25px;
          border-radius: 16px;
          background: rgba(255,255,255,.10);
          border: 1px solid rgba(255,255,255,.14);
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .register-eyebrow {
          margin-bottom: 9px;
          color: #93c5fd;
          font-size: 10px;
          font-weight: 800;
          letter-spacing: .12em;
          text-transform: uppercase;
        }

        .register-brand h1 {
          margin: 0;
          font-size: 30px;
          line-height: 1.18;
          letter-spacing: -.02em;
        }

        .register-brand-description {
          margin: 16px 0 0;
          color: #cbd5e1;
          font-size: 13px;
          line-height: 1.7;
        }

        .register-benefits {
          display: grid;
          gap: 12px;
          margin-top: 34px;
        }

        .register-benefit {
          display: flex;
          align-items: center;
          gap: 9px;
          color: #e2e8f0;
          font-size: 11px;
        }

        .register-benefit-icon {
          width: 27px;
          height: 27px;
          border-radius: 8px;
          background: rgba(59,130,246,.16);
          color: #93c5fd;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .register-form-panel {
          max-height: 88vh;
          overflow-y: auto;
          padding: 40px 42px;
          background: #fff;
        }

        .register-form-header {
          margin-bottom: 23px;
        }

        .register-form-header h2 {
          margin: 0;
          color: #0f172a;
          font-size: 25px;
        }

        .register-form-header p {
          margin: 7px 0 0;
          color: #64748b;
          font-size: 12px;
        }

        .register-alert {
          display: flex;
          align-items: flex-start;
          gap: 10px;
          margin-bottom: 18px;
          padding: 12px 13px;
          border-radius: 9px;
          font-size: 11px;
          line-height: 1.5;
        }

        .register-alert-error {
          border: 1px solid #fecaca;
          background: #fef2f2;
          color: #991b1b;
        }

        .register-alert-success {
          border: 1px solid #bbf7d0;
          background: #f0fdf4;
          color: #166534;
        }

        .register-alert strong {
          display: block;
          margin-bottom: 2px;
          font-size: 11px;
        }

        .register-section {
          margin: 23px 0 15px;
          padding-bottom: 9px;
          border-bottom: 1px solid #e2e8f0;
        }

        .register-section-title {
          display: flex;
          align-items: center;
          gap: 8px;
          color: #334155;
          font-size: 12px;
          font-weight: 800;
        }

        .register-section-title-icon {
          width: 26px;
          height: 26px;
          border-radius: 7px;
          background: #eff6ff;
          color: #2563eb;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .register-grid {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 15px;
        }

        .register-field {
          display: flex;
          flex-direction: column;
          gap: 6px;
        }

        .register-field-full {
          grid-column: 1 / -1;
        }

        .register-field label {
          color: #334155;
          font-size: 11px;
          font-weight: 750;
        }

        .register-required {
          color: #dc2626;
          margin-left: 2px;
        }

        .register-input-wrapper {
          position: relative;
        }

        .register-input-icon {
          position: absolute;
          left: 12px;
          top: 50%;
          transform: translateY(-50%);
          color: #94a3b8;
          pointer-events: none;
        }

        .register-input,
        .register-select {
          width: 100%;
          box-sizing: border-box;
          min-height: 42px;
          padding: 0 11px 0 38px;
          border: 1px solid #cbd5e1;
          border-radius: 8px;
          background: #fff;
          color: #0f172a;
          font-family: inherit;
          font-size: 12px;
          outline: none;
          transition: .15s ease;
        }

        .register-select {
          padding-left: 11px;
        }

        .register-input::placeholder {
          color: #94a3b8;
        }

        .register-input:focus,
        .register-select:focus {
          border-color: #2563eb;
          box-shadow:
            0 0 0 3px
            rgba(37,99,235,.10);
        }

        .register-input:disabled,
        .register-select:disabled {
          background: #f8fafc;
          cursor: not-allowed;
        }

        .register-submit {
          width: 100%;
          min-height: 45px;
          margin-top: 23px;
          border: none;
          border-radius: 9px;
          background: #2563eb;
          color: #fff;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 8px;
          font-family: inherit;
          font-size: 12px;
          font-weight: 750;
          cursor: pointer;
          transition: .15s ease;
        }

        .register-submit:hover:not(:disabled) {
          background: #1d4ed8;
          box-shadow:
            0 7px 18px
            rgba(37,99,235,.20);
        }

        .register-submit:disabled {
          opacity: .65;
          cursor: not-allowed;
        }

        .register-spinner {
          width: 15px;
          height: 15px;
          border: 2px solid rgba(255,255,255,.35);
          border-top-color: #fff;
          border-radius: 50%;
          animation:
            registerSpin .7s linear infinite;
        }

        @keyframes registerSpin {
          to {
            transform: rotate(360deg);
          }
        }

        .register-footer {
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 5px;
          margin: 20px 0 0;
          color: #64748b;
          font-size: 11px;
        }

        .register-footer a {
          color: #2563eb;
          text-decoration: none;
          font-weight: 750;
        }

        .register-footer a:hover {
          text-decoration: underline;
        }

        .register-security {
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 5px;
          margin-top: 14px;
          color: #94a3b8;
          font-size: 9px;
        }

        @media (max-width: 850px) {
          .register-layout {
            grid-template-columns: 1fr;
            max-width: 600px;
          }

          .register-brand {
            padding: 30px;
          }

          .register-benefits {
            display: none;
          }

          .register-form-panel {
            max-height: none;
            padding: 35px 30px;
          }
        }

        @media (max-width: 550px) {
          .register-page {
            padding: 15px;
          }

          .register-brand {
            padding: 27px;
          }

          .register-brand h1 {
            font-size: 25px;
          }

          .register-form-panel {
            padding: 30px 22px;
          }

          .register-grid {
            grid-template-columns: 1fr;
          }

          .register-field-full {
            grid-column: auto;
          }
        }
      `}</style>


      <div className="register-layout">

        {/* BRAND PANEL */}
        <div className="register-brand">

          <div className="register-brand-content">

            <div>

              <div className="register-brand-icon">
                <ShieldCheck size={28} />
              </div>

              <div className="register-eyebrow">
                Decision Management Platform
              </div>

              <h1>
                Build better
                <br />
                decisions together.
              </h1>

              <p className="register-brand-description">
                Create an account to manage
                decisions, collaborate with
                experts, review alternatives,
                and maintain a complete
                decision history.
              </p>


              <div className="register-benefits">

                <div className="register-benefit">

                  <div className="register-benefit-icon">
                    <CheckCircle2 size={14} />
                  </div>

                  Structured decision management

                </div>


                <div className="register-benefit">

                  <div className="register-benefit-icon">
                    <ShieldCheck size={14} />
                  </div>

                  Secure role-based access

                </div>


                <div className="register-benefit">

                  <div className="register-benefit-icon">
                    <UserPlus size={14} />
                  </div>

                  Expert collaboration

                </div>

              </div>

            </div>

          </div>

        </div>


        {/* FORM PANEL */}
        <div className="register-form-panel">

          <div className="register-form-header">

            <h2>
              Create Account
            </h2>

            <p>
              Enter your details to create
              your Expert Decision Replay account.
            </p>

          </div>


          {/* ERROR */}
          {error && (
            <div className="register-alert register-alert-error">

              <AlertCircle size={16} />

              <div>

                <strong>
                  Registration failed
                </strong>

                <span>
                  {error}
                </span>

              </div>

            </div>
          )}


          {/* SUCCESS */}
          {success && (
            <div className="register-alert register-alert-success">

              <CheckCircle2 size={16} />

              <div>

                <strong>
                  Account created
                </strong>

                <span>
                  {success}
                </span>

              </div>

            </div>
          )}


          <form onSubmit={handleSubmit}>

            {/* ACCOUNT INFORMATION */}
            <div className="register-section">

              <div className="register-section-title">

                <div className="register-section-title-icon">
                  <UserRound size={14} />
                </div>

                Account Information

              </div>

            </div>


            <div className="register-grid">

              {/* FULL NAME */}
              <div className="register-field">

                <label htmlFor="full_name">
                  Full Name
                  <span className="register-required">
                    *
                  </span>
                </label>

                <div className="register-input-wrapper">

                  <UserRound
                    size={15}
                    className="register-input-icon"
                  />

                  <input
                    id="full_name"
                    name="full_name"
                    type="text"
                    className="register-input"
                    value={form.full_name}
                    onChange={handleChange}
                    placeholder="Enter your full name"
                    autoComplete="name"
                    disabled={loading}
                    required
                  />

                </div>

              </div>


              {/* EMAIL */}
              <div className="register-field">

                <label htmlFor="email">
                  Email
                  <span className="register-required">
                    *
                  </span>
                </label>

                <div className="register-input-wrapper">

                  <Mail
                    size={15}
                    className="register-input-icon"
                  />

                  <input
                    id="email"
                    name="email"
                    type="email"
                    className="register-input"
                    value={form.email}
                    onChange={handleChange}
                    placeholder="Enter your email"
                    autoComplete="email"
                    disabled={loading}
                    required
                  />

                </div>

              </div>


              {/* PASSWORD */}
              <div className="register-field">

                <label htmlFor="password">
                  Password
                  <span className="register-required">
                    *
                  </span>
                </label>

                <div className="register-input-wrapper">

                  <LockKeyhole
                    size={15}
                    className="register-input-icon"
                  />

                  <input
                    id="password"
                    name="password"
                    type="password"
                    className="register-input"
                    value={form.password}
                    onChange={handleChange}
                    placeholder="Minimum 8 characters"
                    autoComplete="new-password"
                    disabled={loading}
                    required
                  />

                </div>

              </div>


              {/* CONFIRM PASSWORD */}
              <div className="register-field">

                <label htmlFor="confirm_password">
                  Confirm Password
                  <span className="register-required">
                    *
                  </span>
                </label>

                <div className="register-input-wrapper">

                  <LockKeyhole
                    size={15}
                    className="register-input-icon"
                  />

                  <input
                    id="confirm_password"
                    name="confirm_password"
                    type="password"
                    className="register-input"
                    value={form.confirm_password}
                    onChange={handleChange}
                    placeholder="Re-enter your password"
                    autoComplete="new-password"
                    disabled={loading}
                    required
                  />

                </div>

              </div>


              {/* ROLE */}
              <div className="register-field register-field-full">

                <label htmlFor="role">
                  Role
                  <span className="register-required">
                    *
                  </span>
                </label>

                <select
                  id="role"
                  name="role"
                  className="register-select"
                  value={form.role}
                  onChange={handleChange}
                  disabled={loading}
                  required
                >

                  {roles.map(
                    (role) => (
                      <option
                        key={role}
                        value={role}
                      >
                        {role}
                      </option>
                    )
                  )}

                </select>

              </div>

            </div>


            {/* ADDITIONAL INFORMATION */}
            <div className="register-section">

              <div className="register-section-title">

                <div className="register-section-title-icon">
                  <Building2 size={14} />
                </div>

                Additional Information

              </div>

            </div>


            <div className="register-grid">

              {/* EMPLOYEE ID */}
              <div className="register-field">

                <label htmlFor="employee_id">
                  Employee ID
                </label>

                <div className="register-input-wrapper">

                  <IdCard
                    size={15}
                    className="register-input-icon"
                  />

                  <input
                    id="employee_id"
                    name="employee_id"
                    type="text"
                    className="register-input"
                    value={form.employee_id}
                    onChange={handleChange}
                    placeholder="Optional"
                    disabled={loading}
                  />

                </div>

              </div>


              {/* DEPARTMENT */}
              <div className="register-field">

                <label htmlFor="department">
                  Department
                </label>

                <div className="register-input-wrapper">

                  <Building2
                    size={15}
                    className="register-input-icon"
                  />

                  <input
                    id="department"
                    name="department"
                    type="text"
                    className="register-input"
                    value={form.department}
                    onChange={handleChange}
                    placeholder="Optional"
                    disabled={loading}
                  />

                </div>

              </div>


              {/* DESIGNATION */}
              <div className="register-field">

                <label htmlFor="designation">
                  Designation
                </label>

                <div className="register-input-wrapper">

                  <UserRound
                    size={15}
                    className="register-input-icon"
                  />

                  <input
                    id="designation"
                    name="designation"
                    type="text"
                    className="register-input"
                    value={form.designation}
                    onChange={handleChange}
                    placeholder="Optional"
                    disabled={loading}
                  />

                </div>

              </div>


              {/* PHONE */}
              <div className="register-field">

                <label htmlFor="phone_number">
                  Phone Number
                </label>

                <div className="register-input-wrapper">

                  <Phone
                    size={15}
                    className="register-input-icon"
                  />

                  <input
                    id="phone_number"
                    name="phone_number"
                    type="tel"
                    className="register-input"
                    value={form.phone_number}
                    onChange={handleChange}
                    placeholder="Optional"
                    autoComplete="tel"
                    disabled={loading}
                  />

                </div>

              </div>

            </div>


            {/* SUBMIT */}
            <button
              type="submit"
              className="register-submit"
              disabled={loading}
            >

              {loading ? (
                <>
                  <span className="register-spinner" />
                  Creating Account...
                </>
              ) : (
                <>
                  <UserPlus size={15} />
                  Create Account
                  <ArrowRight size={14} />
                </>
              )}

            </button>

          </form>


          {/* FOOTER */}
          <p className="register-footer">

            Already have an account?

            <Link to="/login">
              Sign in
            </Link>

          </p>


          <div className="register-security">

            <LockKeyhole size={10} />

            Secure account registration

          </div>

        </div>

      </div>

    </div>
  );
}


export default Register;