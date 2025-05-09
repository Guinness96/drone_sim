# Project To-Do: Autonomous Drone Simulation & Dashboard

## Phase 0: Setup & Foundation

### Project Management & Version Control
- [x] Create GitHub repository: `autonomous-drone-simulation-dashboard` (local project created)
- [x] Initialize `README.md` with project title, brief description, and tech stack.
- [x] Set up GitHub Projects board with columns: To Do, In Progress, Done.
- [x] Create `.gitignore` file for Python and React development
- [x] Enhance `.gitignore` to include IDE-specific files (.vscode/, .idea/), OS-specific files (.DS_Store, Thumbs.db), and build artifacts

### Development Environments
- [x] Ensure Python 3.x is installed and accessible in PATH.
- [x] Create Python virtual environment: `python -m venv .venv` (activate it).
- [x] Ensure Node.js (LTS) and npm/yarn are installed.
- [x] Create `requirements.txt` file with all Python dependencies
- [ ] Update and freeze requirements.txt when adding new dependencies: `pip freeze > requirements.txt`

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
- [x] Install PostgreSQL locally or sign up for a free tier cloud instance (e.g., ElephantSQL).
- [x] Create database: `drone_monitoring_db`
- [x] Create database user: `drone_user` with a secure password.
- [x] Grant `drone_user` all privileges on `drone_monitoring_db`.
- [x] Note down DB connection string: `postgresql://drone_user:drone_password@localhost:5432/drone_monitoring_db`
- [x] Set up test database: `drone_monitoring_db_test`

## Phase 1: Core Simulation Logic (Python)

### Drone Movement Simulation
- [x] In `simulation/` directory, create `drone_simulator.py`.
- [x] Define waypoint data structure (e.g., `[(lat, lon), ...]`).
- [x] Implement `simulate_path(waypoints)` function to iterate through waypoints.
- [x] Simulation configuration parameters (speed, waypoint file, sensor noise levels)
- [x] Basic physics (velocity, acceleration, simulated inertia)
    - [x] Implementation of physics engine in `drone_physics.py`
    - [x] Integration with drone simulator
    - [x] Comprehensive testing for all physics features

### Sensor Data Generation
- [x] Implement `generate_sensor_reading(current_position)` function in `drone_simulator.py`.
    - [x] Include: timestamp, latitude, longitude, altitude (mocked), temperature, humidity, air_quality_index (randomized within realistic ranges).
- [x] Integrate sensor generation into `simulate_path` to produce data at each waypoint/interval.
- [ ] Improve sensor data realism with specific anomalous patterns for testing anomaly detection

### Simulation Output
- [x] Modify `simulate_path` to collect all generated position and sensor data.
- [x] Initially, print collected data as a list of JSON objects to the console.

## Phase 1b: Enhanced Simulation Features

### Battery Life Simulation
- [ ] Add battery simulation parameters to drone configuration:
    - [ ] Battery capacity (mAh)
    - [ ] Base discharge rate (mAh/minute)
    - [ ] Dynamic discharge factors (speed, altitude changes, payload)
- [ ] Implement battery level tracking in `drone_simulator.py`
- [ ] Create low battery behavior (warnings, return-to-home functionality)
- [ ] Add battery information to telemetry data sent to API
- [ ] For dev: Basic linear discharge model
- [ ] For test: Simulated discharge variability
- [ ] For prod: Realistic power consumption model based on flight parameters

### Weather Conditions Simulation
- [ ] Add weather configuration parameters:
    - [ ] Wind speed and direction
    - [ ] Precipitation probability
    - [ ] Cloud cover/visibility
- [ ] Implement physics adjustments for wind effects on drone movement
- [ ] Create weather effects on sensor readings
- [ ] For dev: Static weather conditions
- [ ] For test: Simulated weather sequences for testing flight behavior
- [ ] For prod: Optional integration point with weather APIs

### Mission Parameters
- [ ] Add mission configuration options:
    - [ ] Flight purpose (photography, survey, delivery)
    - [ ] Geofencing boundaries
    - [ ] No-fly zones
    - [ ] Mission duration limits
- [ ] Implement validation logic for waypoints against geofencing
- [ ] Create API endpoints for mission configuration
- [ ] For dev: Basic validation of waypoints
- [ ] For test: Test scenarios with boundary conditions
- [ ] For prod: Integration with actual regulatory no-fly zone data sources

