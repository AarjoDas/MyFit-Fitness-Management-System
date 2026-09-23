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
- Personalized class recommendations (with cold-start popularity fallback)

### Trainer Portal
- View schedule (classes and PT sessions)
- Search and view member profiles
- Update session status and notes

### Admin Portal
- Manage rooms
- Manage trainers
- Create, reschedule, and cancel group classes
- View all members
- View recommendation eval metrics and retrain the model

## Technologies

### Backend
- FastAPI
- SQLAlchemy
- PostgreSQL
- Pydantic
- scikit-learn / pandas / joblib (class recommendations)

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

## Class recommendation system

Members get ranked upcoming group classes from a scikit-learn logistic regression trained on historical `class_enrollments`. Full and already-booked classes are filtered out before scoring. Members with no bookings get a popularity fallback.

Historical enrollments used for training are **synthetic** (see `backend/database/seed_historical_data.py`). Do not treat eval numbers as production user behavior.

### Setup (ML)

```bash
cd backend
python reset_database.py
python -m database.seed_historical_data
python -m ml.train
python -m pytest tests/test_recommendations.py
```

Then log in as Alice (usually member ID `1`) to see yoga-leaning recommendations, or register a new member for popularity fallback.

### Features (per member, class pair)

| Feature | Description |
| --- | --- |
| same_class_name_before | Prior bookings of this class name |
| same_trainer_before | Prior bookings with this trainer |
| hour_of_day / is_morning / is_evening | Time-of-day signals |
| days_until_class | Days from the reference date to the class |
| class_fill_ratio | Active enrollments / capacity |
| trainer_specialization_match | Class name vs trainer specialization |
| member_total_bookings | History size |
| member_attendance_rate | Share of past bookings marked Attended |
| books_this_weekday_before | History on the same weekday |

### Evaluation

`python -m ml.train` writes `backend/ml/artifacts/metrics.json` (committed) and `rec_v1.joblib` (gitignored). Metrics include precision@3 vs a global most-popular `class_name` baseline on a time-based split (train: first 60 of ~90 days, test: days 60–90).

### Limitations

- Training data is synthetic and small.
- Cold-start members cannot get personalized scores.
- No JWT: the API still takes `member_id` in the path, matching the rest of the app.
- Model is retrained offline (`POST /admin/recommendations/retrain` or `python -m ml.train`), not continuously.

### Demo script

1. Reset DB, seed historical data, train the model (commands above).
2. Log in as member `1` (Alice) → Recommended for you should lean toward Morning Yoga / Pilates.
3. Register a new member and log in → popularity fallback, not an empty list.
4. Book from a recommendation card → class appears under Upcoming Classes.
5. Admin → Recommendation Metrics to view `metrics.json` / retrain.


