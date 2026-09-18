import api from "./api";

const notificationService = {
  // Get all notifications
  getNotifications: async () => {
    const response = await api.get("/notifications");
    return response.data;
  },

  // Get unread notifications
  getUnreadNotifications: async () => {
    const response = await api.get("/notifications/unread");
    return response.data;
  },

  // Mark notification as read
  markAsRead: async (notificationId) => {
    const response = await api.put(
      `/notifications/${notificationId}/read`
    );

    return response.data;
  },

  // Mark all notifications as read
  markAllAsRead: async () => {
    const response = await api.put(
      "/notifications/mark-all-read"
    );

    return response.data;
  },

  // Delete notification
  deleteNotification: async (notificationId) => {
    const response = await api.delete(
      `/notifications/${notificationId}`
    );

    return response.data;
  },
};

export default notificationService;