# Project To-Do: Autonomous Drone Simulation & Dashboard

## Phase 0: Setup & Foundation

### Project Management & Version Control
- [x] Create GitHub repository: `autonomous-drone-simulation-dashboard` (local project created)
- [x] Initialize `README.md` with project title, brief description, and tech stack.
- [ ] Set up GitHub Projects board with columns: To Do, In Progress, Done.
- [x] Create `.gitignore` file for Python and React development

### Development Environments
- [x] Ensure Python 3.x is installed and accessible in PATH.
- [x] Create Python virtual environment: `python -m venv .venv` (activate it).
- [x] Ensure Node.js (LTS) and npm/yarn are installed.
- [x] Create `requirements.txt` file with all Python dependencies

### Backend (Flask) - Initial Setup
- [x] Install Flask: `pip install Flask`
- [x] Create backend project directory: `backend/`
- [x] Inside `backend/`, create `app.py`.
- [x] Implement basic "Hello World" GET route `/` in `app.py`.
- [x] Test Flask app runs locally: `python backend/app.py`

### Frontend (React) - Initial Setup
- [x] Create React app: `npx create-react-app frontend`
- [x] Navigate to `frontend/` and run `npm start` to test.
- [x] Create `frontend/src/components/` directory
- [x] Create `frontend/src/services/` directory

### Database (PostgreSQL) - Initial Setup
- [ ] Install PostgreSQL locally or sign up for a free tier cloud instance (e.g., ElephantSQL).
- [ ] Create database: `drone_monitoring_db`
- [ ] Create database user: `drone_user` with a secure password.
- [ ] Grant `drone_user` all privileges on `drone_monitoring_db`.
- [ ] Note down DB connection string: `postgresql://drone_user:PASSWORD@HOST:PORT/drone_monitoring_db`
- [x] Set up SQLite for development (alternative to PostgreSQL)

## Phase 1: Core Simulation Logic (Python)

### Drone Movement Simulation
- [x] In `simulation/` directory, create `drone_simulator.py`.
- [x] Define waypoint data structure (e.g., `[(lat, lon), ...]`).
- [x] Implement `simulate_path(waypoints)` function to iterate through waypoints.

### Sensor Data Generation
- [x] Implement `generate_sensor_reading(current_position)` function in `drone_simulator.py`.
    - [x] Include: timestamp, latitude, longitude, altitude (mocked), temperature, humidity, air_quality_index (randomized within realistic ranges).
- [x] Integrate sensor generation into `simulate_path` to produce data at each waypoint/interval.

### Simulation Output
- [x] Modify `simulate_path` to collect all generated position and sensor data.
- [x] Initially, print collected data as a list of JSON objects to the console.

## Phase 2: Backend API & Database Integration (Flask)

### Database Schema & SQLAlchemy Models
- [x] In `backend/`, install `Flask-SQLAlchemy`, `psycopg2-binary`: `pip install Flask-SQLAlchemy psycopg2-binary python-dotenv`
- [x] Create `backend/models.py`.
- [x] Define SQLAlchemy models:
    - [x] `Flight(id, start_time, end_time)`
    - [x] `DronePosition(id, flight_id, timestamp, latitude, longitude, altitude)`
    - [x] `SensorReading(id, drone_position_id, timestamp, temperature, humidity, air_quality_index)`
- [x] In `backend/app.py`, configure SQLAlchemy and create database tables: `db.create_all()`

### API Endpoints - Data Ingestion
- [x] Create Flask route `POST /api/flights/start`
    - [x] Accepts: (optional) flight metadata.
    - [x] Action: Creates new `Flight` record, returns `flight_id`.
- [x] Create Flask route `POST /api/flights/<int:flight_id>/log_data`
    - [x] Accepts: JSON payload with drone position (lat, lon, alt) and sensor readings (temp, humidity, aqi).
    - [x] Action: Creates `DronePosition` and linked `SensorReading` records for the given `flight_id`.

### API Endpoints - Data Retrieval
- [x] Create Flask route `GET /api/flights`
    - [x] Action: Returns list of all `Flight` records.
- [x] Create Flask route `GET /api/flights/<int:flight_id>/data`
    - [x] Action: Returns all `DronePosition` and `SensorReading` data for the specified `flight_id`.
- [x] Create Flask route `GET /api/sensor_readings/latest`
    - [x] Accepts: (optional query param `limit=N`)
    - [x] Action: Returns the N most recent `SensorReading` records.

### Simulation Script Integration
- [x] Install `requests` library in simulation venv: `pip install requests`
- [x] Modify `simulation/drone_simulator.py`:
    - [x] Call `POST /api/flights/start` at the beginning of simulation.
    - [x] For each data point, call `POST /api/flights/<flight_id>/log_data`.

### API Configuration & CORS
- [x] In `backend/app.py`, load database URI from `.env` file.
- [x] Install and configure `Flask-CORS`: `pip install Flask-CORS`, then `CORS(app)` in `app.py`.

## Phase 2b: Testing (Added)

### Backend Testing
- [x] Install pytest and required testing packages: `pip install pytest pytest-flask`
- [x] Create `backend/tests/` directory with `__init__.py`
- [x] Create `backend/tests/conftest.py` for test fixtures
- [x] Create `backend/tests/test_models.py` to test database models
- [x] Create `backend/tests/test_api.py` to test API endpoints
- [x] Run tests (6/7 tests pass, with Windows-specific file cleanup issue)

