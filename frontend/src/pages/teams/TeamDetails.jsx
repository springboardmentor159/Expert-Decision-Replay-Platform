import { useEffect, useState } from "react";
import {
  useNavigate,
  useParams,
} from "react-router-dom";

import { useAuth } from "../../context/AuthContext";

import {
  getTeam,
  getTeamMembers,
  addTeamMember,
  removeTeamMember,
} from "../../services/teamService";

import axiosClient from "../../api/axiosClient";

import PageHeader from "../../components/PageHeader";
import Button from "../../components/Button";
import Card from "../../components/Card";
import Alert from "../../components/Alert";


const TeamDetails = () => {
  const { teamId } = useParams();
  const navigate = useNavigate();

  const { role } = useAuth();

  const [team, setTeam] = useState(null);
  const [members, setMembers] = useState([]);
  const [users, setUsers] = useState([]);

  const [selectedUser, setSelectedUser] =
    useState("");

  const [loading, setLoading] =
    useState(true);

  const [adding, setAdding] =
    useState(false);

  const [removingUser, setRemovingUser] =
    useState(null);

  const [error, setError] =
    useState("");

  const [success, setSuccess] =
    useState("");


  const canManage =
    role === "Manager" ||
    role === "Administrator";


  // ---------------------------------------------------------
  // Load Team
  // ---------------------------------------------------------

  const loadTeam = async () => {
    try {

      const data =
        await getTeam(teamId);

      setTeam(data);

    } catch (err) {

      console.error(
        "Team details loading error:",
        err
      );

      if (err.response?.status === 401) {
        setError(
          "You are not authenticated."
        );
      } else if (err.response?.status === 403) {
        setError(
          "You do not have permission to view this team."
        );
      } else if (err.response?.status === 404) {
        setError(
          "Team not found."
        );
      } else if (err.response?.status === 500) {
        setError(
          "Server error. Please try again later."
        );
      } else {
        setError(
          "Failed to load team details."
        );
      }

    }
  };


  // ---------------------------------------------------------
  // Load Members
  // ---------------------------------------------------------

  const loadMembers = async () => {
    try {

      const data =
        await getTeamMembers(teamId);

      if (Array.isArray(data)) {

        setMembers(data);

      } else if (
        Array.isArray(data?.members)
      ) {

        setMembers(data.members);

      } else if (
        Array.isArray(data?.items)
      ) {

        setMembers(data.items);

      } else {

        setMembers([]);

      }

    } catch (err) {

      console.error(
        "Team members loading error:",
        err
      );

      if (err.response?.status === 401) {
        setError(
          "You are not authenticated."
        );
      } else if (err.response?.status === 403) {
        setError(
          "You do not have permission to view team members."
        );
      } else if (err.response?.status === 404) {
        setError(
          "Team not found."
        );
      } else {
        setError(
          "Failed to load team members."
        );
      }

    }
  };


  // ---------------------------------------------------------
  // Load Users
  // ---------------------------------------------------------

  const loadUsers = async () => {
    try {

      const response =
        await axiosClient.get("/users");

      const data =
        response.data;

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

      console.error(
        "Users loading error:",
        err
      );

      if (err.response?.status === 401) {
        setError(
          "You are not authenticated."
        );
      } else if (err.response?.status === 403) {
        setError(
          "You do not have permission to load users."
        );
      }

    }
  };


  // ---------------------------------------------------------
  // Load All Data
  // ---------------------------------------------------------

  const loadData = async () => {

    try {

      setLoading(true);
      setError("");

      await Promise.all([
        loadTeam(),
        loadMembers(),
        ...(canManage
          ? [loadUsers()]
          : []),
      ]);

    } finally {

      setLoading(false);

    }
  };


  useEffect(() => {
    loadData();
  }, [teamId, role]);


  // ---------------------------------------------------------
  // Add Member
  // ---------------------------------------------------------

  const handleAddMember = async (
    event
  ) => {

    event.preventDefault();

    setError("");
    setSuccess("");

    if (!selectedUser) {

      setError(
        "Please select a user."
      );

      return;
    }

    try {

      setAdding(true);

      await addTeamMember(
        teamId,
        Number(selectedUser)
      );

      setSelectedUser("");

      setSuccess(
        "Member added to the team successfully."
      );

      await loadMembers();

    } catch (err) {

      console.error(
        "Add member error:",
        err
      );

      if (err.response?.status === 400) {
        setError(
          "Invalid member information."
        );
      } else if (err.response?.status === 401) {
        setError(
          "You are not authenticated."
        );
      } else if (err.response?.status === 403) {
        setError(
          "You do not have permission to add members."
        );
      } else if (err.response?.status === 404) {
        setError(
          "Team or user not found."
        );
      } else if (err.response?.status === 422) {
        setError(
          "Please check the selected user."
        );
      } else if (err.response?.status === 500) {
        setError(
          "Server error. Please try again later."
        );
      } else {
        setError(
          "Failed to add member."
        );
      }

    } finally {

      setAdding(false);

    }
  };


  // ---------------------------------------------------------
  // Remove Member
  // ---------------------------------------------------------

  const handleRemoveMember = async (
    userId
  ) => {

    setError("");
    setSuccess("");

    const confirmed =
      window.confirm(
        "Are you sure you want to remove this member from the team?"
      );

    if (!confirmed) {
      return;
    }

    try {

      setRemovingUser(userId);

      await removeTeamMember(
        teamId,
        userId
      );

      setSuccess(
        "Member removed from the team successfully."
      );

      await loadMembers();

    } catch (err) {

      console.error(
        "Remove member error:",
        err
      );

      if (err.response?.status === 401) {
        setError(
          "You are not authenticated."
        );
      } else if (err.response?.status === 403) {
        setError(
          "You do not have permission to remove members."
        );
      } else if (err.response?.status === 404) {
        setError(
          "Team or member not found."
        );
      } else if (err.response?.status === 500) {
        setError(
          "Server error. Please try again later."
        );
      } else {
        setError(
          "Failed to remove member."
        );
      }

    } finally {

      setRemovingUser(null);

    }
  };


  // ---------------------------------------------------------
  // Loading
  // ---------------------------------------------------------

  if (loading) {

    return (
      <div className="dashboard-page">

        <PageHeader
          title="Team Details"
          subtitle="Loading team information..."
        />

        <Card>
          <p>
            Loading...
          </p>
        </Card>

      </div>
    );
  }


  // ---------------------------------------------------------
  // Team Not Found
  // ---------------------------------------------------------

  if (!team) {

    return (
      <div className="dashboard-page">

        <PageHeader
          title="Team Details"
          subtitle="Team information"
        />

        {error && (
          <Alert type="error">
            {error}
          </Alert>
        )}

        <Button
          onClick={() =>
            navigate("/teams")
          }
        >
          Back to Teams
        </Button>

      </div>
    );
  }


  // ---------------------------------------------------------
  // Existing Member IDs
  // ---------------------------------------------------------

  const memberIds =
    members.map((member) =>
      Number(
        member.id ??
        member.user_id
      )
    );


  // Users not already in team
  const availableUsers =
    users.filter(
      (user) =>
        !memberIds.includes(
          Number(user.id)
        )
    );


  // ---------------------------------------------------------
  // Page
  // ---------------------------------------------------------

  return (
    <div className="dashboard-page">

      {/* Header */}

      <PageHeader
        title={team.name}
        subtitle="Team details and member management"
      />


      {/* Alerts */}

      {error && (
        <Alert type="error">
          {error}
        </Alert>
      )}

      {success && (
        <Alert type="success">
          {success}
        </Alert>
      )}


      {/* Team Information */}

      <Card>

        <div className="card-header">

          <div>

            <h2>
              Team Information
            </h2>

            <p>
              {team.description ||
                "No description available."}
            </p>

          </div>

        </div>


        <div className="dashboard-stats">

          <div className="stat-card">

            <span className="stat-label">
              Team ID
            </span>

            <span className="stat-value">
              {team.id}
            </span>

          </div>


          <div className="stat-card">

            <span className="stat-label">
              Members
            </span>

            <span className="stat-value">
              {members.length}
            </span>

          </div>


          <div className="stat-card">

            <span className="stat-label">
              Your Role
            </span>

            <span className="stat-value">
              {role || "-"}
            </span>

          </div>

        </div>

      </Card>


      {/* Add Member */}

      {canManage && (

        <Card>

          <div className="card-header">

            <div>

              <h2>
                Add Member
              </h2>

              <p>
                Add an existing user to this team.
              </p>

            </div>

          </div>


          <form
            onSubmit={handleAddMember}
            className="form-grid"
          >

            <div className="form-group">

              <label htmlFor="team-member">
                Select User
              </label>

              <select
                id="team-member"
                value={selectedUser}
                onChange={(event) =>
                  setSelectedUser(
                    event.target.value
                  )
                }
              >

                <option value="">
                  Select a user
                </option>

                {availableUsers.map(
                  (user) => (

                    <option
                      key={user.id}
                      value={user.id}
                    >
                      {user.full_name ||
                        user.name ||
                        user.email}
                      {" - "}
                      {user.email}
                    </option>

                  )
                )}

              </select>

            </div>


            <div className="form-actions">

              <Button
                type="submit"
                disabled={adding}
              >
                {adding
                  ? "Adding..."
                  : "Add Member"}
              </Button>

            </div>

          </form>


          {availableUsers.length === 0 &&
            users.length > 0 && (

              <p className="empty-message">
                All available users are already
                members of this team.
              </p>

            )}

        </Card>
      )}


      {/* Members */}

      <Card>

        <div className="card-header">

          <div>

            <h2>
              Team Members
            </h2>

            <p>
              Users currently assigned to this team.
            </p>

          </div>

        </div>


        {members.length === 0 ? (

          <div className="empty-state">

            <h3>
              No members
            </h3>

            <p>
              No users have been added
              to this team yet.
            </p>

          </div>

        ) : (

          <div className="table-container">

            <table className="data-table">

              <thead>

                <tr>

                  <th>ID</th>
                  <th>Name</th>
                  <th>Email</th>
                  <th>Role</th>

                  {canManage && (
                    <th>Actions</th>
                  )}

                </tr>

              </thead>


              <tbody>

                {members.map(
                  (member) => {

                    const userId =
                      member.id ??
                      member.user_id;

                    const name =
                      member.full_name ??
                      member.name ??
                      "-";

                    const email =
                      member.email ??
                      "-";

                    const memberRole =
                      member.role ??
                      "-";


                    return (

                      <tr
                        key={userId}
                      >

                        <td>
                          {userId}
                        </td>

                        <td>
                          {name}
                        </td>

                        <td>
                          {email}
                        </td>

                        <td>
                          {memberRole}
                        </td>


                        {canManage && (

                          <td>

                            <Button
                              variant="danger"
                              onClick={() =>
                                handleRemoveMember(
                                  userId
                                )
                              }
                              disabled={
                                removingUser ===
                                userId
                              }
                            >
                              {removingUser ===
                              userId
                                ? "Removing..."
                                : "Remove"}
                            </Button>

                          </td>

                        )}

                      </tr>

                    );
                  }
                )}

              </tbody>

            </table>

          </div>

        )}

      </Card>


      {/* Back */}

      <div className="page-actions">

        <Button
          variant="secondary"
          onClick={() =>
            navigate("/teams")
          }
        >
          Back to Teams
        </Button>

      </div>

    </div>
  );
};


export default TeamDetails;