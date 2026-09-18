import api from "./api";

const teamService = {
  getTeams: async () => {
    const response = await api.get("/teams");

    return response.data;
  },

  createTeam: async (teamData) => {
    const response = await api.post("/teams", teamData);

    return response.data;
  },

  updateTeam: async (teamId, teamData) => {
    const response = await api.put(`/teams/${teamId}`, teamData);

    return response.data;
  },

  deleteTeam: async (teamId) => {
    const response = await api.delete(`/teams/${teamId}`);

    return response.data;
  },
};

export default teamService;