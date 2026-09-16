import { useEffect, useMemo, useState } from "react";
import {
  Edit3,
  Mail,
  Phone,
  Plus,
  Search,
  Shield,
  Trash2,
  UserPlus,
  Users,
  X,
} from "lucide-react";

import {
  createUser,
  deleteUser,
  getUsers,
  updateUser,
} from "../api/userApi";


const ROLES = [
  "Employee",
  "Reviewer",
  "Manager",
  "Administrator",
];


const EMPTY_FORM = {
  full_name: "",
  email: "",
  role: "Employee",
  employee_id: "",
  department: "",
  designation: "",
  phone_number: "",
  password: "",
};


function getErrorMessage(
  error,
  fallback = "Something went wrong."
) {
  const status = error?.response?.status;
  const detail = error?.response?.data?.detail;

  if (status === 400) {
    return typeof detail === "string"
      ? detail
      : "Invalid request. Please check the entered information.";
  }

  if (status === 401) {
    return "Your session has expired. Please log in again.";
  }

  if (status === 403) {
    return "You do not have permission to perform this action.";
  }

  if (status === 404) {
    return "The requested user was not found.";
  }

  if (status === 422) {
    if (Array.isArray(detail)) {
      return detail
        .map((item) =>
          item?.msg
            ? item.msg
            : "Invalid input."
        )
        .join(" ");
    }

    return typeof detail === "string"
      ? detail
      : "Please check the entered information.";
  }

  if (status === 500) {
    return "The server encountered an error. Please try again.";
  }

  if (
    error?.code === "ERR_NETWORK" ||
    !error?.response
  ) {
    return "Unable to connect to the backend server.";
  }

  return (
    error?.message ||
    fallback
  );
}


function normalizeUsers(data) {
  if (Array.isArray(data)) {
    return data;
  }

  if (Array.isArray(data?.users)) {
    return data.users;
  }

  if (Array.isArray(data?.items)) {
    return data.items;
  }

  return [];
}


function getRoleClass(role) {
  switch (role) {
    case "Administrator":
      return "role-administrator";

    case "Manager":
      return "role-manager";

    case "Reviewer":
      return "role-reviewer";

    default:
      return "role-employee";
  }
}


