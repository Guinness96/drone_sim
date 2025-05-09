# Tests for Drone Simulation Project

This directory contains tests for the Drone Simulation Project, organized by module.

## Test Structure

The tests are organized into the following modules:

### Project Runner Tests (`tests/project_runner/`)

Tests for the project runner module that handles starting the project components.

- `test_postgres.py`: Tests for PostgreSQL management functionality
- `test_servers.py`: Tests for server management (backend, frontend, simulation)
- `test_process.py`: Tests for process monitoring and cleanup
- `test_cli.py`: Tests for command-line interface (some tests are skipped due to mocking issues)

### Backend Tests (`backend/tests/`)

Tests for the Flask backend API.

- `test_models.py`: Tests for database models
- `test_api.py`: Tests for API endpoints
- `conftest.py`: Test fixtures for backend tests

### Simulation Tests

Tests for the drone simulation functionality.

- `simulation/test_drone_physics.py`: Tests for drone physics engine
- `simulation/test_physics_integration.py`: Tests for integration between physics and simulator
- `simulation/tests/test_simulator.py`: Tests for the drone simulator itself

### Integration Tests

- `tests/test_postgres_integration.py`: Integration tests for PostgreSQL that interact with an actual PostgreSQL installation

### Legacy Tests (Deprecated)

These tests are kept for reference but are now redundant with our modular test structure:

- `tests/test_run.py`: Original tests for the monolithic run.py script

## Running Tests

Use the test runner script to run tests:

```bash
# Run only project_runner tests (default)
python tests/run_tests.py

# Run all tests
python tests/run_tests.py --all

# Run specific test groups
python tests/run_tests.py --project-runner
python tests/run_tests.py --simulation
python tests/run_tests.py --backend
python tests/run_tests.py --integration
```

## Test Dependencies

All tests require the following dependencies:
- Python 3.8+
- unittest (standard library)
- pytest (for backend and simulation tests)

## Notes on Integration Tests

Integration tests interact with actual system components:
- PostgreSQL tests require a PostgreSQL installation 
- These tests can modify your local PostgreSQL instance, so they are disabled by default
- Run them only in a controlled environment where it's safe to start/stop PostgreSQL 