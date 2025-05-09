import pytest
import math
from unittest.mock import patch, MagicMock
from simulation.drone_simulator import DroneSimulator
from simulation.drone_physics import DronePhysics

@pytest.fixture
def mock_api():
    """Set up mock API calls to avoid network and DB dependencies."""
    with patch('requests.post') as mock_post:
        mock_post.return_value.status_code = 201
        mock_post.return_value.json.return_value = {
            'flight_id': 1,
            'position_id': 1,
            'reading_id': 1,
            'is_anomaly': False
        }
        yield mock_post

def test_simulator_initializes_physics(mock_api):
    """Test that the simulator properly initialises the physics engine."""
    # Create simulator
    simulator = DroneSimulator(api_url="mock://api")
    
    # Verify physics engine is correctly configured
    assert isinstance(simulator.physics, DronePhysics)
    assert simulator.physics.max_velocity == 10.0
    assert simulator.physics.max_acceleration == 2.0
    assert simulator.physics.inertia_factor == 0.8

def test_physics_customization(mock_api):
    """Test that physics parameters can be customised via config."""
    config = {
        "physics": {
            "max_velocity": 5.0,      # Lower max speed
            "max_acceleration": 1.0,   # Lower acceleration
            "inertia_factor": 0.5,     # More responsive handling
            "enable_physics": True
        }
    }
    
    # Create simulator with custom physics
    simulator = DroneSimulator(api_url="mock://api", config=config)
    
    # Verify physics engine parameters match config
    assert simulator.physics.max_velocity == 5.0
    assert simulator.physics.max_acceleration == 1.0
    assert simulator.physics.inertia_factor == 0.5

def test_sensor_data_includes_physics_telemetry(mock_api):
    """Test that sensor readings include physics-based telemetry data."""
    simulator = DroneSimulator(api_url="mock://api")
    
    # Set specific physics values for testing
    simulator.physics.velocity = 3.5
    simulator.physics.heading = 45.0
    simulator.physics.acceleration = 1.2
    
    # Generate a sensor reading
    position = (51.5074, -0.1278)  # London
    reading = simulator.generate_sensor_reading(position)
    
    # Verify telemetry data is included in the sensor reading
    assert reading['velocity'] == 3.5
    assert reading['heading'] == 45.0
    assert reading['acceleration'] == 1.2

def test_sensor_noise_levels(mock_api):
    """Test that sensor noise levels affect readings."""
    # Create simulator with low noise
    simulator_low_noise = DroneSimulator(api_url="mock://api", config={
        "sensor_noise_levels": {
            "temperature": 1.0,
            "humidity": 1.0,
            "air_quality": 1.0,
            "altitude": 1.0
        }
    })
    
    # Create simulator with high noise
    simulator_high_noise = DroneSimulator(api_url="mock://api", config={
        "sensor_noise_levels": {
            "temperature": 10.0,
            "humidity": 30.0,
            "air_quality": 50.0,
            "altitude": 20.0
        }
    })
    
    # Collect several readings to analyse variability
    position = (51.5074, -0.1278)  # London
    low_noise_temps = []
    high_noise_temps = []
    
    for _ in range(20):
        low_noise_temps.append(simulator_low_noise.generate_sensor_reading(position)['temperature'])
        high_noise_temps.append(simulator_high_noise.generate_sensor_reading(position)['temperature'])
    
    # Calculate temperature variances (max-min range)
    low_temp_variance = max(low_noise_temps) - min(low_noise_temps)
    high_temp_variance = max(high_noise_temps) - min(high_noise_temps)
    
    # High noise configuration should produce more variable readings
    assert high_temp_variance > low_temp_variance, \
        f"High noise variance ({high_temp_variance}) should be greater than low noise variance ({low_temp_variance})" 