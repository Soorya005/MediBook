import React from 'react';
import { Link } from 'react-router-dom';

const Navbar = ({ user, unreadMessages = 0, unreadNotifications = 0, onLogout }) => {
  return (
    <nav className="navbar">
      <h1>
        <Link to="/dashboard" style={{ color: 'white', textDecoration: 'none' }}>
          🏥 MediBook
        </Link>
      </h1>
      
      <div className="navbar-links">
        <Link to="/dashboard">Dashboard</Link>
        {user?.role === 'doctor' && <Link to="/doctor">Doctor</Link>}
        {user?.role === 'admin' && <Link to="/admin">Admin</Link>}
        
        {unreadMessages > 0 && (
          <span style={{ backgroundColor: '#fc5a5a', borderRadius: '50%', width: '24px', height: '24px', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '12px' }}>
            {unreadMessages}
          </span>
        )}
        
        {unreadNotifications > 0 && (
          <span style={{ backgroundColor: '#ffa500', borderRadius: '50%', width: '24px', height: '24px', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '12px' }}>
            {unreadNotifications}
          </span>
        )}
        
        <button onClick={onLogout}>Logout</button>
      </div>
    </nav>
  );
};

export default Navbar;