### Emergency Simulation
- [ ] Implement emergency condition simulation:
    - [ ] Signal loss scenarios
    - [ ] Component failure models
    - [ ] Obstacle detection
- [ ] Create emergency response behaviors
- [ ] Add emergency event logging
- [ ] For dev: Manual triggering of emergency conditions
- [ ] For test: Scheduled test scenarios for different emergency types
- [ ] For prod: Realistic probability-based emergency simulation

### Payload and Equipment Simulation
- [ ] Add payload configuration options:
    - [ ] Payload weight
    - [ ] Camera/sensor types
    - [ ] Gimbal simulation
- [ ] Implement physics adjustments based on payload weight
- [ ] Add equipment-specific data to telemetry
- [ ] For dev: Fixed payload configurations
- [ ] For test: Range of payloads for testing physical impacts
- [ ] For prod: Detailed equipment simulation with realistic specifications

## Phase 2: Backend API & Database Integration (Flask)

### Database Schema & SQLAlchemy Models
- [x] In `backend/`, install `Flask-SQLAlchemy`, `psycopg2-binary`: `pip install Flask-SQLAlchemy psycopg2-binary python-dotenv`
- [x] Create `backend/models.py`.
- [x] Define SQLAlchemy models:
    - [x] `Flight(id, start_time, end_time)`
    - [x] `DronePosition(id, flight_id, timestamp, latitude, longitude, altitude)`
    - [x] `SensorReading(id, drone_position_id, timestamp, temperature, humidity, air_quality_index)`
- [x] In `backend/app.py`, configure SQLAlchemy and create database tables: `db.create_all()`
- [ ] Ensure all timestamp fields are timezone-aware (UTC)
- [ ] Add database indexes for faster querying (flight_id, drone_position_id, timestamp fields)
- [ ] Enhance database models for simulation features:
    - [ ] Add `battery_level`, `estimated_remaining_time` to `DronePosition`
    - [ ] Create `WeatherCondition(id, flight_id, timestamp, wind_speed, wind_direction, precipitation)` model
    - [ ] Create `MissionConfig(id, flight_id, purpose, geofence_coordinates, max_duration)` model
    - [ ] Create `DroneEquipment(id, flight_id, payload_weight, camera_type, gimbal_enabled)` model
    - [ ] Create `EmergencyEvent(id, flight_id, timestamp, event_type, description, resolved)` model
- [ ] For dev: Simple schema with minimal constraints
- [ ] For test: Add validation constraints and test data
- [ ] For prod: Add proper indexes and optimized queries

### API Endpoints - Data Ingestion
- [x] Create Flask route `POST /api/flights/start`
    - [x] Accepts: (optional) flight metadata.
    - [x] Action: Creates new `Flight` record, returns `flight_id`.
- [x] Create Flask route `POST /api/flights/<int:flight_id>/log_data`
    - [x] Accepts: JSON payload with drone position (lat, lon, alt) and sensor readings (temp, humidity, aqi).
    - [x] Action: Creates `DronePosition` and linked `SensorReading` records for the given `flight_id`.
- [ ] Consider implementing batch data ingestion to improve efficiency
- [ ] Add robust input validation for all API endpoints

### API Endpoints - Data Retrieval
- [x] Create Flask route `GET /api/flights`
    - [x] Action: Returns list of all `Flight` records.
- [x] Create Flask route `GET /api/flights/<int:flight_id>/data`
    - [x] Action: Returns all `DronePosition` and `SensorReading` data for the specified `flight_id`.
- [x] Create Flask route `GET /api/sensor_readings/latest`
    - [x] Accepts: (optional query param `limit=N`)
    - [x] Action: Returns the N most recent `SensorReading` records.
- [ ] Add pagination, time range filtering for data retrieval endpoints
- [ ] Implement data downsampling/aggregation for overview charts (advanced)
- [ ] Return meaningful error codes and messages for all API endpoints
- [ ] Consider API versioning for future scalability (e.g., /api/v1/flights)
- [ ] Create new API endpoints for enhanced simulation features:
    - [ ] `GET /api/flights/<int:flight_id>/battery` - Battery level history
    - [ ] `GET /api/flights/<int:flight_id>/weather` - Weather conditions during flight
    - [ ] `GET/POST /api/mission_configs` - Mission configuration management
    - [ ] `GET /api/flights/<int:flight_id>/emergency_events` - Emergency events during flight
    - [ ] `GET /api/flights/<int:flight_id>/equipment` - Equipment configuration
