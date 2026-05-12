# Quick Start Guide

## Prerequisites
- Python 3.8+
- Node.js 16+
- npm 7+

## 5-Minute Quick Start

### 1. Start the Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Backend runs on: `http://localhost:8000`

### 2. Start the Frontend (in another terminal)

```bash
cd frontend
npm install
npm start
```

Frontend runs on: `http://localhost:3000`

### 3. Login with Demo Credentials

**Patient Account:**
- Email: patient@medibook.local
- Password: patient123

**Doctor Account:**
- Email: priya.menon@medibook.local
- Password: doctor123

## Key Features to Explore

### Patient Features
1. **Dashboard** - View all appointments, messages, and files
2. **Messaging** - Send messages to your doctor
3. **File Upload** - Upload medical documents
4. **Notification** - Receive appointment reminders

### Doctor Features
1. **Doctor Dashboard** - View your appointments
2. **Patient Management** - See list of patients
3. **Appointment Confirmation** - Accept/Cancel appointments
4. **Messaging** - Communicate with patients

### Admin Features
1. **Admin Dashboard** - System statistics
2. **Trigger Management** - Configure automated workflows
3. **System Settings** - Manage application settings

## API Documentation

After backend is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Troubleshooting

### Backend Issues

**Port 8000 already in use:**
```bash
uvicorn main:app --reload --port 8001
```

**Module not found:**
```bash
pip install -r requirements.txt --force-reinstall
```

### Frontend Issues

**Port 3000 already in use:**
```bash
PORT=3001 npm start
```

**Dependencies issues:**
```bash
rm -rf node_modules package-lock.json
npm install
```

## Project Structure Tips

- **Backend Models**: `backend/models/` - Database schema
- **Backend Routes**: `backend/routes/` - API endpoints
- **Frontend Pages**: `frontend/src/pages/` - Page components
- **Frontend Components**: `frontend/src/components/` - Reusable UI components
- **API Client**: `frontend/src/utils/api.js` - API calls

## Next Steps

1. Explore the API docs at http://localhost:8000/docs
2. Create a new user account
3. Book an appointment
4. Send a message to a doctor
5. Upload a medical file
6. Check notifications and messages

## Development Commands

### Backend
```bash
# Run tests
pytest

# Format code
black backend/

# Lint
flake8 backend/
```

### Frontend
```bash
# Run tests
npm test

# Build for production
npm run build

# Analyze bundle
npm run analyze
```

## Additional Resources

- FastAPI Docs: https://fastapi.tiangolo.com/
- React Docs: https://react.dev/
- SQLAlchemy Docs: https://docs.sqlalchemy.org/
