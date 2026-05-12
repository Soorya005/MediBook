import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { appointmentAPI, messageAPI } from '../utils/api';
import Navbar from '../components/Navbar';

const DoctorPage = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [appointments, setAppointments] = useState([]);
  const [patients, setPatients] = useState([]);
  const [activeTab, setActiveTab] = useState('schedule');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadDoctorData();
  }, []);

  const loadDoctorData = async () => {
    setLoading(true);
    try {
      const appointmentsRes = await appointmentAPI.getAll({ doctor_id: user?.id });
      setAppointments(appointmentsRes.data);
      
      // Extract unique patients
      const uniquePatients = [...new Set(appointmentsRes.data.map((apt) => apt.patient_id))];
      setPatients(uniquePatients);
    } catch (error) {
      console.error('Error loading doctor data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const handleUpdateAppointment = async (appointmentId, newStatus) => {
    try {
      await appointmentAPI.update(appointmentId, { status: newStatus });
      loadDoctorData();
    } catch (error) {
      alert('Error updating appointment: ' + error.message);
    }
  };

  return (
    <div>
      <Navbar user={user} onLogout={handleLogout} />
      
      <div className="container">
        <div style={{ marginBottom: '2rem' }}>
          <h2>Doctor Dashboard</h2>
          <p className="text-muted">Specialization: {user?.specialization}</p>
        </div>

        <div style={{ display: 'flex', gap: '1rem', marginBottom: '1.5rem' }}>
          <button 
            className={activeTab === 'schedule' ? '' : 'secondary'}
            onClick={() => setActiveTab('schedule')}
          >
            Schedule ({appointments.length})
          </button>
          <button 
            className={activeTab === 'patients' ? '' : 'secondary'}
            onClick={() => setActiveTab('patients')}
          >
            Patients ({patients.length})
          </button>
        </div>

        {loading && <div className="alert info">Loading...</div>}

        {activeTab === 'schedule' && (
          <div className="card">
            <div className="card-header">
              <h3>Your Appointments</h3>
            </div>
            {appointments.length === 0 ? (
              <p className="text-muted">No appointments scheduled</p>
            ) : (
              <table>
                <thead>
                  <tr>
                    <th>Patient</th>
                    <th>Date</th>
                    <th>Reason</th>
                    <th>Status</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {appointments.map((apt) => (
                    <tr key={apt.id}>
                      <td>{apt.patient?.full_name || 'Unknown'}</td>
                      <td>{new Date(apt.scheduled_at).toLocaleString()}</td>
                      <td>{apt.reason || '-'}</td>
                      <td>
                        <span className={`badge ${apt.status === 'completed' ? 'success' : apt.status === 'cancelled' ? 'danger' : 'info'}`}>
                          {apt.status}
                        </span>
                      </td>
                      <td>
                        {apt.status === 'scheduled' && (
                          <>
                            <button 
                              className="secondary" 
                              style={{ marginRight: '0.5rem' }}
                              onClick={() => handleUpdateAppointment(apt.id, 'confirmed')}
                            >
                              Confirm
                            </button>
                            <button 
                              className="danger"
                              onClick={() => handleUpdateAppointment(apt.id, 'cancelled')}
                            >
                              Cancel
                            </button>
                          </>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        )}

        {activeTab === 'patients' && (
          <div className="card">
            <div className="card-header">
              <h3>Your Patients</h3>
            </div>
            <p className="text-muted">You have {patients.length} patient(s) with scheduled appointments.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default DoctorPage;
