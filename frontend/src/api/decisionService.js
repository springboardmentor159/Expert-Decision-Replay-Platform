import client from './client';

export const decisionService = {
  async getDecisions(params = {}) {
    const response = await client.get('/decisions', { params });
    return response.data;
  },

  async searchDecisions(params = {}) {
    const response = await client.get('/decisions/search', { params });
    return response.data;
  },

  async getDecision(id) {
    const response = await client.get(`/decisions/${id}`);
    return response.data;
  },

  async createDecision(data) {
    const response = await client.post('/decisions', data);
    return response.data;
  },

  async updateDecision(id, data) {
    const response = await client.put(`/decisions/${id}`, data);
    return response.data;
  },

  async deleteDecision(id) {
    const response = await client.delete(`/decisions/${id}`);
    return response.data;
  },

  async updateStatus(id, status) {
    const response = await client.patch(`/decisions/${id}/status`, { status });
    return response.data;
  },

  async updateRationale(id, rationale) {
    const response = await client.put(`/decisions/${id}/rationale`, { rationale });
    return response.data;
  },

  async getRationale(id) {
    const response = await client.get(`/decisions/${id}/rationale`);
    return response.data;
  },

  async getHistory(id) {
    const response = await client.get(`/decisions/${id}/history`);
    return response.data;
  },

  async getTimeline(id) {
    const response = await client.get(`/decisions/${id}/timeline`);
    return response.data;
  },

  async getVersions(id) {
    const response = await client.get(`/decisions/${id}/versions`);
    return response.data;
  },

  async getVersionDetail(id, versionNumber) {
    const response = await client.get(`/decisions/${id}/versions/${versionNumber}`);
    return response.data;
  },

  async getTags(id) {
    const response = await client.get(`/decisions/${id}/tags`);
    return response.data;
  },

  async assignTag(id, name) {
    // If name is string, ensure tag exists via /tags then assign via /decisions/{id}/tags
    let tagId = null;
    try {
      const res = await client.post('/tags', { name });
      tagId = res.data.id;
    } catch {
      const allTags = await client.get('/tags');
      const found = (allTags.data || []).find(
        (t) => t.name.toLowerCase() === name.toLowerCase()
      );
      if (found) tagId = found.id;
    }
    if (tagId) {
      const response = await client.post(`/decisions/${id}/tags`, { tag_ids: [tagId] });
      return response.data;
    }
  },

  async removeTag(id, tagId) {
    const response = await client.delete(`/decisions/${id}/tags/${tagId}`);
    return response.data;
  },
};
