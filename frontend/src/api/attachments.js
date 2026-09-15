import { request } from './client';

export const attachmentsApi = {
  getDecisionAttachments: async (decisionId) => {
    return await request(`/decisions/${decisionId}/attachments`);
  },

  uploadAttachment: async (decisionId, file) => {
    const formData = new FormData();
    formData.append('file', file);
    return await request(`/decisions/${decisionId}/attachments`, {
      method: 'POST',
      body: formData,
    });
  },

  deleteAttachment: async (id) => {
    return await request(`/attachments/${id}`, {
      method: 'DELETE',
    });
  },

  getArchive: async (limit = 100) => {
    return await request(`/attachments/archive?limit=${limit}`);
  },

  downloadAttachmentBlob: async (id) => {
    return await request(`/attachments/${id}/download`, {
      responseType: 'blob',
    });
  },
};
