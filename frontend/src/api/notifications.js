import { request } from './client';

export const notificationsApi = {
  getNotifications: async (limit = 50) => {
    return await request(`/notifications?limit=${limit}`);
  },

  getUnreadCount: async () => {
    return await request('/notifications/unread-count');
  },

  markAsRead: async (id) => {
    return await request(`/notifications/${id}/read`, {
      method: 'PATCH',
    });
  },

  markAllAsRead: async () => {
    return await request('/notifications/read-all', {
      method: 'POST',
    });
  },
};
