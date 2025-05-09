# Autonomous Drone Simulation & Dashboard

A software-based proof-of-concept (PoC) system that simulates an autonomous drone collecting environmental data, transmits this data to a backend server, stores it, and visualizes it on a secure web-based dashboard.

## Project Overview

This project implements:
- A Python-based drone simulator that generates environmental sensor data along a predefined flight path
- A Flask backend API for storing and retrieving drone flight and sensor data
- A PostgreSQL database for persistent storage of flight and sensor data
- A React frontend for visualizing the collected data

## Tech Stack

- **Simulation**: Python
- **Backend API**: Python (Flask) with Flask-SQLAlchemy
- **Database**: PostgreSQL
- **Frontend**: React.js
- **API Integration**: Axios
- **Testing**: pytest (backend), React Testing Library (frontend)
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
│       ├── components/    # React components 
│       └── services/      # API services 
├── simulation/            # Python-based drone simulation
│   ├── drone_simulator.py # Drone flight and sensor data simulator
│   └── tests/             # Simulation tests
├── tests/                 # Integration tests
├── instance/              # Instance-specific configuration
├── .env                   # Environment variables (create this - not in repo)
├── setup_postgres.sql     # Database setup script
├── .gitignore             # Git ignore file
├── README.md              # This file
├── todo.md                # Project to-do list
├── prd.md                 # Product Requirements Document
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

### Simulation Setup

The simulation module can be run independently to generate and send data to the API:

```
python -m simulation.drone_simulator
```

## Development Workflow

This repository uses a monorepo approach where both frontend and backend code are stored in the same repository. This simplifies version management and coordination between components.

### Branch Strategy

- `master`: Main branch containing production-ready code
- `develop`: Development branch for ongoing work
- Create feature branches from `develop` for new features
- Use pull requests to merge changes into develop

## Testing

- Backend tests: `pytest backend/tests/`
- Simulation tests: `pytest simulation/tests/`
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

Based on the project to-do list and requirements:

### Completed:
- ✅ Project setup and structure
- ✅ Python drone simulator with waypoint and sensor data generation
- ✅ Flask backend API with PostgreSQL database integration
- ✅ API endpoints for data ingestion and retrieval
- ✅ Backend and simulation testing
- ✅ Frontend API service integration

### In Progress:
- 🔄 Frontend dashboard components (FlightList, SensorDataTable)

### Planned:
- 📝 Data visualization with Chart.js
- 📝 Map visualization with Leaflet.js
- 📝 Authentication with Auth0
- 📝 Basic anomaly detection
- 📝 Comprehensive testing and documentation

## License

This project is licensed under the MIT License. 