### Simulation Testing
- [x] Create `simulation/tests/` directory with `__init__.py`
- [x] Create `simulation/tests/test_simulator.py` to test drone simulator
- [x] Create mock API responses for testing simulator without the API
- [x] Run tests (all 9 tests pass)

## Phase 3: Basic Frontend Dashboard & Data Display (React)

### React Project Structure
- [x] In `frontend/src/`, create `components/` directory.
- [x] In `frontend/src/`, create `services/` directory (for API calls).

### API Integration (Frontend)
- [ ] Install Axios in `frontend/`: `npm install axios`
- [x] In `frontend/src/services/api.js`, create functions:
    - [x] `startNewFlight()`
    - [x] `logFlightData(flightId, data)`
    - [x] `getAllFlights()`
    - [x] `getFlightData(flightId)`
    - [x] `getLatestSensorReadings(limit)`

### Data Display Components
- [ ] Create `frontend/src/components/FlightList.js`:
    - [ ] Fetches and displays a list of flights using `getAllFlights()`.
    - [ ] Allows selecting a flight.
- [ ] Create `frontend/src/components/SensorDataTable.js`:
    - [ ] Fetches and displays sensor readings in a table using `getLatestSensorReadings()` or `getFlightData()` based on selection.
- [ ] Integrate components into `frontend/src/App.js`.

## Phase 4: Visualizations - Charts & Maps (React)

### Chart Integration (Chart.js)
- [ ] In `frontend/`, install `chart.js` and `react-chartjs-2`: `npm install chart.js react-chartjs-2`
- [ ] Create `frontend/src/components/SensorChart.js`.
- [ ] Fetch time-series sensor data for a selected flight.
- [ ] Display data (e.g., temperature vs. time) using a Line chart.

### Map Integration (Leaflet.js)
- [ ] In `frontend/`, install `leaflet` and `react-leaflet`: `npm install leaflet react-leaflet`
- [ ] Create `frontend/src/components/FlightMap.js`.
- [ ] Import Leaflet CSS in `frontend/src/index.js` or `App.js`.
- [ ] Fetch flight path data (list of lat/lon coordinates) for a selected flight.
- [ ] Display the path as a `<Polyline>` on a `<MapContainer>`.
- [ ] Display sensor reading locations as `<Marker>` components, possibly with popups showing sensor values.

## Phase 5: Authentication & Security (Auth0)

### Auth0 Setup
- [ ] Create Auth0 account and application:
    - [ ] Type: Single Page Application (for React)
    - [ ] Note: Domain, Client ID
    - [ ] Configure Allowed Callback URLs, Logout URLs, Web Origins.
- [ ] Create Auth0 API:
    - [ ] Note: API Identifier (Audience)

### Frontend Authentication (React)
- [ ] In `frontend/`, install `@auth0/auth0-react`: `npm install @auth0/auth0-react`
- [ ] Wrap `frontend/src/index.js` or `App.js` with `Auth0Provider` (using Domain, Client ID, Audience).
- [ ] Create `frontend/src/components/LoginButton.js` and `LogoutButton.js` using `useAuth0()`.
- [ ] Create `frontend/src/components/Profile.js` to display user info.
- [ ] Modify `App.js` to show login/dashboard based on `isAuthenticated`.
- [ ] Update `frontend/src/services/api.js` to get and include Auth0 access token in `Authorization: Bearer <TOKEN>` header for API calls.

### Backend API Security (Flask)
- [ ] In `backend/`, install `PyJWT`, `cryptography`, `requests`: `pip install PyJWT cryptography requests`
- [ ] Create `backend/auth.py` (or similar) with functions to verify Auth0 JWTs (refer to Auth0 Flask SDK or examples).
- [ ] Create a decorator `@require_auth` in `backend/auth.py`.
- [ ] Apply `@require_auth` to protect Flask API routes that need authentication.

## Phase 6: Basic Analytics Placeholder & Refinement

### Anomaly Detection Logic (Backend)
- [x] Modify Flask API endpoint for logging data:
    - [x] Add a simple rule: e.g., if `temperature > 35` or `air_quality_index > 150`, mark data point with an `is_anomaly: true` flag before saving or when retrieving.

### Dashboard Anomaly Display (Frontend)
- [ ] In `SensorDataTable.js` and `FlightMap.js` (Markers):
    - [ ] Conditionally style rows/markers if `is_anomaly` is true (e.g., red color, different icon).

### Code & UI Refinement
- [ ] Review all code for clarity, add comments.
- [ ] Basic error handling in React components for API call failures.
- [ ] Ensure consistent UI styling.
- [ ] Test responsive design (basic).

## Phase 7: Testing, Documentation & Demo Prep

### Testing
- [x] Manually test data flow: Simulation -> API -> Database -> Frontend.
- [ ] Test all API endpoints with Postman/Insomnia (including auth).
- [ ] Test all frontend user interactions and visualizations.
- [ ] Test login/logout functionality.

### Documentation
- [ ] Prepare Code Manifest (list of files, purpose, contribution).
- [ ] Draft sections for the final report (changes, justifications, evaluation).
- [ ] Add `TODO:` comments in code for any known issues or future improvements.

### Software Demonstration Video
- [ ] Plan demo script: introduction, simulation, data flow, dashboard features (login, charts, map, anomalies), code walkthrough.
- [ ] Record video.
- [ ] Edit video.

### Final Report
- [ ] Complete all sections of the final report.
- [ ] Proofread and submit. 