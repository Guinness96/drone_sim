import os
import sys
import pytest
from sqlalchemy.exc import OperationalError

# Add parent directory to path so we can import from backend
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Flag to track if database is available
db_available = False

# Try to import the app and models, but don't fail if database is not available
try:
    from backend.models import db, Flight, DronePosition, SensorReading
    from backend.app import create_app

    # Don't immediately initialize the database
    db_available = True
except (ImportError, OperationalError) as e:
    print(f"Database connection failed: {e}")
    print("Tests requiring database access will be skipped")
    db_available = False

@pytest.fixture(scope='module')
def app():
    """Create a Flask app configured for testing"""
    if not db_available:
        pytest.skip("Database connection not available")
        
    # Set up a test-specific PostgreSQL database
    test_db_name = 'drone_monitoring_db_test'
    
    # Use a separate test database
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': f'postgresql://postgres:postgres@127.0.0.1:5432/{test_db_name}',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False
    })
    
    # Create test database tables
    with app.app_context():
        db.create_all()
    
    yield app
    
    # Clean up after tests
    with app.app_context():
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """A test client for the app."""
    if not db_available:
        pytest.skip("Database connection not available")
        
    return app.test_client()

@pytest.fixture
def runner(app):
    """A test CLI runner for the app."""
    if not db_available:
        pytest.skip("Database connection not available")
        
    return app.test_cli_runner()

@pytest.fixture
def db_session(app):
    """Create a database session for testing."""
    if not db_available:
        pytest.skip("Database connection not available")
        
    with app.app_context():
        yield db.session

@pytest.fixture(scope='function')
def session(app):
    """Create a new database session for a test"""
    with app.app_context():
        try:
            db.session.begin_nested()
            yield db.session
            db.session.rollback()
        except OperationalError:
            pytest.skip("Database connection failed - skipping database tests")

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

# This allows tests unrelated to the backend to run even if the backend can't be imported
if not db_available:
    print("Backend import error: some fixtures will not be available") 