# Fitness Club Frontend

React + TypeScript + Tailwind CSS frontend for the Fitness Club Management System.

## Features

- **Member Portal**: Register, view dashboard, book PT sessions, register for group classes
- **Trainer Portal**: View schedule, search members, manage PT sessions
- **Admin Portal**: Manage rooms, trainers, classes, and view all members

## Setup

1. Install dependencies:
```bash
npm install
```

2. Make sure the FastAPI backend is running on `http://localhost:8000`

3. Start the development server:
```bash
npm start
```

The app will open at `http://localhost:3000`

## Usage

1. **Register as a Member**: Click "Register here" on the login page
2. **Login**: Use your Member ID, Trainer ID, or Admin ID to login
3. **Navigate**: Use the dashboard to access different features based on your role

## Project Structure

```
src/
├── components/       # Reusable components
├── context/         # React context (Auth)
├── pages/           # Page components
│   ├── admin/      # Admin pages
│   ├── member/     # Member pages
│   └── trainer/    # Trainer pages
└── utils/          # API client and utilities
```

## API Integration

The frontend communicates with the FastAPI backend at `http://localhost:8000`. All API calls are defined in `src/utils/api.ts`.

## Technologies

- React 18
- TypeScript
- Tailwind CSS
- React Router
- Axios
