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
- **Database**: SQLite (development), PostgreSQL (planned for production)
- **Frontend**: React.js
- **Charting**: Chart.js (planned)
- **Mapping**: Leaflet.js (planned)
- **Authentication**: Auth0 (planned)

## Project Structure

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

## Setup & Installation

### Prerequisites

- Python 3.x
- Node.js and npm
- Git

### Backend Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/autonomous-drone-simulation-dashboard.git
   cd autonomous-drone-simulation-dashboard
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1  # Windows PowerShell
   # OR
   source .venv/bin/activate     # Linux/macOS
   ```

3. Install Python dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Run the Flask server:
   ```
   cd backend
   python app.py
   ```
   The API will be available at http://localhost:5000

### Frontend Setup

1. Install frontend dependencies:
   ```
   cd frontend
   npm install
   ```

2. Start the React development server:
   ```
   npm start
   ```
   The frontend will be available at http://localhost:3000

### Running the Simulation

1. Make sure the Flask backend is running
2. Run the drone simulator:
   ```
   cd simulation
   python drone_simulator.py
   ```

## API Endpoints

- `POST /api/flights/start` - Start a new flight
- `POST /api/flights/<flight_id>/end` - End a flight
- `POST /api/flights/<flight_id>/log_data` - Log drone position and sensor data
- `GET /api/flights` - Get all flights
- `GET /api/flights/<flight_id>/data` - Get data for a specific flight
- `GET /api/sensor_readings/latest?limit=10` - Get the latest sensor readings

## Testing

Run backend tests:
```
cd backend
python -m pytest tests/
```

Run simulation tests:
```
cd simulation
python -m pytest tests/
```

## Current Development Status

- ✅ Python drone simulator
- ✅ Flask backend API with database models
- ✅ API tests and simulation tests
- 🔄 React frontend (in progress)
- 📝 Data visualization (planned)
- 📝 Authentication (planned)

## License

This project is licensed under the MIT License. 