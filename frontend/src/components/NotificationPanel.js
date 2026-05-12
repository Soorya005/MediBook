import React from 'react';
import { notificationAPI } from '../utils/api';

const NotificationPanel = ({ notifications, onRefresh }) => {
  const handleMarkAsRead = async (notificationId) => {
    try {
      await notificationAPI.markAsRead(notificationId);
      onRefresh();
    } catch (error) {
      alert('Error marking as read: ' + error.message);
    }
  };

  const handleDelete = async (notificationId) => {
    try {
      await notificationAPI.delete(notificationId);
      onRefresh();
    } catch (error) {
      alert('Error deleting notification: ' + error.message);
    }
  };

  return (
    <div className="card">
      <div className="card-header">
        <h3>Notifications</h3>
      </div>

      {notifications.length === 0 ? (
        <p className="text-muted">No notifications</p>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {notifications.map((notif) => (
            <div
              key={notif.id}
              style={{
                padding: '1rem',
                backgroundColor: notif.is_read ? '#f9f9f9' : '#f0f8ff',
                borderLeft: `4px solid ${notif.is_read ? '#ccc' : '#007bff'}`,
                borderRadius: '4px',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'start',
              }}
            >
              <div>
                <h5 style={{ margin: '0 0 0.5rem 0' }}>{notif.title}</h5>
                <p style={{ margin: '0.25rem 0' }}>{notif.message}</p>
                <p style={{ fontSize: '12px', color: '#999', margin: '0.5rem 0 0 0' }}>
                  {new Date(notif.created_at).toLocaleString()}
                </p>
              </div>
              <div style={{ display: 'flex', gap: '0.5rem' }}>
                {!notif.is_read && (
                  <button
                    className="secondary"
                    onClick={() => handleMarkAsRead(notif.id)}
                    style={{ fontSize: '12px', padding: '0.25rem 0.5rem' }}
                  >
                    Read
                  </button>
                )}
                <button
                  className="danger"
                  onClick={() => handleDelete(notif.id)}
                  style={{ fontSize: '12px', padding: '0.25rem 0.5rem' }}
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default NotificationPanel;
