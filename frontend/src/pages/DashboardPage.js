import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { appointmentAPI, messageAPI, notificationAPI, fileAPI } from '../utils/api';
import Navbar from '../components/Navbar';
import MessagePanel from '../components/MessagePanel';
import NotificationPanel from '../components/NotificationPanel';
import AppointmentList from '../components/AppointmentList';
import FileUpload from '../components/FileUpload';

const DashboardPage = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [appointments, setAppointments] = useState([]);
  const [messages, setMessages] = useState([]);
  const [notifications, setNotifications] = useState([]);
  const [files, setFiles] = useState([]);
  const [unreadMessages, setUnreadMessages] = useState(0);
  const [unreadNotifications, setUnreadNotifications] = useState(0);
  const [activeTab, setActiveTab] = useState('appointments');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadDashboardData();
    // Poll for new messages and notifications
    const interval = setInterval(loadDashboardData, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadDashboardData = async () => {
    setLoading(true);
    try {
      const [appointmentsRes, messagesRes, notificationsRes, filesRes, unreadMsgRes, unreadNotifRes] = await Promise.all([
        appointmentAPI.getAll(),
        messageAPI.getAll(),
        notificationAPI.getAll(),
        fileAPI.getAll(),
        messageAPI.getUnreadCount(),
        notificationAPI.getUnreadCount(),
      ]);

      setAppointments(appointmentsRes.data);
      setMessages(messagesRes.data);
      setNotifications(notificationsRes.data);
      setFiles(filesRes.data);
      setUnreadMessages(unreadMsgRes.data.unread_count);
      setUnreadNotifications(unreadNotifRes.data.unread_count);
    } catch (error) {
      console.error('Error loading dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div>
      <Navbar user={user} unreadMessages={unreadMessages} unreadNotifications={unreadNotifications} onLogout={handleLogout} />
      
      <div className="container">
        <div style={{ marginBottom: '2rem' }}>
          <h2>Welcome, {user?.full_name}!</h2>
          <p className="text-muted">Role: {user?.role}</p>
        </div>

        <div style={{ display: 'flex', gap: '1rem', marginBottom: '1.5rem' }}>
          <button 
            className={activeTab === 'appointments' ? '' : 'secondary'}
            onClick={() => setActiveTab('appointments')}
          >
            Appointments ({appointments.length})
          </button>
          <button 
            className={activeTab === 'messages' ? '' : 'secondary'}
            onClick={() => setActiveTab('messages')}
          >
            Messages ({unreadMessages})
          </button>
          <button 
            className={activeTab === 'notifications' ? '' : 'secondary'}
            onClick={() => setActiveTab('notifications')}
          >
            Notifications ({unreadNotifications})
          </button>
          <button 
            className={activeTab === 'files' ? '' : 'secondary'}
            onClick={() => setActiveTab('files')}
          >
            Files ({files.length})
          </button>
        </div>

        {loading && <div className="alert info">Loading...</div>}

        {activeTab === 'appointments' && (
          <div>
            <AppointmentList appointments={appointments} userRole={user?.role} />
          </div>
        )}

        {activeTab === 'messages' && (
          <div>
            <MessagePanel messages={messages} onRefresh={loadDashboardData} />
          </div>
        )}

        {activeTab === 'notifications' && (
          <div>
            <NotificationPanel notifications={notifications} onRefresh={loadDashboardData} />
          </div>
        )}

        {activeTab === 'files' && (
          <div>
            <FileUpload onUploadSuccess={loadDashboardData} />
            <div className="mt-3">
              <h3>Your Files</h3>
              {files.length === 0 ? (
                <p className="text-muted">No files uploaded yet</p>
              ) : (
                <table>
                  <thead>
                    <tr>
                      <th>Filename</th>
                      <th>Type</th>
                      <th>Size</th>
                      <th>Uploaded</th>
                      <th>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {files.map((file) => (
                      <tr key={file.id}>
                        <td>{file.filename}</td>
                        <td>{file.file_type}</td>
                        <td>{(file.file_size / 1024).toFixed(2)} KB</td>
                        <td>{new Date(file.created_at).toLocaleDateString()}</td>
                        <td><span className="badge success">{file.is_public}</span></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default DashboardPage;
