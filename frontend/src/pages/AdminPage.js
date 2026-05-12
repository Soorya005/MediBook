import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import Navbar from '../components/Navbar';

const AdminPage = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('triggers');
  const [triggers, setTriggers] = useState([]);
  const [stats, setStats] = useState({
    total_users: 0,
    total_appointments: 0,
    total_messages: 0,
  });

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div>
      <Navbar user={user} onLogout={handleLogout} />
      
      <div className="container">
        <div style={{ marginBottom: '2rem' }}>
          <h2>Admin Dashboard</h2>
          <p className="text-muted">System Administration and Configuration</p>
        </div>

        <div className="grid" style={{ marginBottom: '2rem' }}>
          <div className="card">
            <div className="card-header">
              <h4>Total Users</h4>
            </div>
            <p style={{ fontSize: '28px', fontWeight: 'bold' }}>{stats.total_users}</p>
          </div>
          <div className="card">
            <div className="card-header">
              <h4>Total Appointments</h4>
            </div>
            <p style={{ fontSize: '28px', fontWeight: 'bold' }}>{stats.total_appointments}</p>
          </div>
          <div className="card">
            <div className="card-header">
              <h4>Total Messages</h4>
            </div>
            <p style={{ fontSize: '28px', fontWeight: 'bold' }}>{stats.total_messages}</p>
          </div>
        </div>

        <div style={{ display: 'flex', gap: '1rem', marginBottom: '1.5rem' }}>
          <button 
            className={activeTab === 'triggers' ? '' : 'secondary'}
            onClick={() => setActiveTab('triggers')}
          >
            Manage Triggers
          </button>
          <button 
            className={activeTab === 'settings' ? '' : 'secondary'}
            onClick={() => setActiveTab('settings')}
          >
            System Settings
          </button>
        </div>

        {activeTab === 'triggers' && (
          <div className="card">
            <div className="card-header">
              <h3>Workflow Triggers</h3>
            </div>
            <p className="text-muted">Configure automated triggers and notifications here.</p>
            <ul>
              <li>Appointment reminders - Email 24 hours before appointment</li>
              <li>Prescription notifications - Notify patient when prescription is ready</li>
              <li>File upload alerts - Alert doctor when patient uploads files</li>
              <li>Message notifications - Notify users of new messages</li>
            </ul>
          </div>
        )}

        {activeTab === 'settings' && (
          <div className="card">
            <div className="card-header">
              <h3>System Settings</h3>
            </div>
            <div className="form-group mt-2">
              <label>Max File Size (MB)</label>
              <input type="number" defaultValue="10" />
            </div>
            <div className="form-group">
              <label>Appointment Reminder Hours Before</label>
              <input type="number" defaultValue="24" />
            </div>
            <button>Save Settings</button>
          </div>
        )}
      </div>
    </div>
  );
};

export default AdminPage;
