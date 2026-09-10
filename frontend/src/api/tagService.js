import client from './client';

export const tagService = {
  async getTags() {
    const response = await client.get('/tags');
    return response.data;
  },

  async createTag(name) {
    try {
      const response = await client.post('/tags', { name });
      return response.data;
    } catch (err) {
      // If tag already exists, find existing tag
      const allTags = await client.get('/tags');
      const found = (allTags.data || []).find(
        (t) => t.name.toLowerCase() === name.toLowerCase()
      );
      if (found) return found;
      throw err;
    }
  },

  async assignTagsToDecision(decisionId, tagIds) {
    const response = await client.post(`/decisions/${decisionId}/tags`, { tag_ids: tagIds });
    return response.data;
  },

  async assignTagByName(decisionId, tagName) {
    const tag = await this.createTag(tagName);
    return this.assignTagsToDecision(decisionId, [tag.id]);
  },
};
