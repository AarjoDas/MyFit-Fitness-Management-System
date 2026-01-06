# Fitness Club Backend API

FastAPI backend for the Fitness Club Management System.

## Project Structure

```
backend/
├── app.py              # FastAPI application and routes
├── schemas.py          # Pydantic models for request/response validation
├── main.py             # CLI entry point
├── reset_database.py   # Database reset utility
├── requirements.txt    # Python dependencies
├── database/           # Database configuration and utilities
│   ├── connection.py   # SQLAlchemy engine and session setup
│   ├── seed_data.py    # Database seeding
│   └── schema_extras.py # Additional schema definitions
├── models/             # SQLAlchemy ORM models
│   ├── member.py
│   ├── trainer.py
│   ├── admin_staff.py
│   ├── room.py
│   ├── group_class.py
│   ├── personal_training_session.py
│   └── class_enrollment.py
├── services/           # Business logic layer
│   ├── member_service.py
│   ├── trainer_service.py
│   └── admin_service.py
└── client/             # CLI client (legacy)
    ├── main_menu.py
    ├── member_menu.py
    ├── trainer_menu.py
    └── admin_menu.py
```

## Setup

1. **Activate the virtual environment** (from project root):
```bash
# On Windows (PowerShell)
..\venv\Scripts\Activate.ps1

# On Windows (Command Prompt)
..\venv\Scripts\activate.bat

# On macOS/Linux
source ../venv/bin/activate
```

2. Install dependencies (if not already installed):
```bash
pip install -r requirements.txt
```

3. Configure database connection in `database/connection.py`:
   - Update `DATABASE_URL` with your PostgreSQL credentials

4. Initialize database:
```bash
python reset_database.py
```

## Running the API

**Important:** Make sure the virtual environment is activated first!

Start the FastAPI server:
```bash
uvicorn app:app --reload
```

**Alternative:** If `uvicorn` command is not found, use:
```bash
python -m uvicorn app:app --reload
```

The API will be available at `http://localhost:8000`

API documentation:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Running the CLI Client

```bash
python main.py
```

## API Endpoints

### Member Routes
- `POST /members/` - Register new member
- `GET /members/{member_id}/dashboard` - Get member dashboard
- `POST /sessions/pt` - Book personal training session
- `POST /classes/enroll` - Enroll in group class
- `GET /members/` - List all members
- `GET /trainers/` - List all trainers
- `GET /rooms/` - List all rooms
- `GET /classes/` - List all classes

### Trainer Routes
- `POST /trainers/schedule` - Get trainer schedule
- `GET /trainers/{trainer_id}/members/search` - Search members
- `GET /trainers/members/` - List all members
- `GET /trainers/members/{member_id}` - View member profile
- `PUT /trainers/sessions/status` - Update session status
- `PUT /trainers/sessions/notes` - Update session notes

### Admin Routes
- `GET /admin/members` - List all members
- `GET /admin/trainers` - List all trainers
- `GET /admin/rooms` - List all rooms
- `GET /admin/classes` - List all classes
- `POST /admin/rooms` - Add new room
- `POST /admin/trainers` - Add new trainer
- `POST /admin/classes` - Create group class
- `PUT /admin/classes/reschedule` - Reschedule class
- `DELETE /admin/classes/{class_id}` - Cancel class

## Technologies

- FastAPI
- SQLAlchemy
- PostgreSQL
- Pydantic

