import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";

import {
  getTeams,
  createTeam,
} from "../../services/teamService";

import PageHeader from "../../components/PageHeader";
import Button from "../../components/Button";
import Card from "../../components/Card";
import Alert from "../../components/Alert";


const Teams = () => {
  const { role } = useAuth();
  const navigate = useNavigate();

  const [teams, setTeams] = useState([]);

  const [name, setName] = useState("");
  const [description, setDescription] = useState("");

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");


  const canManage =
    role === "Manager" ||
    role === "Administrator";


  // =========================================================
  // LOAD TEAMS
  // =========================================================

  const loadTeams = async () => {
    try {
      setLoading(true);
      setError("");

      const data = await getTeams();

      if (Array.isArray(data)) {
        setTeams(data);
      } else if (Array.isArray(data?.teams)) {
        setTeams(data.teams);
      } else if (Array.isArray(data?.items)) {
        setTeams(data.items);
      } else {
        setTeams([]);
      }

    } catch (err) {
      console.error(
        "Teams loading error:",
        err
      );

      if (err.response?.status === 401) {
        setError(
          "You are not authenticated."
        );
      } else if (err.response?.status === 403) {
        setError(
          "You do not have permission to view teams."
        );
      } else if (err.response?.status === 500) {
        setError(
          "Server error. Please try again later."
        );
      } else {
        setError(
          "Failed to load teams."
        );
      }

    } finally {
      setLoading(false);
    }
  };


  useEffect(() => {
    loadTeams();
  }, []);


  // =========================================================
  // CREATE TEAM
  // =========================================================

  const handleCreateTeam = async (event) => {
    event.preventDefault();

    setError("");
    setSuccess("");

    if (!name.trim()) {
      setError(
        "Team name is required."
      );
      return;
    }

    try {
      setSaving(true);

      await createTeam({
        name: name.trim(),
        description:
          description.trim() || null,
      });

      setName("");
      setDescription("");

      setSuccess(
        "Team created successfully."
      );

      await loadTeams();

    } catch (err) {
      console.error(
        "Create team error:",
        err
      );

      if (err.response?.status === 400) {
        setError(
          "Invalid team information."
        );
      } else if (err.response?.status === 401) {
        setError(
          "You are not authenticated."
        );
      } else if (err.response?.status === 403) {
        setError(
          "You do not have permission to create teams."
        );
      } else if (err.response?.status === 422) {
        setError(
          "Please check the entered values."
        );
      } else if (err.response?.status === 500) {
        setError(
          "Server error. Please try again later."
        );
      } else {
        setError(
          "Failed to create team."
        );
      }

    } finally {
      setSaving(false);
    }
  };


  // =========================================================
  // LOADING
  // =========================================================

  if (loading) {
    return (
      <div className="dashboard-page">

        <PageHeader
          title="Team Management"
          subtitle="Create, view and manage teams"
        />

        <Card>
          <p>Loading teams...</p>
        </Card>

      </div>
    );
  }


  // =========================================================
  // PAGE
  // =========================================================

  return (
    <div className="dashboard-page teams-page">

      {/* PAGE HEADER */}

      <PageHeader
        title="Team Management"
        subtitle="Create, view and manage teams"
      />


      {/* ALERTS */}

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


      {/* =====================================================
          SUMMARY
      ===================================================== */}

      <div className="teams-summary">

        <div className="team-summary-card">

          <div className="team-summary-label">
            Total Teams
          </div>

          <div className="team-summary-value">
            {teams.length}
          </div>

        </div>


        <div className="team-summary-card">

          <div className="team-summary-label">
            Your Role
          </div>

          <div className="team-summary-value">
            {role || "-"}
          </div>

        </div>

      </div>


      {/* =====================================================
          CREATE TEAM
      ===================================================== */}

      {canManage && (

        <Card>

          <div className="team-create-section">

            <div className="team-create-heading">

              <h2>
                Create Team
              </h2>

              <p>
                Create a new organizational team.
              </p>

            </div>


            <form
              onSubmit={handleCreateTeam}
              className="team-create-form"
            >

              <div className="team-form-field">

                <label htmlFor="team-name">
                  Team Name *
                </label>

                <input
                  id="team-name"
                  type="text"
                  value={name}
                  onChange={(event) =>
                    setName(event.target.value)
                  }
                  placeholder="Enter team name"
                  maxLength={100}
                />

              </div>


              <div className="team-form-field">

                <label htmlFor="team-description">
                  Description
                </label>

                <textarea
                  id="team-description"
                  value={description}
                  onChange={(event) =>
                    setDescription(
                      event.target.value
                    )
                  }
                  placeholder="Enter team description"
                  rows="3"
                  maxLength={500}
                />

              </div>


              <div className="team-create-button">

                <Button
                  type="submit"
                  disabled={saving}
                >
                  {saving
                    ? "Creating..."
                    : "Create Team"}
                </Button>

              </div>

            </form>

          </div>

        </Card>
      )}


      {/* =====================================================
          TEAMS TABLE
      ===================================================== */}

      <Card>

        <div className="teams-table-header">

          <div>

            <h2>
              Teams
            </h2>

            <p>
              View and manage available teams.
            </p>

          </div>

        </div>


        {teams.length === 0 ? (

          <div className="empty-state">

            <h3>
              No teams available
            </h3>

            <p>
              There are currently no teams
              in the system.
            </p>

          </div>

        ) : (

          <div className="teams-table-wrapper">

            <table className="teams-table">

              <thead>

                <tr>

                  <th className="team-id-column">
                    ID
                  </th>

                  <th className="team-name-column">
                    Name
                  </th>

                  <th className="team-description-column">
                    Description
                  </th>

                  <th className="team-members-column">
                    Members
                  </th>

                  <th className="team-actions-column">
                    Actions
                  </th>

                </tr>

              </thead>


              <tbody>

                {teams.map((team) => (

                  <tr key={team.id}>

                    <td className="team-id-column">
                      {team.id}
                    </td>


                    <td className="team-name-column">

                      <strong>
                        {team.name}
                      </strong>

                    </td>


                    <td className="team-description-column">

                      {team.description ||
                        "-"}

                    </td>


                    <td className="team-members-column">

                      {Array.isArray(
                        team.members
                      )
                        ? team.members.length
                        : team.member_count ??
                          "-"}

                    </td>


                    <td className="team-actions-column">

                      <Button
                        onClick={() =>
                          navigate(
                            `/teams/${team.id}`
                          )
                        }
                      >
                        View Team
                      </Button>

                    </td>

                  </tr>

                ))}

              </tbody>

            </table>

          </div>

        )}

      </Card>

    </div>
  );
};


export default Teams;