import os
import sys
import pytest
import tempfile
from flask import Flask

# Add parent directory to path so we can import from backend
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.models import db, Flight, DronePosition, SensorReading

@pytest.fixture(scope='module')
def app():
    """Create a Flask app configured for testing"""
    # Create a temporary file to isolate the database for each test
    db_fd, db_path = tempfile.mkstemp()
    
    app = Flask(__name__)
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    })
    
    # Create the database and the tables
    with app.app_context():
        db.init_app(app)
        db.create_all()
    
    yield app
    
    # Close and remove the temporary database
    os.close(db_fd)
    os.unlink(db_path)

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