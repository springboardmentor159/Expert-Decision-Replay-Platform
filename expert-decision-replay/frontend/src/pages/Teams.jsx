import React, { useEffect, useState } from "react";
import teamService from "../services/teamService";

const Teams = () => {
  const [teams, setTeams] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadTeams = async () => {
    try {
      setLoading(true);
      setError("");

      const response = await teamService.getTeams();

      setTeams(response.data || response || []);
    } catch (err) {
      console.error("Error loading teams:", err);
      setError("Unable to load teams.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTeams();
  }, []);

  return (
    <div className="p-6">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-3 mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">
            Teams
          </h1>

          <p className="text-gray-600 mt-1">
            View and manage teams in the organization.
          </p>
        </div>

        <button
          onClick={loadTeams}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
        >
          Refresh
        </button>
      </div>

      {loading && (
        <div className="bg-white rounded-xl shadow p-6">
          <p className="text-gray-600">Loading teams...</p>
        </div>
      )}

      {error && (
        <div className="bg-red-100 text-red-700 rounded-lg p-4 mb-4">
          {error}
        </div>
      )}

      {!loading && !error && teams.length === 0 && (
        <div className="bg-white rounded-xl shadow p-6 text-center">
          <p className="text-gray-600">No teams found.</p>
        </div>
      )}

      {!loading && teams.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
          {teams.map((team) => (
            <div
              key={team.id}
              className="bg-white rounded-xl shadow p-5 hover:shadow-lg transition"
            >
              <div className="flex items-center gap-3 mb-4">
                <div className="w-12 h-12 rounded-full bg-blue-100 flex items-center justify-center">
                  <span className="text-xl font-bold text-blue-700">
                    {(team.name || "T").charAt(0).toUpperCase()}
                  </span>
                </div>

                <div>
                  <h2 className="text-lg font-semibold text-gray-800">
                    {team.name || `Team #${team.id}`}
                  </h2>

                  <p className="text-sm text-gray-500">
                    Team ID: {team.id}
                  </p>
                </div>
              </div>

              <p className="text-gray-600 text-sm mb-4">
                {team.description || "No team description available."}
              </p>

              <div className="space-y-2 text-sm text-gray-600">
                <p>
                  <strong>Manager ID:</strong>{" "}
                  {team.manager_id || team.owner_id || "-"}
                </p>

                <p>
                  <strong>Members:</strong>{" "}
                  {team.member_count ||
                    team.members_count ||
                    team.members?.length ||
                    0}
                </p>

                <p>
                  <strong>Status:</strong>{" "}
                  {team.status || "Active"}
                </p>

                {team.created_at && (
                  <p>
                    <strong>Created At:</strong>{" "}
                    {new Date(team.created_at).toLocaleDateString()}
                  </p>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Teams;