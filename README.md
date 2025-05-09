# Autonomous Drone Simulation & Dashboard

A software-based proof-of-concept (PoC) system that simulates an autonomous drone collecting environmental data, transmits this data to a backend server, stores it, and visualizes it on a secure web-based dashboard.

## Quick Start

The easiest way to run the project is using the provided run script:

1. Clone the repository and navigate to the project root (drone_sim)

2. Create and activate a virtual environment:
   ```
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   source .venv/bin/activate  # Linux/MacOS
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root with database configuration:
   ```
   DATABASE_URL=postgresql://drone_user:drone_password@localhost:5432/drone_monitoring_db
   SECRET_KEY=your-secret-key-for-development
   FLASK_ENV=development
   ```

5. Run the project (this will start PostgreSQL, backend, and frontend):
   ```
   python run.py
   ```
   
   This will:
   - Check if PostgreSQL is running and start it if needed
   - Start the Flask backend server
   - Start the React frontend development server
   
6. Once everything is running:
   - Access the frontend at: http://localhost:3000
   - The backend API is available at: http://localhost:5000

7. Additional options:
   ```
   # Start only the backend (no frontend)
   python run.py --no-frontend
   
   # Start only the frontend (no backend)
   python run.py --no-backend
   
   # Start everything and run a simulation
   python run.py --simulation
   
   # Start with a custom simulation configuration
   python run.py --simulation --simulation-config path/to/config.json
   ```

8. Press Ctrl+C to stop all components when finished

## Project Overview

This project implements:
- A Python-based drone simulator that generates environmental sensor data along a predefined flight path
- A realistic physics engine simulating drone movement with inertia, acceleration, and turning dynamics
- A Flask backend API for storing and retrieving drone flight and sensor data
- A PostgreSQL database for persistent storage of flight and sensor data
- A React frontend for visualizing the collected data and controlling simulation parameters

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
│   ├── drone_physics.py   # Physics engine for realistic drone movement
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

### Environment Setup

1. Create a `.env` file in the project root directory (drone_sim):
   ```
   DATABASE_URL=postgresql://drone_user:drone_password@localhost:5432/drone_monitoring_db
   SECRET_KEY=your-secret-key-for-development
   FLASK_ENV=development
   ```

### Database Setup

1. Start PostgreSQL service if it's not already running:
   ```
   # Windows
   net start postgresql-x64-14
   # Linux/MacOS
   sudo service postgresql start
   ```

2. Set up the database tables:
   ```
   psql -U postgres -f setup_postgres.sql
   ```

### Backend Setup

1. Create and activate a virtual environment in the project root (drone_sim):
   ```
   # Create virtual environment
   python -m venv .venv
   
   # Activate on Windows
   .venv\Scripts\activate
   
   # Activate on Linux/MacOS
   source .venv/bin/activate
   ```

2. Install dependencies (from the project root):
   ```
   pip install -r requirements.txt
   ```

3. Start the Flask backend server (from the project root):
   ```
   # Make sure you are in the project root directory (drone_sim)
   python -m backend.app
   ```
   The server should be available at http://localhost:5000

### Frontend Setup

1. Open a new terminal window

2. Navigate to the frontend directory from the project root:
   ```
   cd frontend
   ```

3. Install dependencies:
   ```
   npm install
   ```

4. Start the development server:
   ```
   npm start
   ```
   The frontend should be available at http://localhost:3000

### Running the Simulation

1. Make sure the backend server is running

2. Run the simulation from the project root directory (drone_sim) in a separate terminal with the virtual environment activated:
   ```
   # Make sure you are in the project root directory (drone_sim)
   python -m simulation.drone_simulator
   ```

3. Alternatively, you can control the simulation from the web UI at http://localhost:3000 using the SimulatorControl component

### Troubleshooting

- **Directory Issues**: All commands should be run from the project root directory (drone_sim) unless specified otherwise
- **Database Connection Issues**: Ensure PostgreSQL is running and that your database connection details in the `.env` file match your PostgreSQL setup
- **Import Errors**: Make sure you're running commands from the project root directory and using module notation (e.g., `python -m backend.app` instead of just `python backend/app.py`)
- **Port Conflicts**: If port 5000 or 3000 is already in use, you'll need to change the port in the respective configuration

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
- Physics tests: `pytest simulation/test_drone_physics.py`
- Physics integration tests: `pytest simulation/test_physics_integration.py`
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
- ✅ Realistic physics engine for drone movement simulation
- ✅ Flask backend API with PostgreSQL database integration
- ✅ API endpoints for data ingestion and retrieval
- ✅ Backend, simulation, and physics testing
- ✅ Frontend API service integration
- ✅ Frontend simulator control component for adjusting simulation parameters

### In Progress:
- 🔄 Frontend dashboard components (FlightList, SensorDataTable)

### Planned:
- 📝 Data visualization with Chart.js
- 📝 Map visualization with Leaflet.js
- 📝 Authentication with Auth0
- 📝 Basic anomaly detection
- 📝 Enhanced simulation features (battery life, weather conditions, etc.)
- 📝 Comprehensive testing and documentation

## License

This project is licensed under the MIT License. 