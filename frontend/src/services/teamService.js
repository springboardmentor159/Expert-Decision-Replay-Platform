import axiosClient from "../api/axiosClient";

// Get all teams
export const getTeams = async () => {
  const response = await axiosClient.get("/teams");

  return response.data;
};


// Get one team
export const getTeam = async (teamId) => {
  const response = await axiosClient.get(
    `/teams/${teamId}`
  );

  return response.data;
};


// Create team
export const createTeam = async (teamData) => {
  const response = await axiosClient.post(
    "/teams",
    teamData
  );

  return response.data;
};


// Get team members
export const getTeamMembers = async (teamId) => {
  const response = await axiosClient.get(
    `/teams/${teamId}/members`
  );

  return response.data;
};


// Add member
export const addTeamMember = async (
  teamId,
  userId
) => {
  const response = await axiosClient.post(
    `/teams/${teamId}/members/${userId}`
  );

  return response.data;
};


// Remove member
export const removeTeamMember = async (
  teamId,
  userId
) => {
  const response = await axiosClient.delete(
    `/teams/${teamId}/members/${userId}`
  );

  return response.data;
};