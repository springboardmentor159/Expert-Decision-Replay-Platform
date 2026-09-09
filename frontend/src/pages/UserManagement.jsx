import { useEffect, useMemo, useState } from "react";

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


function getErrorMessage(error) {
  const status = error?.response?.status;

  const detail =
    error?.response?.data?.detail;

  if (typeof detail === "string") {
    return detail;
  }

  if (Array.isArray(detail)) {
    return detail
      .map((item) => item?.msg || "Invalid input")
      .join(", ");
  }

  switch (status) {
    case 400:
      return "Invalid request. Please check the entered information.";

    case 401:
      return "Your session has expired. Please log in again.";

    case 403:
      return "You do not have permission to manage users.";

    case 404:
      return "User not found.";

    case 422:
      return "Please correct the validation errors.";

    case 500:
      return "Server error. Please try again.";

    default:
      return (
        error?.message ||
        "Unable to complete the request."
      );
  }
}


function getRoleClass(role) {
  switch (role) {
    case "Administrator":
      return "status-approved";

    case "Manager":
      return "status-under-review";

    case "Reviewer":
      return "status-draft";

    case "Employee":
      return "status-archived";

    default:
      return "";
  }
}


function UserManagement() {
  const [users, setUsers] = useState([]);

  const [loading, setLoading] =
    useState(true);

  const [saving, setSaving] =
    useState(false);

  const [error, setError] =
    useState("");

  const [success, setSuccess] =
    useState("");

  const [search, setSearch] =
    useState("");

  const [roleFilter, setRoleFilter] =
    useState("");

  const [showForm, setShowForm] =
    useState(false);

  const [editingUserId, setEditingUserId] =
    useState(null);

  const [form, setForm] =
    useState(EMPTY_FORM);


  async function loadUsers() {
    try {
      setLoading(true);
      setError("");

      const data = await getUsers();

      if (Array.isArray(data)) {
        setUsers(data);
      } else if (
        Array.isArray(data?.users)
      ) {
        setUsers(data.users);
      } else if (
        Array.isArray(data?.items)
      ) {
        setUsers(data.items);
      } else {
        setUsers([]);
      }
    } catch (err) {
      setError(
        getErrorMessage(err)
      );
    } finally {
      setLoading(false);
    }
  }


  useEffect(() => {
    loadUsers();
  }, []);


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


  function openCreateForm() {
    setEditingUserId(null);

    setForm({
      ...EMPTY_FORM,
    });

    setError("");
    setSuccess("");
    setShowForm(true);
  }


  function openEditForm(user) {
    setEditingUserId(user.id);

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

    setError("");
    setSuccess("");
    setShowForm(true);

    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  }


  function closeForm() {
    if (saving) {
      return;
    }

    setShowForm(false);
    setEditingUserId(null);
    setForm({
      ...EMPTY_FORM,
    });
  }


  function validateForm() {
    if (!form.full_name.trim()) {
      return "Full name is required.";
    }

    if (!form.email.trim()) {
      return "Email is required.";
    }

    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(
      form.email.trim()
    )) {
      return "Please enter a valid email address.";
    }

    if (!form.role) {
      return "Role is required.";
    }

    if (!editingUserId && !form.password.trim()) {
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

    setError("");
    setSuccess("");

    const validationError =
      validateForm();

    if (validationError) {
      setError(validationError);
      return;
    }

    try {
      setSaving(true);

      const payload = {
        full_name:
          form.full_name.trim(),

        email:
          form.email.trim(),

        role:
          form.role,

        employee_id:
          form.employee_id.trim() || null,

        department:
          form.department.trim() || null,

        designation:
          form.designation.trim() || null,

        phone_number:
          form.phone_number.trim() || null,
      };

      if (form.password.trim()) {
        payload.password =
          form.password.trim();
      }


      if (editingUserId) {
        await updateUser(
          editingUserId,
          payload
        );

        setSuccess(
          "User updated successfully."
        );
      } else {
        await createUser(payload);

        setSuccess(
          "User created successfully."
        );
      }

      await loadUsers();

      setShowForm(false);
      setEditingUserId(null);

      setForm({
        ...EMPTY_FORM,
      });
    } catch (err) {
      setError(
        getErrorMessage(err)
      );
    } finally {
      setSaving(false);
    }
  }


  async function handleDelete(user) {
    const confirmed =
      window.confirm(
        `Delete user "${user.full_name}"?\n\nThis action cannot be undone.`
      );

    if (!confirmed) {
      return;
    }

    try {
      setError("");
      setSuccess("");

      await deleteUser(user.id);

      setSuccess(
        "User deleted successfully."
      );

      await loadUsers();
    } catch (err) {
      setError(
        getErrorMessage(err)
      );
    }
  }


  const filteredUsers =
    useMemo(() => {
      const searchValue =
        search.trim().toLowerCase();

      return users.filter((user) => {
        const matchesSearch =
          !searchValue ||
          String(user.full_name || "")
            .toLowerCase()
            .includes(searchValue) ||
          String(user.email || "")
            .toLowerCase()
            .includes(searchValue) ||
          String(user.employee_id || "")
            .toLowerCase()
            .includes(searchValue) ||
          String(user.department || "")
            .toLowerCase()
            .includes(searchValue);

        const matchesRole =
          !roleFilter ||
          user.role === roleFilter;

        return (
          matchesSearch &&
          matchesRole
        );
      });
    }, [
      users,
      search,
      roleFilter,
    ]);


  const roleCounts =
    useMemo(() => {
      return ROLES.reduce(
        (counts, role) => {
          counts[role] =
            users.filter(
              (user) =>
                user.role === role
            ).length;

          return counts;
        },
        {}
      );
    }, [users]);


  return (
    <div className="page-container">

      {/* HEADER */}

      <div className="page-header">

        <div>
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
          className="primary-button"
          onClick={openCreateForm}
        >
          + Create User
        </button>

      </div>


      {/* MESSAGES */}

      {error && (
        <div className="error-state">
          <strong>
            Error:
          </strong>{" "}
          {error}
        </div>
      )}


      {success && (
        <div className="success-state">
          {success}
        </div>
      )}


      {/* STATISTICS */}

      <div className="stats-grid">

        <div className="stat-card">
          <span>
            Total Users
          </span>

          <strong>
            {users.length}
          </strong>
        </div>


        <div className="stat-card">
          <span>
            Employees
          </span>

          <strong>
            {roleCounts.Employee || 0}
          </strong>
        </div>


        <div className="stat-card">
          <span>
            Reviewers
          </span>

          <strong>
            {roleCounts.Reviewer || 0}
          </strong>
        </div>


        <div className="stat-card">
          <span>
            Managers
          </span>

          <strong>
            {roleCounts.Manager || 0}
          </strong>
        </div>


        <div className="stat-card">
          <span>
            Administrators
          </span>

          <strong>
            {roleCounts.Administrator || 0}
          </strong>
        </div>

      </div>


      {/* CREATE / EDIT FORM */}

      {showForm && (
        <div className="card">

          <div className="page-header">

            <div>
              <h2>
                {editingUserId
                  ? "Edit User"
                  : "Create User"}
              </h2>

              <p>
                {editingUserId
                  ? `Update user #${editingUserId}.`
                  : "Add a new platform user."}
              </p>
            </div>

          </div>


          <form
            onSubmit={handleSubmit}
          >

            <div className="form-row">

              <div className="form-group">

                <label htmlFor="full_name">
                  Full Name *
                </label>

                <input
                  id="full_name"
                  name="full_name"
                  type="text"
                  value={form.full_name}
                  onChange={handleChange}
                  placeholder="Enter full name"
                  disabled={saving}
                />

              </div>


              <div className="form-group">

                <label htmlFor="email">
                  Email *
                </label>

                <input
                  id="email"
                  name="email"
                  type="email"
                  value={form.email}
                  onChange={handleChange}
                  placeholder="user@example.com"
                  disabled={saving}
                />

              </div>

            </div>


            <div className="form-row">

              <div className="form-group">

                <label htmlFor="role">
                  Role *
                </label>

                <select
                  id="role"
                  name="role"
                  value={form.role}
                  onChange={handleChange}
                  disabled={saving}
                >

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


              <div className="form-group">

                <label htmlFor="employee_id">
                  Employee ID
                </label>

                <input
                  id="employee_id"
                  name="employee_id"
                  type="text"
                  value={form.employee_id}
                  onChange={handleChange}
                  placeholder="E008"
                  disabled={saving}
                />

              </div>

            </div>


            <div className="form-row">

              <div className="form-group">

                <label htmlFor="department">
                  Department
                </label>

                <input
                  id="department"
                  name="department"
                  type="text"
                  value={form.department}
                  onChange={handleChange}
                  placeholder="Engineering"
                  disabled={saving}
                />

              </div>


              <div className="form-group">

                <label htmlFor="designation">
                  Designation
                </label>

                <input
                  id="designation"
                  name="designation"
                  type="text"
                  value={form.designation}
                  onChange={handleChange}
                  placeholder="Software Engineer"
                  disabled={saving}
                />

              </div>

            </div>


            <div className="form-row">

              <div className="form-group">

                <label htmlFor="phone_number">
                  Phone Number
                </label>

                <input
                  id="phone_number"
                  name="phone_number"
                  type="tel"
                  value={form.phone_number}
                  onChange={handleChange}
                  placeholder="9876543210"
                  disabled={saving}
                />

              </div>


              <div className="form-group">

                <label htmlFor="password">
                  {editingUserId
                    ? "New Password (optional)"
                    : "Password *"}
                </label>

                <input
                  id="password"
                  name="password"
                  type="password"
                  value={form.password}
                  onChange={handleChange}
                  placeholder={
                    editingUserId
                      ? "Leave blank to keep current password"
                      : "Enter password"
                  }
                  disabled={saving}
                />

              </div>

            </div>


            <div className="page-footer-actions">

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
                {saving
                  ? "Saving..."
                  : editingUserId
                    ? "Save Changes"
                    : "Create User"}
              </button>

            </div>

          </form>

        </div>
      )}


      {/* FILTERS */}

      <div className="card">

        <div className="form-row">

          <div className="form-group">

            <label htmlFor="user-search">
              Search Users
            </label>

            <input
              id="user-search"
              type="text"
              value={search}
              onChange={(event) =>
                setSearch(
                  event.target.value
                )
              }
              placeholder="Search by name, email, ID, department..."
            />

          </div>


          <div className="form-group">

            <label htmlFor="role-filter">
              Filter by Role
            </label>

            <select
              id="role-filter"
              value={roleFilter}
              onChange={(event) =>
                setRoleFilter(
                  event.target.value
                )
              }
            >

              <option value="">
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

      </div>


      {/* USER TABLE */}

      <div className="card">

        <div className="page-header">

          <div>
            <h2>
              Platform Users
            </h2>

            <p>
              {filteredUsers.length} user
              {filteredUsers.length === 1
                ? ""
                : "s"} displayed
            </p>
          </div>

        </div>


        {loading ? (
          <div className="loading-state">
            Loading users...
          </div>
        ) : filteredUsers.length === 0 ? (
          <div className="empty-state">

            <h2>
              No Users Found
            </h2>

            <p>
              No users match the current
              search or role filter.
            </p>

          </div>
        ) : (
          <div className="table-container">

            <table>

              <thead>

                <tr>

                  <th>
                    ID
                  </th>

                  <th>
                    Name
                  </th>

                  <th>
                    Email
                  </th>

                  <th>
                    Role
                  </th>

                  <th>
                    Employee ID
                  </th>

                  <th>
                    Department
                  </th>

                  <th>
                    Designation
                  </th>

                  <th>
                    Phone
                  </th>

                  <th>
                    Actions
                  </th>

                </tr>

              </thead>


              <tbody>

                {filteredUsers.map(
                  (user) => (
                    <tr
                      key={user.id}
                    >

                      <td>
                        #{user.id}
                      </td>

                      <td>
                        <strong>
                          {user.full_name ||
                            "—"}
                        </strong>
                      </td>

                      <td>
                        {user.email ||
                          "—"}
                      </td>

                      <td>

                        <span
                          className={`status-badge ${getRoleClass(
                            user.role
                          )}`}
                        >
                          {user.role ||
                            "—"}
                        </span>

                      </td>

                      <td>
                        {user.employee_id ||
                          "—"}
                      </td>

                      <td>
                        {user.department ||
                          "—"}
                      </td>

                      <td>
                        {user.designation ||
                          "—"}
                      </td>

                      <td>
                        {user.phone_number ||
                          "—"}
                      </td>

                      <td>

                        <div className="table-actions">

                          <button
                            type="button"
                            className="secondary-button"
                            onClick={() =>
                              openEditForm(
                                user
                              )
                            }
                          >
                            Edit
                          </button>


                          <button
                            type="button"
                            className="danger-button"
                            onClick={() =>
                              handleDelete(
                                user
                              )
                            }
                          >
                            Delete
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

    </div>
  );
}


export default UserManagement;