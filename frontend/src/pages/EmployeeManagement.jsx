import { useEffect, useState } from "react";
import api from "../services/api";

function EmployeeManagement() {
  const [users, setUsers] = useState([]);
  const [search, setSearch] = useState("");
  const [roleFilter, setRoleFilter] = useState("Employee");

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const [showForm, setShowForm] = useState(false);
  const [editingUser, setEditingUser] = useState(null);

  const emptyForm = {
    full_name: "",
    email: "",
    role: "Employee",
    password: "",
    employee_id: "",
    department: "",
    designation: "",
    phone_number: "",
  };

  const [form, setForm] = useState(emptyForm);

  useEffect(() => {
    loadUsers();
  }, []);

  const loadUsers = async () => {
    try {
      setLoading(true);
      setError("");

      const response = await api.get("/users");

      const data = Array.isArray(response.data)
        ? response.data
        : response.data.data || [];

      setUsers(data);
    } catch (err) {
      console.error("Employee Management error:", err);

      setError(
        err.response?.data?.detail ||
          "Unable to load employees."
      );
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    setForm({
      ...form,
      [e.target.name]: e.target.value,
    });
  };

  const openCreateForm = () => {
    setEditingUser(null);
    setForm(emptyForm);
    setError("");
    setSuccess("");
    setShowForm(true);
  };

  const openEditForm = (employee) => {
    setEditingUser(employee);

    setForm({
      full_name: employee.full_name || "",
      email: employee.email || "",
      role: employee.role || "Employee",
      password: "",
      employee_id: employee.employee_id || "",
      department: employee.department || "",
      designation: employee.designation || "",
      phone_number: employee.phone_number || "",
    });

    setError("");
    setSuccess("");
    setShowForm(true);
  };

  const closeForm = () => {
    setShowForm(false);
    setEditingUser(null);
    setForm(emptyForm);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      setSaving(true);
      setError("");
      setSuccess("");

      if (editingUser) {
        const updateData = {
          full_name: form.full_name,
          email: form.email,
          role: form.role,
          employee_id: form.employee_id,
          department: form.department,
          designation: form.designation,
          phone_number: form.phone_number,
        };

        await api.put(
          `/users/${editingUser.id}`,
          updateData
        );

        setSuccess("Employee updated successfully.");
      } else {
        await api.post("/users", form);

        setSuccess("Employee created successfully.");
      }

      await loadUsers();
      closeForm();

      setTimeout(() => {
        setSuccess("");
      }, 3000);
    } catch (err) {
      console.error("Save employee error:", err);

      setError(
        err.response?.data?.detail ||
          "Unable to save employee."
      );
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (employee) => {
    const confirmed = window.confirm(
      `Are you sure you want to delete ${employee.full_name}?`
    );

    if (!confirmed) return;

    try {
      setError("");
      setSuccess("");

      await api.delete(`/users/${employee.id}`);

      setSuccess("Employee deleted successfully.");

      await loadUsers();

      setTimeout(() => {
        setSuccess("");
      }, 3000);
    } catch (err) {
      console.error("Delete employee error:", err);

      setError(
        err.response?.data?.detail ||
          "Unable to delete employee."
      );
    }
  };

  const filteredUsers = users.filter((user) => {
    const matchesSearch =
      user.full_name
        ?.toLowerCase()
        .includes(search.toLowerCase()) ||
      user.email
        ?.toLowerCase()
        .includes(search.toLowerCase()) ||
      user.employee_id
        ?.toLowerCase()
        .includes(search.toLowerCase()) ||
      user.department
        ?.toLowerCase()
        .includes(search.toLowerCase());

    const matchesRole =
      roleFilter === "All" ||
      user.role === roleFilter;

    return matchesSearch && matchesRole;
  });

  const employeeCount = users.filter(
    (user) => user.role === "Employee"
  ).length;

  const managerCount = users.filter(
    (user) => user.role === "Manager"
  ).length;

  const reviewerCount = users.filter(
    (user) => user.role === "Reviewer"
  ).length;

  if (loading) {
    return (
      <div className="employee-management-page">
        <div className="page-header">
          <div>
            <h1>Employee Management</h1>
            <p>Manage workforce accounts and employee information.</p>
          </div>
        </div>

        <div className="employee-loading">
          Loading employee information...
        </div>
      </div>
    );
  }

  return (
    <div className="employee-management-page">

      {/* HEADER */}
      <div className="employee-page-header">
        <div>
          <span className="employee-eyebrow">
            HR MANAGEMENT
          </span>

          <h1>Employee Management</h1>

          <p>
            Manage employee accounts, roles and organizational information.
          </p>
        </div>

        <button
          className="employee-primary-button"
          onClick={openCreateForm}
        >
          + Add Employee
        </button>
      </div>

      {/* ALERTS */}
      {error && (
        <div className="employee-alert employee-alert-error">
          {error}
        </div>
      )}

      {success && (
        <div className="employee-alert employee-alert-success">
          {success}
        </div>
      )}

      {/* STATISTICS */}
      <div className="employee-stats">

        <div className="employee-stat-card">
          <span>Total Employees</span>
          <strong>{employeeCount}</strong>
          <small>Active employee accounts</small>
        </div>

        <div className="employee-stat-card">
          <span>Managers</span>
          <strong>{managerCount}</strong>
          <small>Management accounts</small>
        </div>

        <div className="employee-stat-card">
          <span>Reviewers</span>
          <strong>{reviewerCount}</strong>
          <small>Review accounts</small>
        </div>

        <div className="employee-stat-card">
          <span>Total Users</span>
          <strong>{users.length}</strong>
          <small>Registered platform users</small>
        </div>

      </div>

      {/* CONTROLS */}
      <div className="employee-toolbar">

        <div className="employee-search">
          <span>⌕</span>

          <input
            type="text"
            placeholder="Search by name, email, ID or department..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>

        <select
          value={roleFilter}
          onChange={(e) => setRoleFilter(e.target.value)}
          className="employee-filter"
        >
          <option value="Employee">Employees</option>
          <option value="All">All Roles</option>
          <option value="Manager">Managers</option>
          <option value="Reviewer">Reviewers</option>
          <option value="HR">HR</option>
          <option value="Administrator">Administrators</option>
        </select>

        <button
          className="employee-refresh-button"
          onClick={loadUsers}
        >
          Refresh
        </button>

      </div>

      {/* TABLE */}
      <div className="employee-table-card">

        <div className="employee-table-header">
          <div>
            <h2>Employee Directory</h2>
            <p>
              {filteredUsers.length} user
              {filteredUsers.length !== 1 ? "s" : ""} displayed
            </p>
          </div>
        </div>

        {filteredUsers.length === 0 ? (
          <div className="employee-empty-state">
            <div className="employee-empty-icon">⌕</div>

            <h3>No employees found</h3>

            <p>
              Try changing your search or role filter.
            </p>
          </div>
        ) : (
          <div className="employee-table-wrapper">

            <table className="employee-table">

              <thead>
                <tr>
                  <th>Employee</th>
                  <th>Employee ID</th>
                  <th>Department</th>
                  <th>Designation</th>
                  <th>Role</th>
                  <th>Contact</th>
                  <th>Actions</th>
                </tr>
              </thead>

              <tbody>
                {filteredUsers.map((employee) => (
                  <tr key={employee.id}>

                    <td>
                      <div className="employee-name-cell">
                        <div className="employee-avatar">
                          {employee.full_name
                            ?.charAt(0)
                            .toUpperCase()}
                        </div>

                        <div>
                          <strong>
                            {employee.full_name}
                          </strong>

                          <span>
                            {employee.email}
                          </span>
                        </div>
                      </div>
                    </td>

                    <td>
                      {employee.employee_id}
                    </td>

                    <td>
                      {employee.department}
                    </td>

                    <td>
                      {employee.designation}
                    </td>

                    <td>
                      <span
                        className={`employee-role employee-role-${employee.role
                          ?.toLowerCase()
                          .replace(/\s+/g, "-")}`}
                      >
                        {employee.role}
                      </span>
                    </td>

                    <td>
                      {employee.phone_number}
                    </td>

                    <td>
                      <div className="employee-actions">

                        <button
                          className="employee-edit-button"
                          onClick={() =>
                            openEditForm(employee)
                          }
                        >
                          Edit
                        </button>

                        <button
                          className="employee-delete-button"
                          onClick={() =>
                            handleDelete(employee)
                          }
                        >
                          Delete
                        </button>

                      </div>
                    </td>

                  </tr>
                ))}
              </tbody>

            </table>

          </div>
        )}

      </div>

      {/* FORM MODAL */}
      {showForm && (
        <div className="employee-modal-overlay">

          <div className="employee-modal">

            <div className="employee-modal-header">

              <div>
                <span className="employee-eyebrow">
                  {editingUser
                    ? "EDIT ACCOUNT"
                    : "NEW ACCOUNT"}
                </span>

                <h2>
                  {editingUser
                    ? "Edit Employee"
                    : "Add Employee"}
                </h2>
              </div>

              <button
                className="employee-close-button"
                onClick={closeForm}
              >
                ×
              </button>

            </div>

            <form onSubmit={handleSubmit}>

              <div className="employee-form-section">
                <h3>Personal Information</h3>

                <div className="employee-form-grid">

                  <div className="employee-form-group">
                    <label>Full Name</label>
                    <input
                      name="full_name"
                      value={form.full_name}
                      onChange={handleChange}
                      required
                    />
                  </div>

                  <div className="employee-form-group">
                    <label>Email</label>
                    <input
                      type="email"
                      name="email"
                      value={form.email}
                      onChange={handleChange}
                      required
                    />
                  </div>

                  <div className="employee-form-group">
                    <label>Employee ID</label>
                    <input
                      name="employee_id"
                      value={form.employee_id}
                      onChange={handleChange}
                      required
                    />
                  </div>

                  <div className="employee-form-group">
                    <label>Phone Number</label>
                    <input
                      name="phone_number"
                      value={form.phone_number}
                      onChange={handleChange}
                      required
                    />
                  </div>

                </div>
              </div>

              <div className="employee-form-section">
                <h3>Organization</h3>

                <div className="employee-form-grid">

                  <div className="employee-form-group">
                    <label>Department</label>
                    <input
                      name="department"
                      value={form.department}
                      onChange={handleChange}
                      required
                    />
                  </div>

                  <div className="employee-form-group">
                    <label>Designation</label>
                    <input
                      name="designation"
                      value={form.designation}
                      onChange={handleChange}
                      required
                    />
                  </div>

                  <div className="employee-form-group">
                    <label>Role</label>

                    <select
                      name="role"
                      value={form.role}
                      onChange={handleChange}
                      required
                    >
                      <option value="Employee">
                        Employee
                      </option>
                      <option value="Reviewer">
                        Reviewer
                      </option>
                      <option value="Manager">
                        Manager
                      </option>
                      <option value="HR">
                        HR
                      </option>
                      <option value="Administrator">
                        Administrator
                      </option>
                    </select>
                  </div>

                  {!editingUser && (
                    <div className="employee-form-group">
                      <label>Password</label>

                      <input
                        type="password"
                        name="password"
                        value={form.password}
                        onChange={handleChange}
                        required
                        minLength={6}
                        placeholder="Initial password"
                      />
                    </div>
                  )}

                </div>
              </div>

              <div className="employee-modal-footer">

                <button
                  type="button"
                  className="employee-cancel-button"
                  onClick={closeForm}
                >
                  Cancel
                </button>

                <button
                  type="submit"
                  className="employee-primary-button"
                  disabled={saving}
                >
                  {saving
                    ? "Saving..."
                    : editingUser
                    ? "Save Changes"
                    : "Create Employee"}
                </button>

              </div>

            </form>

          </div>
        </div>
      )}

    </div>
  );
}

export default EmployeeManagement;