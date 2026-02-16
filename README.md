# Guitar Gym

A practice app for drilling guitar exercises — fretboard note identification, interval training, and more.

## Architecture

```
guitar_gym/
├── backend/          # Python / FastAPI API server
│   ├── app/
│   │   ├── main.py           # FastAPI entry point
│   │   ├── config.py         # Settings (env-based)
│   │   ├── database.py       # Async SQLAlchemy setup
│   │   ├── models/           # DB models (User, ExerciseSession, ExerciseAttempt)
│   │   ├── routers/          # API routes (auth, exercises, progress)
│   │   ├── services/         # Auth utils, music theory core
│   │   └── exercises/        # Pluggable exercise system
│   │       ├── base.py               # BaseExercise ABC
│   │       ├── registry.py            # Exercise registry
│   │       ├── note_identification.py # Fretboard note ID
│   │       └── interval_training.py   # Interval recognition
│   ├── alembic/              # DB migrations
│   └── requirements.txt
│
└── ios/              # SwiftUI native iOS app
    └── GuitarGym/
        └── GuitarGym/
            ├── GuitarGymApp.swift
            ├── Models/       # Codable API models
            ├── Views/        # SwiftUI screens
            ├── ViewModels/   # MVVM view models
            └── Services/     # API client
```

## Tech Stack

| Layer    | Technology              |
|----------|------------------------|
| Backend  | Python 3.12, FastAPI, SQLAlchemy (async), Alembic |
| Database | PostgreSQL              |
| Auth     | JWT (python-jose) + bcrypt |
| iOS App  | SwiftUI, MVVM pattern   |

## Getting Started

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Start the server
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`. Interactive docs at `/docs`.

### iOS App

Open `ios/GuitarGym/` in Xcode and run on a simulator or device.

## Adding a New Exercise

1. Create a new file in `backend/app/exercises/` (e.g. `scale_drill.py`)
2. Subclass `BaseExercise` and implement `generate_question()` and `check_answer()`
3. Add an instance to `EXERCISE_REGISTRY` in `registry.py`

The iOS app will automatically pick up new exercises from the `/exercises/` API endpoint.

## Current Exercises

- **Note Identification** — A position is highlighted on the fretboard; identify the note name
- **Interval Training** — Two notes are shown; identify the interval (4th, 5th, etc.)

## Planned Features

- Practice session history and accuracy tracking
- Streak tracking and practice reminders
- Scale and chord exercises
- Ear training mode
- Multi-user support with profiles
