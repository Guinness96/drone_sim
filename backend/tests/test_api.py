"""Tests for the API endpoints"""
import json
from datetime import datetime, UTC
from backend.models import Flight, DronePosition, SensorReading
from backend.app import db

def test_hello_world(client):
    """Test the root endpoint"""
    response = client.get('/')
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert 'message' in data
    assert 'Drone Monitoring API is running' in data['message']

def test_start_flight(client, session):
    """Test starting a new flight"""
    # Request to start a new flight
    response = client.post('/api/flights/start')
    data = json.loads(response.data)
    
    # Verify the response
    assert response.status_code == 201
    assert 'flight_id' in data
    assert 'start_time' in data
    
    # Verify the flight was created in the database
    flight = db.session.get(Flight, data['flight_id'])
    assert flight is not None
    assert flight.start_time is not None
    assert flight.end_time is None

def test_end_flight(client, sample_flight):
    """Test ending a flight"""
    # Request to end the flight
    response = client.post(f'/api/flights/{sample_flight.id}/end')
    data = json.loads(response.data)
    
    # Verify the response
    assert response.status_code == 200
    assert 'flight_id' in data
    assert 'end_time' in data
    
    # Verify the flight was updated in the database
    flight = db.session.get(Flight, sample_flight.id)
    assert flight.end_time is not None

def test_log_flight_data(client, sample_flight):
    """Test logging flight data"""
    # Create test data
    test_data = {
        "timestamp": datetime.now(UTC).isoformat(),
        "latitude": 51.507351,
        "longitude": -0.127758,
        "altitude": 100.0,
        "temperature": 20.0,
        "humidity": 60.0,
        "air_quality_index": 50.0
    }
    
    # Request to log data
    response = client.post(
        f'/api/flights/{sample_flight.id}/log_data',
        json=test_data,
        content_type='application/json'
    )
    data = json.loads(response.data)
    
    # Verify the response
    assert response.status_code == 201
    assert 'position_id' in data
    assert 'reading_id' in data
    assert 'is_anomaly' in data
    
    # Verify the data was saved in the database
    position = db.session.get(DronePosition, data['position_id'])
    assert position is not None
    assert position.flight_id == sample_flight.id
    assert position.latitude == test_data['latitude']
    assert position.longitude == test_data['longitude']
    assert position.altitude == test_data['altitude']
    
    reading = db.session.get(SensorReading, data['reading_id'])
    assert reading is not None
    assert reading.drone_position_id == position.id
    assert reading.temperature == test_data['temperature']
    assert reading.humidity == test_data['humidity']
    assert reading.air_quality_index == test_data['air_quality_index']
    assert reading.is_anomaly == data['is_anomaly']

def test_log_flight_data_anomaly(client, sample_flight):
    """Test logging flight data with anomalous values"""
    # Create test data with anomalous values
    test_data = {
        "timestamp": datetime.now(UTC).isoformat(),
        "latitude": 51.507351,
        "longitude": -0.127758,
        "altitude": 100.0,
        "temperature": 40.0,  # Anomalous temperature (> 30)
        "humidity": 95.0,     # Anomalous humidity (> 90)
        "air_quality_index": 200.0  # Anomalous AQI (> 150)
    }
    
    # Request to log data
    response = client.post(
        f'/api/flights/{sample_flight.id}/log_data',
        json=test_data,
        content_type='application/json'
    )
    data = json.loads(response.data)
    
    # Verify the anomaly was detected
    assert response.status_code == 201
    assert data['is_anomaly'] is True
    
    # Verify the anomaly was saved in the database
    reading = db.session.get(SensorReading, data['reading_id'])
    assert reading.is_anomaly is True

def test_get_all_flights(client, sample_flight):
    """Test getting all flights"""
    # Request to get all flights
    response = client.get('/api/flights')
    data = json.loads(response.data)
    
    # Verify the response
    assert response.status_code == 200
    assert isinstance(data, list)
    assert len(data) >= 1  # At least the sample flight
    
    # Verify the flight data is correct
    flight_data = next((f for f in data if f['id'] == sample_flight.id), None)
    assert flight_data is not None
    assert 'id' in flight_data
    assert 'start_time' in flight_data
    assert 'end_time' in flight_data

def test_get_flight_data(client, sample_flight, sample_position, sample_reading):
    """Test getting flight data"""
    # Request to get flight data
    response = client.get(f'/api/flights/{sample_flight.id}/data')
    data = json.loads(response.data)
    
    # Verify the response
    assert response.status_code == 200
    assert 'id' in data
    assert data['id'] == sample_flight.id
    assert 'start_time' in data
    assert 'positions' in data
    assert isinstance(data['positions'], list)
    assert len(data['positions']) >= 1
    
    # Verify position data
    position_data = data['positions'][0]
    assert 'id' in position_data
    assert 'latitude' in position_data
    assert 'longitude' in position_data
    assert 'altitude' in position_data
    assert 'sensor_readings' in position_data
    assert isinstance(position_data['sensor_readings'], list)
    
    # Verify sensor reading data
    if len(position_data['sensor_readings']) > 0:
        reading_data = position_data['sensor_readings'][0]
        assert 'id' in reading_data
        assert 'temperature' in reading_data
        assert 'humidity' in reading_data
        assert 'air_quality_index' in reading_data
        assert 'is_anomaly' in reading_data

def test_get_latest_sensor_readings(client, sample_reading):
    """Test getting latest sensor readings"""
    # Request to get latest sensor readings
    response = client.get('/api/sensor_readings/latest')
    data = json.loads(response.data)
    
    # Verify the response
    assert response.status_code == 200
    assert isinstance(data, list)
    assert len(data) >= 1
    
    # Verify reading data
    reading_data = data[0]
    assert 'id' in reading_data
    assert 'timestamp' in reading_data
    assert 'temperature' in reading_data
    assert 'humidity' in reading_data
    assert 'air_quality_index' in reading_data
    assert 'is_anomaly' in reading_data
    assert 'position' in reading_data

def test_flight_not_found(client):
    """Test handling non-existent flight"""
    # Try to get a non-existent flight
    response = client.get('/api/flights/9999/data')
    data = json.loads(response.data)
    
    # Verify error response
    assert response.status_code == 404
    assert 'error' in data
    assert 'not found' in data['error'] 