import React from 'react';
import { appointmentAPI } from '../utils/api';

const AppointmentList = ({ appointments, userRole }) => {
  const handleCancelAppointment = async (appointmentId) => {
    if (window.confirm('Are you sure you want to cancel this appointment?')) {
      try {
        await appointmentAPI.update(appointmentId, { status: 'cancelled' });
        window.location.reload();
      } catch (error) {
        alert('Error canceling appointment: ' + error.message);
      }
    }
  };

  if (appointments.length === 0) {
    return (
      <div className="card">
        <p className="text-muted">No appointments found</p>
      </div>
    );
  }

  return (
    <div className="card">
      <div className="card-header">
        <h3>Appointments</h3>
      </div>

      <table>
        <thead>
          <tr>
            <th>Date & Time</th>
            <th>{userRole === 'patient' ? 'Doctor' : 'Patient'}</th>
            <th>Reason</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {appointments.map((apt) => (
            <tr key={apt.id}>
              <td>{new Date(apt.scheduled_at).toLocaleString()}</td>
              <td>
                {userRole === 'patient'
                  ? apt.doctor?.full_name || 'Dr. Unknown'
                  : apt.patient?.full_name || 'Unknown'}
              </td>
              <td>{apt.reason || '-'}</td>
              <td>
                <span
                  className={`badge ${
                    apt.status === 'completed'
                      ? 'success'
                      : apt.status === 'cancelled'
                      ? 'danger'
                      : 'info'
                  }`}
                >
                  {apt.status}
                </span>
              </td>
              <td>
                {apt.status === 'scheduled' && userRole === 'patient' && (
                  <button
                    className="danger"
                    onClick={() => handleCancelAppointment(apt.id)}
                    style={{ fontSize: '12px', padding: '0.25rem 0.5rem' }}
                  >
                    Cancel
                  </button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default AppointmentList;
