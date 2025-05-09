"""Tests for the drone simulator"""
import json
from unittest import mock
from datetime import datetime
from simulation.drone_simulator import DroneSimulator

class MockResponse:
    """Mock response class to simulate requests.Response objects"""
    def __init__(self, json_data, status_code):
        self.json_data = json_data
        self.status_code = status_code
        self.text = json.dumps(json_data)
    
    def json(self):
        return self.json_data

def test_drone_simulator_init():
    """Test the initialization of the DroneSimulator class"""
    simulator = DroneSimulator()
    
    # Check default values
    assert simulator.api_url == "http://localhost:5000"
    assert simulator.flight_id is None
    assert len(simulator.waypoints) > 0
    
    # Test with custom API URL
    custom_simulator = DroneSimulator(api_url="http://example.com/api")
    assert custom_simulator.api_url == "http://example.com/api"

def test_generate_sensor_reading():
    """Test that sensor readings are generated correctly"""
    simulator = DroneSimulator()
    position = (51.507351, -0.127758)
    
    reading = simulator.generate_sensor_reading(position)
    
    # Check reading contains all expected fields
    assert 'timestamp' in reading
    assert 'latitude' in reading
    assert 'longitude' in reading
    assert 'altitude' in reading
    assert 'temperature' in reading
    assert 'humidity' in reading
    assert 'air_quality_index' in reading
    
    # Check values are within expected ranges
    assert reading['latitude'] == position[0]
    assert reading['longitude'] == position[1]
    assert isinstance(reading['altitude'], float)
    assert 80 <= reading['altitude'] <= 120  # Around 100m ±20
    assert 15 <= reading['temperature'] <= 25  # Around 20°C ±5
    assert 40 <= reading['humidity'] <= 80  # Around 60% ±20
    assert 20 <= reading['air_quality_index'] <= 150  # Around 50 ±100

@mock.patch('requests.post')
def test_start_flight_success(mock_post):
    """Test starting a flight with a successful API response"""
    # Mock successful API response
    mock_response = MockResponse({'flight_id': 1, 'start_time': datetime.now().isoformat()}, 201)
    mock_post.return_value = mock_response
    
    simulator = DroneSimulator()
    flight_id = simulator.start_flight()
    
    # Verify API call and result
    mock_post.assert_called_once_with(f"{simulator.api_url}/api/flights/start")
    assert flight_id == 1
    assert simulator.flight_id == 1

@mock.patch('requests.post')
def test_start_flight_failure(mock_post):
    """Test starting a flight with a failed API response"""
    # Mock failed API response
    mock_response = MockResponse({'error': 'Service unavailable'}, 500)
    mock_post.return_value = mock_response
    
    simulator = DroneSimulator()
    flight_id = simulator.start_flight()
    
    # Verify API call and result
    mock_post.assert_called_once_with(f"{simulator.api_url}/api/flights/start")
    assert flight_id is None
    assert simulator.flight_id is None

@mock.patch('requests.post')
def test_end_flight_success(mock_post):
    """Test ending a flight with a successful API response"""
    # Mock successful API response
    mock_response = MockResponse({'flight_id': 1, 'end_time': datetime.now().isoformat()}, 200)
    mock_post.return_value = mock_response
    
    simulator = DroneSimulator()
    simulator.flight_id = 1
    result = simulator.end_flight()
    
    # Verify API call and result
    mock_post.assert_called_once_with(f"{simulator.api_url}/api/flights/1/end")
    assert result is True

@mock.patch('requests.post')
def test_end_flight_no_flight_id(mock_post):
    """Test ending a flight without a flight_id"""
    simulator = DroneSimulator()
    result = simulator.end_flight()
    
    # Verify no API call and result
    mock_post.assert_not_called()
    assert result is False

@mock.patch('requests.post')
def test_send_data_to_api_success(mock_post):
    """Test sending data to API with a successful response"""
    # Mock successful API response
    mock_response = MockResponse({
        'position_id': 1,
        'reading_id': 1,
        'is_anomaly': False
    }, 201)
    mock_post.return_value = mock_response
    
    # Test data
    test_data = {
        'timestamp': datetime.now().isoformat(),
        'latitude': 51.507351,
        'longitude': -0.127758,
        'altitude': 100.0,
        'temperature': 20.0,
        'humidity': 60.0,
        'air_quality_index': 50.0
    }
    
    # Send data
    simulator = DroneSimulator()
    simulator.flight_id = 1
    result = simulator.send_data_to_api(test_data)
    
    # Verify API call and result
    mock_post.assert_called_once_with(
        f"{simulator.api_url}/api/flights/1/log_data",
        json=test_data
    )
    assert result is True

@mock.patch('requests.post')
def test_send_data_to_api_no_flight_id(mock_post):
    """Test sending data to API without a flight_id"""
    # Test data
    test_data = {
        'timestamp': datetime.now().isoformat(),
        'latitude': 51.507351,
        'longitude': -0.127758,
        'altitude': 100.0,
        'temperature': 20.0,
        'humidity': 60.0,
        'air_quality_index': 50.0
    }
    
    # Send data
    simulator = DroneSimulator()
    result = simulator.send_data_to_api(test_data)
    
    # Verify no API call and result
    mock_post.assert_not_called()
    assert result is False

@mock.patch.object(DroneSimulator, 'start_flight')
@mock.patch.object(DroneSimulator, 'send_data_to_api')
@mock.patch.object(DroneSimulator, 'end_flight')
def test_simulate_path(mock_end_flight, mock_send_data, mock_start_flight):
    """Test the main simulate_path method with mocked API calls"""
    # Configure mocks
    mock_start_flight.return_value = 1
    mock_send_data.return_value = True
    mock_end_flight.return_value = True
    
    # Create simulator with a limited number of waypoints for faster testing
    simulator = DroneSimulator()
    simulator.waypoints = simulator.waypoints[:3]  # Use only first 3 waypoints
    
    # Run simulation
    flight_data = simulator.simulate_path()
    
    # Verify API calls
    mock_start_flight.assert_called_once()
    assert mock_send_data.call_count == len(simulator.waypoints)
    mock_end_flight.assert_called_once()
    
    # Verify collected data
    assert len(flight_data) == len(simulator.waypoints)
    for data_point in flight_data:
        assert 'timestamp' in data_point
        assert 'latitude' in data_point
        assert 'longitude' in data_point
        assert 'altitude' in data_point
        assert 'temperature' in data_point
        assert 'humidity' in data_point
        assert 'air_quality_index' in data_point 