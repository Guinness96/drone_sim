"""Tests for the database models"""
from datetime import datetime, UTC
from backend.models import Flight, DronePosition, SensorReading
from backend.app import db

def test_flight_model(session):
    """Test the Flight model"""
    # Create a flight
    flight = Flight(start_time=datetime.now(UTC))
    session.add(flight)
    session.commit()
    
    # Verify the flight was created
    retrieved_flight = session.get(Flight, flight.id)
    assert retrieved_flight is not None
    assert retrieved_flight.start_time is not None
    assert retrieved_flight.end_time is None
    assert retrieved_flight.positions == []
    
    # Test updating a flight
    retrieved_flight.end_time = datetime.now(UTC)
    session.commit()
    
    # Verify the update
    updated_flight = session.get(Flight, flight.id)
    assert updated_flight.end_time is not None
    
    # Test representation
    assert repr(flight).startswith('<Flight')

def test_drone_position_model(session, sample_flight):
    """Test the DronePosition model"""
    # Create a position
    position = DronePosition(
        flight_id=sample_flight.id,
        timestamp=datetime.now(UTC),
        latitude=51.507351,
        longitude=-0.127758,
        altitude=100.0
    )
    session.add(position)
    session.commit()
    
    # Verify the position was created
    retrieved_position = session.get(DronePosition, position.id)
    assert retrieved_position is not None
    assert retrieved_position.flight_id == sample_flight.id
    assert retrieved_position.timestamp is not None
    assert retrieved_position.latitude == 51.507351
    assert retrieved_position.longitude == -0.127758
    assert retrieved_position.altitude == 100.0
    assert retrieved_position.sensor_readings == []
    
    # Test representation
    assert repr(position).startswith('<DronePosition')
    
    # Test relationship with Flight
    assert position in sample_flight.positions

def test_sensor_reading_model(session, sample_position):
    """Test the SensorReading model"""
    # Create a sensor reading
    reading = SensorReading(
        drone_position_id=sample_position.id,
        timestamp=datetime.now(UTC),
        temperature=20.0,
        humidity=60.0,
        air_quality_index=50.0,
        is_anomaly=False
    )
    session.add(reading)
    session.commit()
    
    # Verify the reading was created
    retrieved_reading = session.get(SensorReading, reading.id)
    assert retrieved_reading is not None
    assert retrieved_reading.drone_position_id == sample_position.id
    assert retrieved_reading.timestamp is not None
    assert retrieved_reading.temperature == 20.0
    assert retrieved_reading.humidity == 60.0
    assert retrieved_reading.air_quality_index == 50.0
    assert retrieved_reading.is_anomaly is False
    
    # Test updating a reading
    retrieved_reading.is_anomaly = True
    session.commit()
    
    # Verify the update
    updated_reading = session.get(SensorReading, reading.id)
    assert updated_reading.is_anomaly is True
    
    # Test representation
    assert repr(reading).startswith('<SensorReading')
    
    # Test relationship with DronePosition
    assert reading in sample_position.sensor_readings

def test_cascading_delete(session):
    """Test that deleting a flight cascades to positions and readings"""
    # Create test data with relationships
    flight = Flight(start_time=datetime.now(UTC))
    session.add(flight)
    session.flush()
    
    position = DronePosition(
        flight_id=flight.id,
        timestamp=datetime.now(UTC),
        latitude=51.507351,
        longitude=-0.127758,
        altitude=100.0
    )
    session.add(position)
    session.flush()
    
    reading = SensorReading(
        drone_position_id=position.id,
        timestamp=datetime.now(UTC),
        temperature=20.0,
        humidity=60.0,
        air_quality_index=50.0,
        is_anomaly=False
    )
    session.add(reading)
    session.commit()
    
    # Store IDs for later verification
    flight_id = flight.id
    position_id = position.id
    reading_id = reading.id
    
    # Delete the flight
    session.delete(flight)
    session.commit()
    
    # Verify cascade deletion
    assert session.get(Flight, flight_id) is None
    assert session.get(DronePosition, position_id) is None
    assert session.get(SensorReading, reading_id) is None 