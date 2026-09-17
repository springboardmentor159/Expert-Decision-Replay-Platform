import { useEffect, useState } from "react";
import api from "../services/api";

function UserManagement() {
  const [users, setUsers] = useState([]);
  const [search, setSearch] = useState("");
  const [roleFilter, setRoleFilter] = useState("All");

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

  const loadUsers = async () => {
    try {
      setLoading(true);
      setError("");

      const response = await api.get("/users");
      setUsers(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to load users");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadUsers();
  }, []);

  const handleChange = (e) => {
    setForm({
      ...form,
      [e.target.name]: e.target.value,
    });
  };

  const openAddForm = () => {
    setEditingUser(null);
    setForm(emptyForm);
    setError("");
    setSuccess("");
    setShowForm(true);
  };

  const openEditForm = (user) => {
    setEditingUser(user);

    setForm({
      full_name: user.full_name || "",
      email: user.email || "",
      role: user.role || "Employee",
      password: "",
      employee_id: user.employee_id || "",
      department: user.department || "",
      designation: user.designation || "",
      phone_number: user.phone_number || "",
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
        await api.put(`/users/${editingUser.id}`, {
          full_name: form.full_name,
          email: form.email,
          role: form.role,
          employee_id: form.employee_id,
          department: form.department,
          designation: form.designation,
          phone_number: form.phone_number,
        });

        setSuccess("User updated successfully");
      } else {
        await api.post("/users", form);

        setSuccess("User created successfully");
      }

      await loadUsers();
      closeForm();
    } catch (err) {
      setError(err.response?.data?.detail || "Operation failed");
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (userId) => {
    const confirmed = window.confirm(
      "Are you sure you want to delete this user?"
    );

    if (!confirmed) return;

    try {
      setError("");
      setSuccess("");

      await api.delete(`/users/${userId}`);

      setSuccess("User deleted successfully");
      await loadUsers();
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to delete user");
    }
  };

  const filteredUsers = users.filter((user) => {
    const searchText = search.toLowerCase();

    const matchesSearch =
      user.full_name?.toLowerCase().includes(searchText) ||
      user.email?.toLowerCase().includes(searchText) ||
      user.employee_id?.toLowerCase().includes(searchText) ||
      user.department?.toLowerCase().includes(searchText);

    const matchesRole =
      roleFilter === "All" || user.role === roleFilter;

    return matchesSearch && matchesRole;
  });

  return (
    <div className="page-container">

      <div className="page-header">
        <div>
          <h1>User Management</h1>
          <p>Manage platform users, roles and employee information.</p>
        </div>

        <button className="primary-btn" onClick={openAddForm}>
          + Add User
        </button>
      </div>

      {error && <div className="error-message">{error}</div>}
      {success && <div className="success-message">{success}</div>}

      <div className="filter-bar">

        <input
          type="text"
          placeholder="Search users..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />

        <select
          value={roleFilter}
          onChange={(e) => setRoleFilter(e.target.value)}
        >
          <option value="All">All Roles</option>
          <option value="Employee">Employee</option>
          <option value="Reviewer">Reviewer</option>
          <option value="Manager">Manager</option>
          <option value="HR">HR</option>
          <option value="Administrator">Administrator</option>
        </select>

      </div>

      {showForm && (
        <div className="form-card">

          <div className="form-card-header">
            <h2>
              {editingUser ? "Edit User" : "Create New User"}
            </h2>

            <button
              className="secondary-btn"
              onClick={closeForm}
            >
              Cancel
            </button>
          </div>

          <form onSubmit={handleSubmit}>

            <div className="form-grid">

              <input
                name="full_name"
                placeholder="Full Name"
                value={form.full_name}
                onChange={handleChange}
                required
              />

              <input
                name="email"
                type="email"
                placeholder="Email"
                value={form.email}
                onChange={handleChange}
                required
              />

              <select
                name="role"
                value={form.role}
                onChange={handleChange}
                required
              >
                <option value="Employee">Employee</option>
                <option value="Reviewer">Reviewer</option>
                <option value="Manager">Manager</option>
                <option value="HR">HR</option>
                <option value="Administrator">Administrator</option>
              </select>

              {!editingUser && (
                <input
                  name="password"
                  type="password"
                  placeholder="Password"
                  value={form.password}
                  onChange={handleChange}
                  required
                />
              )}

              <input
                name="employee_id"
                placeholder="Employee ID"
                value={form.employee_id}
                onChange={handleChange}
                required
              />

              <input
                name="department"
                placeholder="Department"
                value={form.department}
                onChange={handleChange}
                required
              />

              <input
                name="designation"
                placeholder="Designation"
                value={form.designation}
                onChange={handleChange}
                required
              />

              <input
                name="phone_number"
                placeholder="Phone Number"
                value={form.phone_number}
                onChange={handleChange}
                required
              />

            </div>

            <button
              type="submit"
              className="primary-btn"
              disabled={saving}
            >
              {saving
                ? "Saving..."
                : editingUser
                ? "Update User"
                : "Create User"}
            </button>

          </form>

        </div>
      )}

      <div className="table-card">

        {loading ? (
          <div className="loading-state">
            Loading users...
          </div>
        ) : filteredUsers.length === 0 ? (
          <div className="empty-state">
            No users found.
          </div>
        ) : (
          <div className="table-wrapper">

            <table>

              <thead>
                <tr>
                  <th>Name</th>
                  <th>Email</th>
                  <th>Employee ID</th>
                  <th>Role</th>
                  <th>Department</th>
                  <th>Designation</th>
                  <th>Actions</th>
                </tr>
              </thead>

              <tbody>

                {filteredUsers.map((user) => (
                  <tr key={user.id}>

                    <td>{user.full_name}</td>

                    <td>{user.email}</td>

                    <td>{user.employee_id}</td>

                    <td>
                      <span className="role-badge">
                        {user.role}
                      </span>
                    </td>

                    <td>{user.department}</td>

                    <td>{user.designation}</td>

                    <td>
                      <button
                        className="edit-btn"
                        onClick={() => openEditForm(user)}
                      >
                        Edit
                      </button>

                      <button
                        className="delete-btn"
                        onClick={() => handleDelete(user.id)}
                      >
                        Delete
                      </button>
                    </td>

                  </tr>
                ))}

              </tbody>

            </table>

          </div>
        )}

      </div>

    </div>
  );
}

export default UserManagement;