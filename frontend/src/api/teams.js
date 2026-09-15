import { request } from './client';

export const teamsApi = {
  getTeams: async () => {
    return await request('/teams');
  },

  getTeam: async (id) => {
    return await request(`/teams/${id}`);
  },

  createTeam: async (data) => {
    return await request('/teams', {
      method: 'POST',
      body: data,
    });
  },

  updateTeam: async (id, data) => {
    return await request(`/teams/${id}`, {
      method: 'PUT',
      body: data,
    });
  },

  deleteTeam: async (id) => {
    return await request(`/teams/${id}`, {
      method: 'DELETE',
    });
  },

  addMember: async (teamId, userId) => {
    return await request(`/teams/${teamId}/members`, {
      method: 'POST',
      body: { user_id: userId },
    });
  },

  removeMember: async (teamId, userId) => {
    return await request(`/teams/${teamId}/members/${userId}`, {
      method: 'DELETE',
    });
  },
};
