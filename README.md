# MediBook

MediBook is an advanced full-stack Hospital Appointment Booking System built with FastAPI,
SQLite, and a modern React frontend. It supports patient and doctor management, appointment
scheduling, real-time messaging, file handling, and an automated trigger system for notifications.

## Features

### Core Features
- Patient and Doctor registration with JWT authentication
- Appointment booking, confirmation, and management
- Specialization-based doctor search
- Doctor availability and scheduling

### Advanced Features
- **Real-time Messaging**: Direct communication between patients and doctors
- **File Management**: Upload and share medical documents (profiles, reports, prescriptions)
- **Notifications**: Automated trigger system for appointment reminders, status updates, and alerts
- **Role-based Access**: Patient, Doctor, and Admin roles with specific permissions
- **Admin Dashboard**: System administration and trigger configuration

## Tech Stack

- **Backend**: FastAPI, SQLAlchemy, SQLite, Python
- **Frontend**: React 18, React Router, Axios, modern JavaScript
- **Auth**: JWT (HS256)
- **Database**: SQLite with SQLAlchemy ORM

## Project Structure

```
.
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── database.py             # SQLAlchemy configuration
│   ├── requirements.txt         # Python dependencies
│   ├── models/                 # SQLAlchemy models
│   │   ├── user.py            # User model (Patient/Doctor)
│   │   ├── appointment.py      # Appointment model
│   │   ├── prescription.py     # Prescription model
│   │   ├── file.py            # File upload model
│   │   ├── message.py         # Message/Chat model
│   │   └── trigger.py         # Notifications & Triggers
│   ├── routes/                 # API endpoints
│   │   ├── auth.py            # Authentication endpoints
│   │   ├── appointments.py     # Appointment management
│   │   ├── doctors.py          # Doctor listings
│   │   ├── prescriptions.py    # Prescription management
│   │   ├── files.py           # File upload/management
│   │   ├── messages.py        # Messaging system
│   │   └── triggers.py        # Notifications & Triggers
│   ├── schemas/                # Pydantic schemas
│   └── utils/                  # Helper functions
│       ├── auth.py
│       └── email.py
├── frontend/
│   ├── package.json            # npm dependencies
│   ├── public/
│   │   └── index.html
│   └── src/
│       ├── App.js              # Main app component
│       ├── App.css             # Global styles
│       ├── index.js            # React entry point
│       ├── context/            # React context
│       │   └── AuthContext.js  # Authentication state
│       ├── utils/
│       │   └── api.js          # API client
│       ├── pages/              # Page components
│       │   ├── LoginPage.js
│       │   ├── RegisterPage.js
│       │   ├── DashboardPage.js
│       │   ├── DoctorPage.js
│       │   └── AdminPage.js
│       └── components/         # Reusable components
│           ├── Navbar.js
│           ├── MessagePanel.js
│           ├── NotificationPanel.js
│           ├── AppointmentList.js
│           └── FileUpload.js
└── README.md
```

## Setup & Installation

### Backend Setup

1. Create and activate a virtual environment:
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the FastAPI server:
```bash
uvicorn backend.main:app --reload
```

The backend will be available at `http://localhost:8000`
API documentation: `http://localhost:8000/docs`

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Configure environment (optional):
```bash
# Copy .env file (already configured for localhost)
cat .env  # REACT_APP_API_URL=http://localhost:8000/api
```

4. Start the development server:
```bash
npm start
```

The frontend will be available at `http://localhost:3000`

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `GET /api/auth/me` - Get current user

### Appointments
- `GET /api/appointments` - List appointments
- `POST /api/appointments` - Create appointment
- `PATCH /api/appointments/{id}` - Update appointment
- `DELETE /api/appointments/{id}` - Cancel appointment

### Doctors
- `GET /api/doctors` - List doctors
- `GET /api/doctors/{id}` - Get doctor details
- `GET /api/doctors/{id}/availability` - Get doctor availability

### Files
- `POST /api/files/upload` - Upload file
- `GET /api/files` - List files
- `PATCH /api/files/{id}` - Update file metadata
- `DELETE /api/files/{id}` - Delete file

### Messages
- `POST /api/messages` - Send message
- `GET /api/messages` - List messages
- `GET /api/messages/conversation/{user_id}` - Get conversation
- `PATCH /api/messages/{id}` - Mark message as read
- `DELETE /api/messages/{id}` - Delete message

### Notifications
- `GET /api/notifications` - List notifications
- `PATCH /api/notifications/{id}` - Mark notification as read
- `POST /api/notifications/mark-all-read` - Mark all as read
- `DELETE /api/notifications/{id}` - Delete notification

### Triggers (Admin only)
- `GET /api/triggers` - List triggers
- `POST /api/triggers` - Create trigger
- `PATCH /api/triggers/{id}` - Update trigger
- `DELETE /api/triggers/{id}` - Delete trigger

## Demo Credentials

After running the backend, use these credentials to test:

**Patient:**
- Email: `patient@medibook.local`
- Password: `patient123`

**Doctor:**
- Email: `priya.menon@medibook.local`
- Password: `doctor123`

## Development

### Backend Development
- Modify models in `backend/models/`
- Add routes in `backend/routes/`
- Create schemas in `backend/schemas/`
- Tests can be added in `backend/tests/`

### Frontend Development
- Add pages in `frontend/src/pages/`
- Create components in `frontend/src/components/`
- Update styles in `frontend/src/App.css`
- Manage state with `frontend/src/context/`

## Features Demo

1. **Authentication**: Login/Register with different roles
2. **Dashboard**: View appointments, messages, notifications, files
3. **Appointments**: Book, view, and cancel appointments
4. **Messaging**: Direct messages between patients and doctors
5. **File Management**: Upload and share medical documents
6. **Notifications**: Receive alerts for appointments and messages
7. **Doctor Portal**: View patient list and appointment schedule
8. **Admin Dashboard**: Manage system triggers and settings

## Future Enhancements

- Video consultation integration
- Payment gateway integration
- Advanced search and filtering
- Prescription generation and sharing
- Patient health records
- Analytics and reporting
- Mobile app

## License

This project is open source and available under the MIT License.

```

The API will run at http://127.0.0.1:8000.

### Frontend

Open frontend/index.html in a browser. If you use a local file server, keep it
pointed at the frontend folder. The app uses CORS to call the API.

## Seed Accounts

When the app starts, it seeds demo accounts if the database is empty:

- Doctors
  - priya.menon@medibook.local / doctor123
  - arjun.rao@medibook.local / doctor123
  - aisha.khan@medibook.local / doctor123
- Patient
  - patient@medibook.local / patient123

## API Overview

### Auth

- POST /api/auth/register
- POST /api/auth/login
- GET /api/auth/me

### Doctors

- GET /api/doctors
- GET /api/doctors/{doctor_id}/availability

### Appointments

- GET /api/appointments
- POST /api/appointments
- POST /api/appointments/{id}/cancel
- POST /api/appointments/{id}/reschedule

### Prescriptions

- POST /api/prescriptions
- GET /api/prescriptions/{appointment_id}

## Email Configuration

The SMTP settings are defined in backend/utils/email.py. Update the
credentials to your SMTP provider before using email notifications.

## Notes

- All times are stored and returned in UTC.
- The frontend uses native browser dialogs for rescheduling.
- Doctor availability is generated from fixed daily slots.

## Troubleshooting

- If JWT errors occur, clear localStorage and login again.
- If CORS errors occur, ensure the API is running on port 8000.
- If SQLite is locked, stop and restart the server.

## License

This project is provided for educational purposes.