- [ ] For dev: Basic CRUD endpoints with minimal validation
- [ ] For test: Add comprehensive validation and error responses
- [ ] For prod: Add rate limiting, caching strategies, and optimization

### Simulation Script Integration
- [x] Install `requests` library in simulation venv: `pip install requests`
- [x] Modify `simulation/drone_simulator.py`:
    - [x] Call `POST /api/flights/start` at the beginning of simulation.
    - [x] For each data point, call `POST /api/flights/<flight_id>/log_data`.

### API Configuration & CORS
- [x] In `backend/app.py`, load database URI from `.env` file.
- [x] Install and configure `Flask-CORS`: `pip install Flask-CORS`, then `CORS(app)` in `app.py`.
- [ ] Implement proper logging in the Flask backend

## Phase 2b: Testing (Added)

### Backend Testing
- [x] Install pytest and required testing packages: `pip install pytest pytest-flask`
- [x] Create `backend/tests/` directory with `__init__.py`
- [x] Create `backend/tests/conftest.py` for test fixtures
- [x] Create `backend/tests/test_models.py` to test database models
- [x] Create `backend/tests/test_api.py` to test API endpoints
- [x] Run tests (6/7 tests pass, with Windows-specific file cleanup issue)
- [ ] Investigate Windows-specific file cleanup issue
- [ ] Add test coverage measurement with pytest-cov

### Simulation Testing
- [x] Create `simulation/tests/` directory with `__init__.py`
- [x] Create `simulation/tests/test_simulator.py` to test drone simulator
- [x] Create mock API responses for testing simulator without the API
- [x] Create `simulation/test_drone_physics.py` to test physics implementation
- [x] Create `simulation/test_physics_integration.py` to test physics and simulator integration
- [x] Run tests (all tests pass)

### Integration Testing
- [ ] Create specific tests that span multiple components (simulation to data retrieval)
- [ ] Test data flow: Simulation -> API -> Database -> Frontend

## Phase 3: Basic Frontend Dashboard & Data Display (React)

### React Project Structure
- [x] In `frontend/src/`, create `components/` directory.
- [x] In `frontend/src/`, create `services/` directory (for API calls).
- [ ] Decide on a state management strategy (Context, Redux, Zustand)

### API Integration (Frontend)
- [x] Install Axios in `frontend/`: `npm install axios`
- [x] In `frontend/src/services/api.js`, create functions:
    - [x] `startNewFlight()`
    - [x] `logFlightData(flightId, data)`
    - [x] `getAllFlights()`
    - [x] `getFlightData(flightId)`
    - [x] `getLatestSensorReadings(limit)`

### Data Display Components
- [x] Create `frontend/src/components/FlightList.js`:
    - [x] Fetches and displays a list of flights using `getAllFlights()`.
    - [x] Allows selecting a flight.
    - [x] Add visual indicator for flights with anomalies (once backend logic is in place).
- [x] Create `frontend/src/components/SensorDataTable.js`:
    - [x] Fetches and displays sensor readings in a table using `getLatestSensorReadings()` or `getFlightData()` based on selection.
    - [x] Ensure table handles horizontal scrolling for many columns.
    - [x] Handle different data types appropriately (numbers, strings, booleans).
- [x] Implement loading states (skeletons/spinners) for components
- [x] Add error handling and meaningful error messages
- [x] Create empty states for when no data is available
- [x] Integrate components into `frontend/src/App.js`.
- [x] Create `frontend/src/components/SimulatorControl.js` to control drone simulation parameters
- [ ] Create enhanced simulation feature components:
    - [ ] Create `BatteryStatusWidget.js` with graphical battery indicator and alerts
    - [ ] Create `WeatherPanel.js` to display and configure weather conditions
    - [ ] Create `MissionConfigPanel.js` for mission planning and geofencing visualization
    - [ ] Create `EmergencyEventLog.js` to display emergency events with filtering options
    - [ ] Create `EquipmentConfiguration.js` to display and configure drone equipment
- [ ] For dev: Basic UI components with minimal styling
- [ ] For test: Add comprehensive test cases for UI components
- [ ] For prod: Add responsive design, accessibility features, and performance optimization

## Phase 4: Visualizations - Charts & Maps (React)

