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
        full_name: formData.full_name,
        email: formData.email,
        password: formData.password,
        role: formData.role,
        employee_id: formData.employee_id || null,
        department: formData.department || null,
        designation: formData.designation || null,
        phone_number: formData.phone_number || null,
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
    <div>
      <h1>Expert Decision Replay Platform</h1>

      <h2>Register</h2>

      {error && <p>{error}</p>}
      {success && <p>{success}</p>}

      <form onSubmit={handleSubmit}>
        <div>
          <label>Full Name</label>
          <br />
          <input
            name="full_name"
            value={formData.full_name}
            onChange={handleChange}
            placeholder="Enter full name"
          />
        </div>

        <br />

        <div>
          <label>Email</label>
          <br />
          <input
            type="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            placeholder="Enter email"
          />
        </div>

        <br />

        <div>
          <label>Password</label>
          <br />
          <input
            type="password"
            name="password"
            value={formData.password}
            onChange={handleChange}
            placeholder="Enter password"
          />
        </div>

        <br />

        <div>
          <label>Confirm Password</label>
          <br />
          <input
            type="password"
            name="confirm_password"
            value={formData.confirm_password}
            onChange={handleChange}
            placeholder="Confirm password"
          />
        </div>

        <br />

        <div>
          <label>Role</label>
          <br />
          <select
            name="role"
            value={formData.role}
            onChange={handleChange}
          >
            <option value="Employee">Employee</option>
            <option value="Reviewer">Reviewer</option>
            <option value="Manager">Manager</option>
            <option value="Administrator">Administrator</option>
          </select>
        </div>

        <br />

        <div>
          <label>Employee ID</label>
          <br />
          <input
            name="employee_id"
            value={formData.employee_id}
            onChange={handleChange}
          />
        </div>

        <br />

        <div>
          <label>Department</label>
          <br />
          <input
            name="department"
            value={formData.department}
            onChange={handleChange}
          />
        </div>

        <br />

        <div>
          <label>Designation</label>
          <br />
          <input
            name="designation"
            value={formData.designation}
            onChange={handleChange}
          />
        </div>

        <br />

        <div>
          <label>Phone Number</label>
          <br />
          <input
            name="phone_number"
            value={formData.phone_number}
            onChange={handleChange}
          />
        </div>

        <br />

        <button type="submit" disabled={loading}>
          {loading ? "Registering..." : "Register"}
        </button>
      </form>

      <br />

      <button onClick={() => navigate("/login")}>
        Already have an account? Login
      </button>
    </div>
  );
};

export default Register;