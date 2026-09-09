import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { registerUser } from "../../api/auth";
import Input from "../../components/ui/Input";
import Select from "../../components/ui/Select";
import Button from "../../components/ui/Button";
import Alert from "../../components/ui/Alert";
import { ROLES } from "../../utils/roles";

const EMPTY_FORM = {
  full_name: "",
  email: "",
  password: "",
  confirm_password: "",
  role: "",
  employee_id: "",
  department: "",
  designation: "",
  phone_number: "",
};

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export default function Register() {
  const navigate = useNavigate();
  const [form, setForm] = useState(EMPTY_FORM);
  const [errors, setErrors] = useState({});
  const [serverError, setServerError] = useState("");
  const [success, setSuccess] = useState(false);
  const [loading, setLoading] = useState(false);

  function update(field, value) {
    setForm((f) => ({ ...f, [field]: value }));
  }

  function validate() {
    const next = {};
    if (!form.full_name.trim()) next.full_name = "Full name is required.";
    if (!form.email.trim()) next.email = "Email is required.";
    else if (!EMAIL_RE.test(form.email)) next.email = "Enter a valid email address.";
    if (!form.role) next.role = "Select a role.";
    if (!form.password) next.password = "Password is required.";
    else if (form.password.length < 8) next.password = "Password must be at least 8 characters.";
    if (form.confirm_password !== form.password) next.confirm_password = "Passwords do not match.";
    if (!form.employee_id.trim()) next.employee_id = "Employee ID is required.";
    if (!form.department.trim()) next.department = "Department is required.";
    if (!form.designation.trim()) next.designation = "Designation is required.";
    if (!form.phone_number.trim()) next.phone_number = "Phone number is required.";
    setErrors(next);
    return Object.keys(next).length === 0;
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setServerError("");
    if (!validate()) return;

    setLoading(true);
    try {
      const { confirm_password, ...payload } = form;
      void confirm_password;
      await registerUser(payload);
      setSuccess(true);
      setTimeout(() => navigate("/login"), 1200);
    } catch (err) {
      setServerError(err.message || "Registration failed. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="auth-page">
      <form className="auth-card auth-card-wide" onSubmit={handleSubmit} noValidate>
        <h1>Create an account</h1>
        <p className="auth-subtitle">Expert Decision Replay Platform</p>

        <Alert type="error">{serverError}</Alert>
        <Alert type="success">{success ? "Account created! Redirecting to login…" : ""}</Alert>

        <div className="form-grid">
          <Input
            label="Full Name"
            name="full_name"
            required
            value={form.full_name}
            onChange={(e) => update("full_name", e.target.value)}
            error={errors.full_name}
          />
          <Input
            label="Email"
            type="email"
            name="email"
            required
            value={form.email}
            onChange={(e) => update("email", e.target.value)}
            error={errors.email}
          />
          <Select
            label="Role"
            name="role"
            required
            placeholder="Select role"
            options={Object.values(ROLES)}
            value={form.role}
            onChange={(e) => update("role", e.target.value)}
            error={errors.role}
          />
          <Input
            label="Employee ID"
            name="employee_id"
            required
            value={form.employee_id}
            onChange={(e) => update("employee_id", e.target.value)}
            error={errors.employee_id}
          />
          <Input
            label="Department"
            name="department"
            required
            value={form.department}
            onChange={(e) => update("department", e.target.value)}
            error={errors.department}
          />
          <Input
            label="Designation"
            name="designation"
            required
            value={form.designation}
            onChange={(e) => update("designation", e.target.value)}
            error={errors.designation}
          />
          <Input
            label="Phone Number"
            name="phone_number"
            required
            value={form.phone_number}
            onChange={(e) => update("phone_number", e.target.value)}
            error={errors.phone_number}
          />
          <div />
          <Input
            label="Password"
            type="password"
            name="password"
            required
            value={form.password}
            onChange={(e) => update("password", e.target.value)}
            error={errors.password}
            hint="At least 8 characters."
            autoComplete="new-password"
          />
          <Input
            label="Confirm Password"
            type="password"
            name="confirm_password"
            required
            value={form.confirm_password}
            onChange={(e) => update("confirm_password", e.target.value)}
            error={errors.confirm_password}
            autoComplete="new-password"
          />
        </div>

        <Button type="submit" loading={loading} className="btn-block">
          Register
        </Button>

        <p className="auth-footer">
          Already have an account? <Link to="/login">Log in</Link>
        </p>
      </form>
    </div>
  );
}