### Chart Integration (Chart.js)
- [ ] In `frontend/`, install `chart.js` and `react-chartjs-2`: `npm install chart.js react-chartjs-2`
- [ ] Create `frontend/src/components/SensorChart.js`.
- [ ] Fetch time-series sensor data for a selected flight.
- [ ] Display data (e.g., temperature vs. time) using a Line chart.
- [ ] Implement synchronization between multiple charts or between charts and tables

### Map Integration (Leaflet.js)
- [ ] In `frontend/`, install `leaflet` and `react-leaflet`: `npm install leaflet react-leaflet`
- [ ] Create `frontend/src/components/FlightMap.js`.
- [ ] Import Leaflet CSS in `frontend/src/index.js` or `App.js`.
- [ ] Fetch flight path data (list of lat/lon coordinates) for a selected flight.
- [ ] Display the path as a `<Polyline>` on a `<MapContainer>`.
- [ ] Display sensor reading locations as `<Marker>` components, with popups showing sensor values.
- [ ] Consider marker clustering for performance with large numbers of points
- [ ] Ensure proper map tile attribution
- [ ] Add interactivity: clicking on map elements highlights data in table/chart
- [ ] Enhance map features for simulation enhancements:
    - [ ] Add battery level indicators along flight path
    - [ ] Visualize weather conditions (wind vectors, precipitation areas)
    - [ ] Display geofence boundaries and no-fly zones
    - [ ] Mark locations of emergency events
    - [ ] Show equipment-specific data (camera coverage area, etc.)
- [ ] For dev: Basic visualization with static styling
- [ ] For test: Add different map layers and visualization modes for testing
- [ ] For prod: Add performance optimizations for large datasets and complex visualizations

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
- [ ] Implement token refresh handling

### Backend API Security (Flask)
- [ ] In `backend/`, install `PyJWT`, `cryptography`, `requests`: `pip install PyJWT cryptography requests`
- [ ] Create `backend/auth.py` (or similar) with functions to verify Auth0 JWTs (refer to Auth0 Flask SDK or examples).
- [ ] Create a decorator `@require_auth` in `backend/auth.py`.
- [ ] Apply `@require_auth` to protect Flask API routes that need authentication.
- [ ] Implement standard web security practices (appropriate headers, protection against common vulnerabilities)
- [ ] For future enhancement: consider user roles/permissions

## Phase 6: Basic Analytics Placeholder & Refinement

### Anomaly Detection Logic (Backend)
- [x] Modify Flask API endpoint for logging data:
    - [x] Add a simple rule: e.g., if `temperature > 35` or `air_quality_index > 150`, mark data point with an `is_anomaly: true` flag before saving or when retrieving.
- [ ] Consider adding anomaly type (e.g., "high_temp", "erratic_movement") or severity
- [ ] Decide whether to store anomaly flags in the database or calculate on retrieval

### Dashboard Anomaly Display (Frontend)
- [ ] In `SensorDataTable.js` and `FlightMap.js` (Markers):
    - [ ] Conditionally style rows/markers if `is_anomaly` is true (e.g., red color, different icon).
- [ ] Create separate "Anomalies List" component showing all detected anomalies for selected flight

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
- [ ] Add end-to-end (E2E) tests using Cypress or Playwright
- [ ] Conduct basic performance testing with large datasets (10,000+ data points)

### Documentation
- [ ] Prepare Code Manifest (list of files, purpose, contribution).
- [ ] Draft sections for the final report (changes, justifications, evaluation).
- [ ] Add `TODO:` comments in code for any known issues or future improvements.
- [ ] Generate API documentation (using Swagger/OpenAPI or Markdown)
- [ ] Document deployment steps for backend, frontend, and database

### Software Demonstration Video
- [ ] Plan demo script: introduction, simulation, data flow, dashboard features (login, charts, map, anomalies), code walkthrough.
- [ ] Record video.
- [ ] Edit video.
- [ ] Focus on showcasing key features and the data flow from simulation to anomaly highlighting

### Final Report
- [ ] Complete all sections of the final report.
- [ ] Proofread and submit. 

## Phase 8: Configuration & Deployment Considerations

### Configuration Management
- [ ] Use .env files consistently for secrets and environment-specific configurations
- [ ] Provide .env.example files with placeholder values
- [ ] Ensure .env is in .gitignore

### Logging
- [ ] Implement proper logging throughout the application
- [ ] Be careful not to log sensitive information

### Scalability (Long-term consideration)
- [ ] Document potential database optimizations for scaling
- [ ] Consider API rate limiting for production
- [ ] Evaluate using a task queue for long-running processes 