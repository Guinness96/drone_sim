import os
import sys
import pytest

# Add parent directory to path so we can import from backend
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Change from backend.app to using relative imports
from backend.models import db, Flight, DronePosition, SensorReading
from backend.app import app as flask_app

@pytest.fixture(scope='module')
def app():
    """Create a Flask app configured for testing"""
    # Set up a test-specific PostgreSQL database
    test_db_name = 'drone_monitoring_db_test'
    
    # Use the actual app but reconfigure it for testing with a test database
    app = flask_app
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': f'postgresql://drone_user:drone_password@localhost:5432/{test_db_name}',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    })
    
    # Create the test database if it doesn't exist
    with app.app_context():
        # Database already created manually
        # Create the database tables in the test database
        db.create_all()
    
    yield app
    
    # We don't drop the test database here to allow for inspection,
    # but in a real CI environment, you might want to drop it

@pytest.fixture(scope='module')
def client(app):
    """Create a test client for the app"""
    return app.test_client()

@pytest.fixture(scope='module')
def runner(app):
    """Create a test CLI runner for the app"""
    return app.test_cli_runner()

@pytest.fixture(scope='function')
def session(app):
    """Create a new database session for a test"""
    with app.app_context():
        db.session.begin_nested()
        yield db.session
        db.session.rollback()

@pytest.fixture(scope='function')
def sample_flight(session):
    """Create a sample flight for testing"""
    flight = Flight()
    session.add(flight)
    session.commit()
    return flight

@pytest.fixture(scope='function')
def sample_position(session, sample_flight):
    """Create a sample drone position for testing"""
    position = DronePosition(
        flight_id=sample_flight.id,
        latitude=51.507351,
        longitude=-0.127758,
        altitude=100.0
    )
    session.add(position)
    session.commit()
    return position

@pytest.fixture(scope='function')
def sample_reading(session, sample_position):
    """Create a sample sensor reading for testing"""
    reading = SensorReading(
        drone_position_id=sample_position.id,
        temperature=20.0,
        humidity=60.0,
        air_quality_index=50.0
    )
    session.add(reading)
    session.commit()
    return reading 