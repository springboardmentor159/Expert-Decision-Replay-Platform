import { useState } from "react";
import { useNavigate } from "react-router-dom";
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
    <div>
      <h1>Expert Decision Replay Platform</h1>

      <h2>Create Account</h2>

      <form onSubmit={handleSubmit}>
        <label>Full Name</label>
        <br />
        <input
          name="full_name"
          value={form.full_name}
          onChange={handleChange}
          placeholder="Enter full name"
        />

        <br />
        <br />

        <label>Email</label>
        <br />
        <input
          type="email"
          name="email"
          value={form.email}
          onChange={handleChange}
          placeholder="Enter email"
        />

        <br />
        <br />

        <label>Password</label>
        <br />
        <input
          type="password"
          name="password"
          value={form.password}
          onChange={handleChange}
          placeholder="Enter password"
        />

        <br />
        <br />

        <label>Role</label>
        <br />
        <select
          name="role"
          value={form.role}
          onChange={handleChange}
        >
          <option value="Employee">Employee</option>
          <option value="Reviewer">Reviewer</option>
          <option value="Manager">Manager</option>
          <option value="Administrator">Administrator</option>
        </select>

        <br />
        <br />

        <label>Employee ID</label>
        <br />
        <input
          name="employee_id"
          value={form.employee_id}
          onChange={handleChange}
          placeholder="Enter employee ID"
        />

        <br />
        <br />

        <label>Department</label>
        <br />
        <input
          name="department"
          value={form.department}
          onChange={handleChange}
          placeholder="Enter department"
        />

        <br />
        <br />

        <label>Designation</label>
        <br />
        <input
          name="designation"
          value={form.designation}
          onChange={handleChange}
          placeholder="Enter designation"
        />

        <br />
        <br />

        <label>Phone Number</label>
        <br />
        <input
          name="phone_number"
          value={form.phone_number}
          onChange={handleChange}
          placeholder="Enter phone number"
        />

        <br />
        <br />

        {error && <p>{error}</p>}
        {success && <p>{success}</p>}

        <button type="submit" disabled={loading}>
          {loading ? "Registering..." : "Register"}
        </button>
      </form>

      <br />

      <button onClick={() => navigate("/login")}>
        Back to Login
      </button>
    </div>
  );
}

export default Register;