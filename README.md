# Autonomous Drone Simulation & Dashboard

A software-based proof-of-concept (PoC) system that simulates an autonomous drone collecting environmental data, transmits this data to a backend server, stores it, and visualizes it on a secure web-based dashboard.

## Project Overview

This project implements:
- A Python-based drone simulator that generates environmental sensor data along a predefined flight path
- A Flask backend API for storing and retrieving drone flight and sensor data
- A React frontend for visualizing the collected data (in development)

## Tech Stack

- **Simulation**: Python
- **Backend API**: Python (Flask)
- **Database**: PostgreSQL
- **Frontend**: React.js
- **Charting**: Chart.js (planned)
- **Mapping**: Leaflet.js (planned)
- **Authentication**: Auth0 (planned)

## Project Structure

This project follows a monorepo structure with both the frontend and backend in a single repository:

```
drone_sim/
├── backend/               # Flask API server
│   ├── app.py             # Main Flask application
│   ├── config.py          # Configuration settings
│   ├── models.py          # SQLAlchemy database models
│   └── tests/             # Backend tests
├── frontend/              # React web dashboard
│   ├── public/            # Static files
│   └── src/               # React source code
│       ├── components/    # React components (in development)
│       └── services/      # API services 
├── simulation/            # Python-based drone simulation
│   ├── drone_simulator.py # Drone flight and sensor data simulator
│   └── tests/             # Simulation tests
├── .env                   # Environment variables (create this - not in repo)
├── .gitignore             # Git ignore file
├── README.md              # This file
└── requirements.txt       # Python dependencies
```

## Getting Started

### Prerequisites

- Python 3.8+
- Node.js 16+
- PostgreSQL

### Backend Setup

1. Create a virtual environment:
   ```
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up PostgreSQL database:
   ```
   psql -U postgres -f setup_postgres.sql
   ```

4. Run the backend server:
   ```
   python -m backend.app
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```
   cd frontend
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Run the development server:
   ```
   npm start
   ```

## Development Workflow

This repository uses a monorepo approach where both frontend and backend code are stored in the same repository. This simplifies version management and coordination between components.

### Branch Strategy

- `master`: Main branch containing production-ready code
- Create feature branches for new features
- Use pull requests to merge changes into master

## Testing

- Backend tests: `pytest`
- Frontend tests: `cd frontend && npm test`
- Integration tests: `pytest tests/`

## API Endpoints

- `POST /api/flights/start` - Start a new flight
- `POST /api/flights/<flight_id>/end` - End a flight
- `POST /api/flights/<flight_id>/log_data` - Log drone position and sensor data
- `GET /api/flights` - Get all flights
- `GET /api/flights/<flight_id>/data` - Get data for a specific flight
- `GET /api/sensor_readings/latest?limit=10` - Get the latest sensor readings

## Current Development Status

- ✅ Python drone simulator
- ✅ Flask backend API with database models
- ✅ API tests and simulation tests
- 🔄 React frontend (in progress)
- 📝 Data visualization (planned)
- 📝 Authentication (planned)

## License

This project is licensed under the MIT License. 