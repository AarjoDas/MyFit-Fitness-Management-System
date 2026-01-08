# Fitness Club Management System

Full-stack fitness club management application with FastAPI backend and React frontend.

## Project Structure

```
Project/
├── backend/          # FastAPI backend API
│   ├── app.py        # FastAPI application
│   ├── schemas.py    # Pydantic models
│   ├── models/       # SQLAlchemy ORM models
│   ├── services/     # Business logic layer
│   ├── database/     # Database configuration
│   └── client/       # CLI client (legacy)
├── frontend/         # React + TypeScript frontend
│   ├── src/          # React source code
│   └── public/       # Static assets
└── docs/             # Documentation
```

## Quick Start

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure database in `database/connection.py`

4. Initialize database:
```bash
python reset_database.py
```

5. Start the API server:
```bash
# Option 1: If virtual environment is activated
uvicorn app:app --reload

# Option 2: Using Python module syntax (works without activation)
python -m uvicorn app:app --reload
```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm start
```

The app will open at `http://localhost:3000`

## Features

### Member Portal
- Register as a new member
- View dashboard with upcoming sessions and classes
- Book personal training sessions
- Register for group classes

### Trainer Portal
- View schedule (classes and PT sessions)
- Search and view member profiles
- Update session status and notes

### Admin Portal
- Manage rooms
- Manage trainers
- Create, reschedule, and cancel group classes
- View all members

## Technologies

### Backend
- FastAPI
- SQLAlchemy
- PostgreSQL
- Pydantic

### Frontend
- React 18
- TypeScript
- Tailwind CSS
- React Router
- Axios

## API Documentation

When the backend is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Documentation

See `docs/README.md` for detailed project documentation including ER model and architecture details.