export default function UserManagement() {
  const [users, setUsers] = useState([]);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [searchTerm, setSearchTerm] = useState("");
  const [roleFilter, setRoleFilter] =
    useState("All Roles");

  const [showForm, setShowForm] = useState(false);
  const [editingUser, setEditingUser] =
    useState(null);

  const [form, setForm] =
    useState(EMPTY_FORM);

  const [saving, setSaving] = useState(false);
  const [deletingId, setDeletingId] =
    useState(null);

  const [formError, setFormError] =
    useState("");

  const [successMessage, setSuccessMessage] =
    useState("");


  async function loadUsers() {
    try {
      setLoading(true);
      setError("");

      const data = await getUsers();

      setUsers(normalizeUsers(data));
    } catch (err) {
      setError(
        getErrorMessage(
          err,
          "Unable to load users."
        )
      );
    } finally {
      setLoading(false);
    }
  }


  useEffect(() => {
    loadUsers();
  }, []);


  const filteredUsers = useMemo(() => {
    const query =
      searchTerm.trim().toLowerCase();

    return users.filter((user) => {
      const matchesSearch =
        !query ||
        [
          user.full_name,
          user.email,
          user.employee_id,
          user.department,
          user.designation,
          user.phone_number,
        ]
          .filter(Boolean)
          .some((value) =>
            String(value)
              .toLowerCase()
              .includes(query)
          );

      const matchesRole =
        roleFilter === "All Roles" ||
        user.role === roleFilter;

      return (
        matchesSearch &&
        matchesRole
      );
    });
  }, [
    users,
    searchTerm,
    roleFilter,
  ]);


  const stats = useMemo(
    () => ({
      total: users.length,

      employees: users.filter(
        (user) =>
          user.role === "Employee"
      ).length,

      reviewers: users.filter(
        (user) =>
          user.role === "Reviewer"
      ).length,

      managers: users.filter(
        (user) =>
          user.role === "Manager"
      ).length,

      administrators: users.filter(
        (user) =>
          user.role === "Administrator"
      ).length,
    }),
    [users]
  );


  function openCreateForm() {
    setEditingUser(null);
    setForm(EMPTY_FORM);
    setFormError("");
    setSuccessMessage("");
    setShowForm(true);
  }


  function openEditForm(user) {
    setEditingUser(user);

    setForm({
      full_name:
        user.full_name || "",

      email:
        user.email || "",

      role:
        user.role || "Employee",

      employee_id:
        user.employee_id || "",

      department:
        user.department || "",

      designation:
        user.designation || "",

      phone_number:
        user.phone_number || "",

      password: "",
    });

    setFormError("");
    setSuccessMessage("");
    setShowForm(true);
  }


  function closeForm() {
    if (saving) {
      return;
    }

    setShowForm(false);
    setEditingUser(null);
    setForm(EMPTY_FORM);
    setFormError("");
    setSuccessMessage("");
  }


  function handleChange(event) {
    const {
      name,
      value,
    } = event.target;

    setForm((previous) => ({
      ...previous,
      [name]: value,
    }));
  }


  function validateForm() {
    if (!form.full_name.trim()) {
      return "Full name is required.";
    }

    if (!form.email.trim()) {
      return "Email is required.";
    }

    if (!form.email.includes("@")) {
      return "Please enter a valid email address.";
    }

    if (!form.role) {
      return "Role is required.";
    }

    if (
      !editingUser &&
      !form.password.trim()
    ) {
      return "Password is required when creating a user.";
    }

    if (
      form.password &&
      form.password.length < 6
    ) {
      return "Password must contain at least 6 characters.";
    }

    return "";
  }


  async function handleSubmit(event) {
    event.preventDefault();

    const validationError =
      validateForm();

    if (validationError) {
      setFormError(validationError);
      return;
    }

    try {
      setSaving(true);
      setFormError("");
      setSuccessMessage("");

      const payload = {
        full_name:
          form.full_name.trim(),

        email:
          form.email.trim(),

        role:
          form.role,

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

      if (form.password.trim()) {
        payload.password =
          form.password.trim();
      }

      if (editingUser) {
        await updateUser(
          editingUser.id,
          payload
        );

        setSuccessMessage(
          "User updated successfully."
        );
      } else {
        await createUser(payload);

        setSuccessMessage(
          "User created successfully."
        );
      }

      await loadUsers();

      setTimeout(() => {
        setShowForm(false);
        setEditingUser(null);
        setForm(EMPTY_FORM);
        setSuccessMessage("");
      }, 700);

    } catch (err) {
      setFormError(
        getErrorMessage(
          err,
          "Unable to save user."
        )
      );
    } finally {
      setSaving(false);
    }
  }


  async function handleDelete(user) {
    const confirmed =
      window.confirm(
        `Are you sure you want to delete ${user.full_name}?`
      );

    if (!confirmed) {
      return;
    }

    try {
      setDeletingId(user.id);
      setError("");

      await deleteUser(user.id);

      setUsers((previous) =>
        previous.filter(
          (item) =>
            item.id !== user.id
        )
      );

      setSuccessMessage(
        "User deleted successfully."
      );

      setTimeout(() => {
        setSuccessMessage("");
      }, 2500);

    } catch (err) {
      setError(
        getErrorMessage(
          err,
          "Unable to delete user."
        )
      );
    } finally {
      setDeletingId(null);
    }
  }


  return (
    <div className="page-container user-management-page">

      {/* Header */}

      <div className="page-header user-page-header">

        <div>

          <div className="eyebrow">
            ADMINISTRATION
          </div>

          <h1>
            User Management
          </h1>

          <p>
            Manage users, roles, departments,
            and platform access.
          </p>

        </div>


        <button
          type="button"
          className="primary-button create-user-button"
          onClick={openCreateForm}
        >
          <Plus size={18} />
          Create User
        </button>

      </div>


      {/* Success */}

      {successMessage && (
        <div className="user-success">
          <Shield size={18} />
          {successMessage}
        </div>
      )}


      {/* Error */}

      {error && (
        <div className="error-state user-error">
          {error}
        </div>
      )}


      {/* Statistics */}

      <div className="user-stats-grid">

        <div className="user-stat-card">
          <div className="user-stat-icon total-icon">
            <Users size={21} />
          </div>

          <div>
            <span>Total Users</span>
            <strong>
              {stats.total}
            </strong>
          </div>
        </div>


        <div className="user-stat-card">
          <div className="user-stat-icon employee-icon">
            <Users size={21} />
          </div>

          <div>
            <span>Employees</span>
            <strong>
              {stats.employees}
            </strong>
          </div>
        </div>


        <div className="user-stat-card">
          <div className="user-stat-icon reviewer-icon">
            <Shield size={21} />
          </div>

          <div>
            <span>Reviewers</span>
            <strong>
              {stats.reviewers}
            </strong>
          </div>
        </div>


        <div className="user-stat-card">
          <div className="user-stat-icon manager-icon">
            <Shield size={21} />
          </div>

          <div>
            <span>Managers</span>
            <strong>
              {stats.managers}
            </strong>
          </div>
        </div>


        <div className="user-stat-card">
          <div className="user-stat-icon admin-icon">
            <Shield size={21} />
          </div>

          <div>
            <span>Administrators</span>
            <strong>
              {stats.administrators}
            </strong>
          </div>
        </div>

      </div>


      {/* Users */}

      <div className="users-card">

        <div className="users-card-header">

          <div>
            <h2>
              Platform Users
            </h2>

            <p>
              {filteredUsers.length} user
              {filteredUsers.length !== 1
                ? "s"
                : ""}{" "}
              displayed
            </p>
          </div>

        </div>


        {/* Filters */}

        <div className="user-filters">

          <div className="user-search">

            <Search size={18} />

            <input
              type="text"
              value={searchTerm}
              onChange={(event) =>
                setSearchTerm(
                  event.target.value
                )
              }
              placeholder="Search by name, email, ID, department..."
            />

            {searchTerm && (
              <button
                type="button"
                className="clear-search"
                onClick={() =>
                  setSearchTerm("")
                }
              >
                <X size={16} />
              </button>
            )}

          </div>


          <div className="role-filter">

            <Shield size={17} />

            <select
              value={roleFilter}
              onChange={(event) =>
                setRoleFilter(
                  event.target.value
                )
              }
            >
              <option value="All Roles">
                All Roles
              </option>

              {ROLES.map((role) => (
                <option
                  key={role}
                  value={role}
                >
                  {role}
                </option>
              ))}

            </select>

          </div>

        </div>


        {/* Loading */}

        {loading && (
          <div className="user-loading">
            Loading users...
          </div>
        )}


        {/* Empty */}

        {!loading &&
          filteredUsers.length === 0 && (
            <div className="user-empty">

              <div className="empty-user-icon">
                <Users size={28} />
              </div>

              <h3>
                No users found
              </h3>

              <p>
                Try changing your search or
                role filter.
              </p>

            </div>
          )}


        {/* Table */}

        {!loading &&
          filteredUsers.length > 0 && (
            <div className="users-table-wrapper">

              <table className="users-table">

                <thead>

                  <tr>
                    <th>ID</th>
                    <th>User</th>
                    <th>Email</th>
                    <th>Role</th>
                    <th>Employee ID</th>
                    <th>Department</th>
                    <th>Designation</th>
                    <th>Phone</th>
                    <th>Actions</th>
                  </tr>

                </thead>


                <tbody>

                  {filteredUsers.map(
                    (user) => (
                      <tr key={user.id}>

                        <td>
                          <span className="user-id">
                            #{user.id}
                          </span>
                        </td>


                        <td>
                          <div className="user-name-cell">

                            <div className="user-avatar">
                              {user.full_name
                                ?.charAt(0)
                                ?.toUpperCase() ||
                                "U"}
                            </div>

                            <strong>
                              {user.full_name ||
                                "Unnamed User"}
                            </strong>

                          </div>
                        </td>


                        <td>
                          <div className="email-cell">
                            <Mail size={14} />
                            <span>
                              {user.email}
                            </span>
                          </div>
                        </td>


                        <td>
                          <span
                            className={`role-badge ${getRoleClass(
                              user.role
                            )}`}
                          >
                            {user.role}
                          </span>
                        </td>


                        <td>
                          {user.employee_id || (
                            <span className="muted">
                              —
                            </span>
                          )}
                        </td>


                        <td>
                          {user.department || (
                            <span className="muted">
                              —
                            </span>
                          )}
                        </td>


                        <td>
                          {user.designation || (
                            <span className="muted">
                              —
                            </span>
                          )}
                        </td>


                        <td>
                          {user.phone_number ? (
                            <div className="phone-cell">
                              <Phone size={14} />
                              <span>
                                {user.phone_number}
                              </span>
                            </div>
                          ) : (
                            <span className="muted">
                              —
                            </span>
                          )}
                        </td>


                        <td>

                          <div className="user-actions">

                            <button
                              type="button"
                              className="table-action edit-action"
                              onClick={() =>
                                openEditForm(user)
                              }
                            >
                              <Edit3 size={15} />
                              Edit
                            </button>


                            <button
                              type="button"
                              className="table-action delete-action"
                              onClick={() =>
                                handleDelete(user)
                              }
                              disabled={
                                deletingId ===
                                user.id
                              }
                            >
                              <Trash2 size={15} />

                              {deletingId ===
                              user.id
                                ? "Deleting..."
                                : "Delete"}
                            </button>

                          </div>

                        </td>

                      </tr>
                    )
                  )}

                </tbody>

              </table>

            </div>
          )}

      </div>


      {/* Create / Edit Modal */}

      {showForm && (
        <div
          className="modal-overlay"
          onMouseDown={(event) => {
            if (
              event.target ===
              event.currentTarget
            ) {
              closeForm();
            }
          }}
        >

          <div className="user-modal">

            <div className="user-modal-header">

              <div className="modal-heading">

                <div className="modal-icon">
                  {editingUser ? (
                    <Edit3 size={21} />
                  ) : (
                    <UserPlus size={21} />
                  )}
                </div>

                <div>

                  <h2>
                    {editingUser
                      ? "Edit User"
                      : "Create User"}
                  </h2>

                  <p>
                    {editingUser
                      ? "Update user information and access."
                      : "Add a new user to the platform."}
                  </p>

                </div>

              </div>


              <button
                type="button"
                className="modal-close"
                onClick={closeForm}
                disabled={saving}
              >
                <X size={20} />
              </button>

            </div>


            <form
              onSubmit={handleSubmit}
              className="user-form"
            >

              {formError && (
                <div className="form-error">
                  {formError}
                </div>
              )}


              {successMessage && (
                <div className="form-success">
                  {successMessage}
                </div>
              )}


              <div className="form-grid">

                <div className="form-group">
                  <label>
                    Full Name
                    <span>*</span>
                  </label>

                  <input
                    name="full_name"
                    value={form.full_name}
                    onChange={handleChange}
                    placeholder="Enter full name"
                  />
                </div>


                <div className="form-group">
                  <label>
                    Email
                    <span>*</span>
                  </label>

                  <input
                    type="email"
                    name="email"
                    value={form.email}
                    onChange={handleChange}
                    placeholder="name@example.com"
                  />
                </div>


                <div className="form-group">
                  <label>
                    Role
                    <span>*</span>
                  </label>

                  <select
                    name="role"
                    value={form.role}
                    onChange={handleChange}
                  >
                    {ROLES.map(
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


                <div className="form-group">
                  <label>
                    Employee ID
                  </label>

                  <input
                    name="employee_id"
                    value={form.employee_id}
                    onChange={handleChange}
                    placeholder="e.g. E008"
                  />
                </div>


                <div className="form-group">
                  <label>
                    Department
                  </label>

                  <input
                    name="department"
                    value={form.department}
                    onChange={handleChange}
                    placeholder="e.g. Engineering"
                  />
                </div>


                <div className="form-group">
                  <label>
                    Designation
                  </label>

                  <input
                    name="designation"
                    value={form.designation}
                    onChange={handleChange}
                    placeholder="e.g. Software Engineer"
                  />
                </div>


                <div className="form-group">
                  <label>
                    Phone Number
                  </label>

                  <input
                    name="phone_number"
                    value={form.phone_number}
                    onChange={handleChange}
                    placeholder="Enter phone number"
                  />
                </div>


                <div className="form-group">
                  <label>
                    Password
                    {!editingUser && (
                      <span>*</span>
                    )}
                  </label>

                  <input
                    type="password"
                    name="password"
                    value={form.password}
                    onChange={handleChange}
                    placeholder={
                      editingUser
                        ? "Leave blank to keep current password"
                        : "Minimum 6 characters"
                    }
                  />
                </div>

              </div>


              <div className="modal-actions">

                <button
                  type="button"
                  className="secondary-button"
                  onClick={closeForm}
                  disabled={saving}
                >
                  Cancel
                </button>


                <button
                  type="submit"
                  className="primary-button"
                  disabled={saving}
                >
                  {saving ? (
                    "Saving..."
                  ) : (
                    <>
                      {editingUser ? (
                        <Edit3 size={17} />
                      ) : (
                        <UserPlus size={17} />
                      )}

                      {editingUser
                        ? "Update User"
                        : "Create User"}
                    </>
                  )}
                </button>

              </div>

            </form>

          </div>

        </div>
      )}


      <style>{`

        .user-management-page {
          padding-bottom: 40px;
        }

        .user-page-header {
          align-items: flex-end;
        }

        .eyebrow {
          color: #2563eb;
          font-size: 11px;
          font-weight: 700;
          letter-spacing: 0.12em;
          margin-bottom: 6px;
        }

        .create-user-button {
          display: inline-flex;
          align-items: center;
          gap: 7px;
          white-space: nowrap;
        }

        .user-success {
          display: flex;
          align-items: center;
          gap: 9px;
          padding: 12px 15px;
          margin-bottom: 18px;
          border-radius: 10px;
          background: #f0fdf4;
          border: 1px solid #bbf7d0;
          color: #15803d;
          font-size: 13px;
          font-weight: 600;
        }

        .user-error {
          margin-bottom: 18px;
        }

        .user-stats-grid {
          display: grid;
          grid-template-columns:
            repeat(5, minmax(0, 1fr));
          gap: 14px;
          margin-bottom: 20px;
        }

        .user-stat-card {
          display: flex;
          align-items: center;
          gap: 13px;
          min-height: 86px;
          padding: 17px;
          background: #ffffff;
          border: 1px solid #e5e7eb;
          border-radius: 14px;
          box-shadow:
            0 2px 8px
            rgba(15, 23, 42, 0.04);
        }

        .user-stat-icon {
          width: 43px;
          height: 43px;
          border-radius: 11px;
          display: flex;
          align-items: center;
          justify-content: center;
          flex-shrink: 0;
        }

        .total-icon {
          background: #eff6ff;
          color: #2563eb;
        }

        .employee-icon {
          background: #f5f3ff;
          color: #7c3aed;
        }

        .reviewer-icon {
          background: #fff7ed;
          color: #ea580c;
        }

        .manager-icon {
          background: #f0fdfa;
          color: #0f766e;
        }

        .admin-icon {
          background: #fef2f2;
          color: #dc2626;
        }

        .user-stat-card span {
          display: block;
          color: #64748b;
          font-size: 12px;
          margin-bottom: 4px;
        }

        .user-stat-card strong {
          display: block;
          color: #0f172a;
          font-size: 23px;
          line-height: 1;
        }

        .users-card {
          background: #ffffff;
          border: 1px solid #e5e7eb;
          border-radius: 16px;
          box-shadow:
            0 2px 8px
            rgba(15, 23, 42, 0.04);
          overflow: hidden;
        }

        .users-card-header {
          padding: 22px 24px 15px;
        }

        .users-card-header h2 {
          margin: 0 0 5px;
          color: #0f172a;
          font-size: 20px;
        }

        .users-card-header p {
          margin: 0;
          color: #64748b;
          font-size: 13px;
        }

        .user-filters {
          display: flex;
          gap: 12px;
          padding: 0 24px 20px;
        }

        .user-search {
          flex: 1;
          min-width: 0;
          height: 43px;
          display: flex;
          align-items: center;
          gap: 9px;
          padding: 0 13px;
          background: #f8fafc;
          border: 1px solid #dbe3ef;
          border-radius: 10px;
          color: #64748b;
        }

        .user-search:focus-within {
          border-color: #2563eb;
          box-shadow:
            0 0 0 3px
            rgba(37, 99, 235, 0.10);
          background: #ffffff;
        }

        .user-search input {
          width: 100%;
          min-width: 0;
          border: 0;
          outline: none;
          background: transparent;
          color: #0f172a;
          font-size: 13px;
        }

        .user-search input::placeholder {
          color: #94a3b8;
        }

        .clear-search {
          border: 0;
          background: transparent;
          color: #94a3b8;
          display: flex;
          cursor: pointer;
          padding: 2px;
        }

        .role-filter {
          width: 180px;
          height: 43px;
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 0 12px;
          box-sizing: border-box;
          background: #f8fafc;
          border: 1px solid #dbe3ef;
          border-radius: 10px;
          color: #64748b;
        }

        .role-filter select {
          flex: 1;
          min-width: 0;
          border: 0;
          outline: none;
          background: transparent;
          color: #334155;
          font-size: 13px;
          cursor: pointer;
        }

        .users-table-wrapper {
          width: 100%;
          overflow-x: auto;
          border-top: 1px solid #eef2f7;
        }

        .users-table {
          width: 100%;
          min-width: 1150px;
          border-collapse: collapse;
        }

        .users-table th {
          padding: 13px 15px;
          background: #f8fafc;
          border-bottom: 1px solid #e2e8f0;
          color: #64748b;
          font-size: 11px;
          font-weight: 700;
          text-align: left;
          white-space: nowrap;
          text-transform: uppercase;
          letter-spacing: 0.04em;
        }

        .users-table td {
          padding: 14px 15px;
          border-bottom: 1px solid #eef2f7;
          color: #334155;
          font-size: 13px;
          vertical-align: middle;
          white-space: nowrap;
        }

        .users-table tbody tr:hover {
          background: #fafcff;
        }

        .users-table tbody tr:last-child td {
          border-bottom: 0;
        }

        .user-id {
          color: #64748b;
          font-weight: 600;
        }

        .user-name-cell {
          display: flex;
          align-items: center;
          gap: 9px;
        }

        .user-avatar {
          width: 32px;
          height: 32px;
          border-radius: 9px;
          background: #dbeafe;
          color: #2563eb;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 12px;
          font-weight: 700;
          flex-shrink: 0;
        }

        .user-name-cell strong {
          color: #0f172a;
          font-size: 13px;
        }

        .email-cell,
        .phone-cell {
          display: flex;
          align-items: center;
          gap: 7px;
          color: #64748b;
        }

        .email-cell span,
        .phone-cell span {
          color: #475569;
        }

        .role-badge {
          display: inline-flex;
          align-items: center;
          padding: 5px 9px;
          border-radius: 20px;
          font-size: 10px;
          font-weight: 700;
        }

        .role-employee {
          background: #f5f3ff;
          color: #7c3aed;
        }

        .role-reviewer {
          background: #fff7ed;
          color: #c2410c;
        }

        .role-manager {
          background: #ecfeff;
          color: #0e7490;
        }

        .role-administrator {
          background: #f0fdf4;
          color: #15803d;
        }

        .muted {
          color: #94a3b8;
        }

        .user-actions {
          display: flex;
          align-items: center;
          gap: 7px;
        }

        .table-action {
          display: inline-flex;
          align-items: center;
          justify-content: center;
          gap: 6px;
          min-height: 34px;
          padding: 0 10px;
          border-radius: 8px;
          background: #ffffff;
          font-size: 12px;
          font-weight: 600;
          cursor: pointer;
          transition: 0.15s ease;
        }

        .edit-action {
          color: #2563eb;
          border: 1px solid #bfdbfe;
        }

        .edit-action:hover {
          background: #eff6ff;
        }

        .delete-action {
          color: #dc2626;
          border: 1px solid #fecaca;
        }

        .delete-action:hover {
          background: #fef2f2;
        }

        .table-action:disabled {
          opacity: 0.55;
          cursor: not-allowed;
        }

        .user-loading {
          padding: 55px 20px;
          text-align: center;
          color: #64748b;
          font-size: 14px;
        }

        .user-empty {
          padding: 60px 20px;
          text-align: center;
          border-top: 1px solid #eef2f7;
        }

        .empty-user-icon {
          width: 58px;
          height: 58px;
          margin: 0 auto 14px;
          border-radius: 15px;
          display: flex;
          align-items: center;
          justify-content: center;
          background: #f1f5f9;
          color: #64748b;
        }

        .user-empty h3 {
          margin: 0 0 6px;
          color: #0f172a;
          font-size: 17px;
        }

        .user-empty p {
          margin: 0;
          color: #64748b;
          font-size: 13px;
        }

        .modal-overlay {
          position: fixed;
          inset: 0;
          z-index: 1000;
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 20px;
          background:
            rgba(15, 23, 42, 0.52);
          overflow-y: auto;
        }

        .user-modal {
          width: min(760px, 100%);
          max-height: 92vh;
          overflow-y: auto;
          background: #ffffff;
          border-radius: 18px;
          box-shadow:
            0 25px 60px
            rgba(15, 23, 42, 0.25);
        }

        .user-modal-header {
          display: flex;
          justify-content: space-between;
          gap: 20px;
          padding: 22px 24px;
          border-bottom: 1px solid #e5e7eb;
        }

        .modal-heading {
          display: flex;
          align-items: center;
          gap: 12px;
        }

        .modal-icon {
          width: 42px;
          height: 42px;
          border-radius: 11px;
          background: #eff6ff;
          color: #2563eb;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .modal-heading h2 {
          margin: 0 0 4px;
          color: #0f172a;
          font-size: 19px;
        }

        .modal-heading p {
          margin: 0;
          color: #64748b;
          font-size: 12px;
        }

        .modal-close {
          width: 36px;
          height: 36px;
          border: 1px solid #e2e8f0;
          border-radius: 9px;
          background: #ffffff;
          color: #64748b;
          display: flex;
          align-items: center;
          justify-content: center;
          cursor: pointer;
        }

        .modal-close:hover {
          background: #f8fafc;
          color: #0f172a;
        }

        .user-form {
          padding: 24px;
        }

        .form-error,
        .form-success {
          padding: 11px 13px;
          border-radius: 9px;
          margin-bottom: 17px;
          font-size: 13px;
        }

        .form-error {
          color: #b91c1c;
          background: #fef2f2;
          border: 1px solid #fecaca;
        }

        .form-success {
          color: #15803d;
          background: #f0fdf4;
          border: 1px solid #bbf7d0;
        }

        .form-grid {
          display: grid;
          grid-template-columns:
            repeat(2, minmax(0, 1fr));
          gap: 17px;
        }

        .form-group {
          display: flex;
          flex-direction: column;
          gap: 7px;
        }

        .form-group label {
          color: #334155;
          font-size: 12px;
          font-weight: 700;
        }

        .form-group label span {
          color: #dc2626;
          margin-left: 3px;
        }

        .form-group input,
        .form-group select {
          width: 100%;
          height: 42px;
          box-sizing: border-box;
          padding: 0 12px;
          border: 1px solid #dbe3ef;
          border-radius: 9px;
          outline: none;
          background: #ffffff;
          color: #0f172a;
          font-size: 13px;
        }

        .form-group input:focus,
        .form-group select:focus {
          border-color: #2563eb;
          box-shadow:
            0 0 0 3px
            rgba(37, 99, 235, 0.10);
        }

        .form-group input::placeholder {
          color: #94a3b8;
        }

        .modal-actions {
          display: flex;
          justify-content: flex-end;
          gap: 10px;
          margin-top: 24px;
          padding-top: 19px;
          border-top: 1px solid #e5e7eb;
        }

        .modal-actions button {
          display: inline-flex;
          align-items: center;
          justify-content: center;
          gap: 7px;
        }

        @media (max-width: 1200px) {
          .user-stats-grid {
            grid-template-columns:
              repeat(3, minmax(0, 1fr));
          }
        }

        @media (max-width: 800px) {
          .user-stats-grid {
            grid-template-columns:
              repeat(2, minmax(0, 1fr));
          }

          .user-filters {
            flex-direction: column;
          }

          .role-filter {
            width: 100%;
          }

          .form-grid {
            grid-template-columns: 1fr;
          }
        }

        @media (max-width: 520px) {
          .user-stats-grid {
            grid-template-columns: 1fr;
          }

          .user-page-header {
            align-items: flex-start;
            flex-direction: column;
          }

          .create-user-button {
            width: 100%;
            justify-content: center;
          }

          .users-card-header,
          .user-filters {
            padding-left: 16px;
            padding-right: 16px;
          }

          .user-modal-header,
          .user-form {
            padding: 18px;
          }
        }

      `}</style>

    </div>
  );
}