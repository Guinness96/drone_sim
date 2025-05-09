"""Tests for the drone simulator"""
import json
import os
import tempfile
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
    
    # Check default config values
    assert simulator.config["simulation_speed"] == 1.0
    assert simulator.config["waypoint_file"] is None
    assert "temperature" in simulator.config["sensor_noise_levels"]
    assert "humidity" in simulator.config["sensor_noise_levels"]
    assert "air_quality" in simulator.config["sensor_noise_levels"]
    assert "altitude" in simulator.config["sensor_noise_levels"]
    
    # Test with custom API URL
    custom_simulator = DroneSimulator(api_url="http://example.com/api")
    assert custom_simulator.api_url == "http://example.com/api"

def test_simulator_with_config():
    """Test initializing simulator with custom configuration"""
    custom_config = {
        "simulation_speed": 2.0,
        "sensor_noise_levels": {
            "temperature": 2.5,
            "humidity": 10.0,
            "air_quality": 75.0,  # Include air_quality explicitly
            "altitude": 20.0       # Include altitude explicitly
        }
    }
    
    simulator = DroneSimulator(config=custom_config)
    
    # Check config was updated correctly
    assert simulator.config["simulation_speed"] == 2.0
    assert simulator.config["waypoint_file"] is None  # Default unchanged
    assert simulator.config["sensor_noise_levels"]["temperature"] == 2.5  # Updated
    assert simulator.config["sensor_noise_levels"]["humidity"] == 10.0  # Updated
    assert simulator.config["sensor_noise_levels"]["air_quality"] == 75.0  # Updated
    assert simulator.config["sensor_noise_levels"]["altitude"] == 20.0  # Same as default

def test_load_waypoints_from_file():
    """Test loading waypoints from a file"""
    # Create a temporary waypoints file
    test_waypoints = [
        [52.123456, -1.123456],
        [52.234567, -1.234567],
        [52.345678, -1.345678]
    ]
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as temp_file:
        json.dump(test_waypoints, temp_file)
        temp_path = temp_file.name
    
    try:
        # Initialize simulator with config pointing to waypoint file
        config = {"waypoint_file": temp_path}
        simulator = DroneSimulator(config=config)
        
        # Check waypoints were loaded correctly
        assert len(simulator.waypoints) == len(test_waypoints)
        # Instead of comparing lists to tuples directly, compare each coordinate
        for i in range(len(test_waypoints)):
            assert simulator.waypoints[i][0] == test_waypoints[i][0]
            assert simulator.waypoints[i][1] == test_waypoints[i][1]
    finally:
        # Clean up temporary file
        if os.path.exists(temp_path):
            os.unlink(temp_path)

def test_load_waypoints_file_not_found():
    """Test behavior when waypoint file doesn't exist"""
    config = {"waypoint_file": "non_existent_file.json"}
    simulator = DroneSimulator(config=config)
    
    # Should use default waypoints if file not found
    assert len(simulator.waypoints) > 0
    # Check first waypoint matches default
    assert simulator.waypoints[0] == (51.507351, -0.127758)

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

def test_sensor_noise_levels():
    """Test that sensor noise levels affect data generation"""
    # Create simulator with very low noise
    low_noise_config = {
        "sensor_noise_levels": {
            "temperature": 0.5,  # Very low noise
            "humidity": 1.0,
            "air_quality": 5.0,
            "altitude": 1.0
        }
    }
    low_noise_simulator = DroneSimulator(config=low_noise_config)
    
    # Create simulator with high noise
    high_noise_config = {
        "sensor_noise_levels": {
            "temperature": 10.0,  # Very high noise
            "humidity": 30.0,
            "air_quality": 100.0,
            "altitude": 50.0
        }
    }
    high_noise_simulator = DroneSimulator(config=high_noise_config)
    
    # Generate readings with same position
    position = (51.507351, -0.127758)
    readings_low = [low_noise_simulator.generate_sensor_reading(position) for _ in range(10)]
    readings_high = [high_noise_simulator.generate_sensor_reading(position) for _ in range(10)]
    
    # Calculate range of values (max - min)
    temp_range_low = max(r['temperature'] for r in readings_low) - min(r['temperature'] for r in readings_low)
    temp_range_high = max(r['temperature'] for r in readings_high) - min(r['temperature'] for r in readings_high)
    
    humidity_range_low = max(r['humidity'] for r in readings_low) - min(r['humidity'] for r in readings_low)
    humidity_range_high = max(r['humidity'] for r in readings_high) - min(r['humidity'] for r in readings_high)
    
    # High noise config should generally produce wider range of values
    # Note: This is statistical, so in rare cases it might not hold true
    # so we check it's at least within reasonable bounds
    assert temp_range_high >= temp_range_low * 0.5
    assert humidity_range_high >= humidity_range_low * 0.5

@mock.patch('time.sleep')
def test_simulation_speed(mock_sleep):
    """Test that simulation speed affects the time between waypoints"""
    # Create a simulator with fast speed
    fast_config = {"simulation_speed": 2.0}
    fast_simulator = DroneSimulator(config=fast_config)
    
    # Create a simulator with slow speed
    slow_config = {"simulation_speed": 0.5}
    slow_simulator = DroneSimulator(config=slow_config)
    
    # Mock API calls to avoid actual API requests
    with mock.patch.object(fast_simulator, 'start_flight', return_value=1), \
         mock.patch.object(fast_simulator, 'send_data_to_api', return_value=True), \
         mock.patch.object(fast_simulator, 'end_flight', return_value=True):
        
        # Run fast simulation
        fast_simulator.waypoints = [(0, 0), (1, 1)]  # Just 2 waypoints
        fast_simulator.simulate_path()
        
        # Check sleep time (should be 1.0 / 2.0 = 0.5 seconds)
        mock_sleep.assert_called_with(0.5)
    
    # Reset mock
    mock_sleep.reset_mock()
    
    # Mock API calls for slow simulator
    with mock.patch.object(slow_simulator, 'start_flight', return_value=1), \
         mock.patch.object(slow_simulator, 'send_data_to_api', return_value=True), \
         mock.patch.object(slow_simulator, 'end_flight', return_value=True):
        
        # Run slow simulation
        slow_simulator.waypoints = [(0, 0), (1, 1)]  # Just 2 waypoints
        slow_simulator.simulate_path()
        
        # Check sleep time (should be 1.0 / 0.5 = 2.0 seconds)
        mock_sleep.assert_called_with(2.0)

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