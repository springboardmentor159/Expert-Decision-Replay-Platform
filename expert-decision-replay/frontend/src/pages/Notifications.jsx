import React, { useEffect, useState } from "react";
import notificationService from "../services/notificationService";
import "./Notifications.css";

const Notifications = () => {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadNotifications = async () => {
    try {
      setLoading(true);
      setError("");

      const response = await notificationService.getNotifications();

      const data = response?.data || response || [];

      setNotifications(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error("Error loading notifications:", err);
      setError("Unable to load notifications.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadNotifications();
  }, []);

  const handleMarkAsRead = async (notificationId) => {
    try {
      await notificationService.markAsRead(notificationId);

      setNotifications((previousNotifications) =>
        previousNotifications.map((notification) =>
          notification.id === notificationId
            ? {
                ...notification,
                is_read: true,
                read: true,
              }
            : notification
        )
      );
    } catch (err) {
      console.error("Error marking notification as read:", err);
      alert("Unable to mark notification as read.");
    }
  };

  const handleMarkAllAsRead = async () => {
    try {
      await notificationService.markAllAsRead();

      setNotifications((previousNotifications) =>
        previousNotifications.map((notification) => ({
          ...notification,
          is_read: true,
          read: true,
        }))
      );
    } catch (err) {
      console.error("Error marking all notifications as read:", err);
      alert("Unable to mark all notifications as read.");
    }
  };

  const unreadCount = notifications.filter(
    (notification) =>
      notification.is_read === false ||
      notification.is_read === 0 ||
      notification.read === false
  ).length;

  const getNotificationTitle = (notification) => {
    return (
      notification.title ||
      notification.subject ||
      "System Notification"
    );
  };

  const getNotificationMessage = (notification) => {
    return (
      notification.message ||
      notification.description ||
      notification.content ||
      "No message available."
    );
  };

  const formatDate = (dateValue) => {
    if (!dateValue) {
      return "-";
    }

    const date = new Date(dateValue);

    if (Number.isNaN(date.getTime())) {
      return "-";
    }

    return date.toLocaleString();
  };

  return (
    <div className="notifications-page">
      {/* Page Header */}
      <div className="notifications-header">
        <div>
          <div className="notifications-breadcrumb">
            Workspace / Notifications
          </div>

          <h1>Notifications</h1>

          <p>
            View updates and important system alerts.
          </p>
        </div>

        <div className="notifications-header-actions">
          <button
            type="button"
            onClick={loadNotifications}
            className="notification-refresh-btn"
          >
            ↻ Refresh
          </button>

          {unreadCount > 0 && (
            <button
              type="button"
              onClick={handleMarkAllAsRead}
              className="notification-read-all-btn"
            >
              ✓ Mark All as Read
            </button>
          )}
        </div>
      </div>

      {/* Notification Summary */}
      <div
        className={`notification-summary ${
          unreadCount > 0
            ? "notification-summary-unread"
            : "notification-summary-clear"
        }`}
      >
        <div className="summary-icon">
          {unreadCount > 0 ? "!" : "✓"}
        </div>

        <div>
          <strong>
            {unreadCount > 0
              ? `${unreadCount} unread notification${
                  unreadCount !== 1 ? "s" : ""
                }`
              : "All notifications are read"}
          </strong>

          <span>
            {unreadCount > 0
              ? "You have new updates that need your attention."
              : "There are no unread notifications at the moment."}
          </span>
        </div>
      </div>

      {/* Loading */}
      {loading && (
        <div className="notifications-state-card">
          <div className="notification-spinner"></div>
          <h3>Loading notifications...</h3>
          <p>Please wait while we fetch your notifications.</p>
        </div>
      )}

      {/* Error */}
      {!loading && error && (
        <div className="notifications-error">
          <div className="error-icon">!</div>

          <div>
            <strong>Unable to load notifications</strong>
            <p>{error}</p>
          </div>

          <button
            type="button"
            onClick={loadNotifications}
            className="retry-btn"
          >
            Try Again
          </button>
        </div>
      )}

      {/* Empty State */}
      {!loading && !error && notifications.length === 0 && (
        <div className="notifications-state-card">
          <div className="empty-notification-icon">✓</div>

          <h3>No notifications</h3>

          <p>
            You don't have any notifications at the moment.
          </p>
        </div>
      )}

      {/* Notification List */}
      {!loading && !error && notifications.length > 0 && (
        <div className="notifications-section">
          <div className="notifications-section-header">
            <div>
              <h2>Recent Notifications</h2>
              <p>
                {notifications.length} notification
                {notifications.length !== 1 ? "s" : ""} found
              </p>
            </div>

            {unreadCount > 0 && (
              <span className="unread-count-badge">
                {unreadCount} New
              </span>
            )}
          </div>

          <div className="notification-list">
            {notifications.map((notification) => {
              const isRead =
                notification.is_read === true ||
                notification.is_read === 1 ||
                notification.read === true;

              return (
                <div
                  key={notification.id}
                  className={`notification-card ${
                    isRead
                      ? "notification-card-read"
                      : "notification-card-unread"
                  }`}
                >
                  <div
                    className={`notification-icon ${
                      isRead
                        ? "notification-icon-read"
                        : "notification-icon-unread"
                    }`}
                  >
                    {isRead ? "✓" : "!"}
                  </div>

                  <div className="notification-content">
                    <div className="notification-title-row">
                      <h3>{getNotificationTitle(notification)}</h3>

                      {!isRead && (
                        <span className="new-badge">
                          New
                        </span>
                      )}
                    </div>

                    <p className="notification-message">
                      {getNotificationMessage(notification)}
                    </p>

                    <div className="notification-meta">
                      <span>
                        <strong>ID:</strong>{" "}
                        {notification.id}
                      </span>

                      <span>
                        <strong>Date:</strong>{" "}
                        {formatDate(notification.created_at)}
                      </span>
                    </div>
                  </div>

                  <div className="notification-action">
                    {!isRead ? (
                      <button
                        type="button"
                        onClick={() =>
                          handleMarkAsRead(notification.id)
                        }
                        className="mark-read-btn"
                      >
                        ✓ Mark as Read
                      </button>
                    ) : (
                      <span className="read-status">
                        ✓ Read
                      </span>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};

export default Notifications;