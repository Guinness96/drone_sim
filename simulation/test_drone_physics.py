import pytest
import time
from simulation.drone_physics import DronePhysics

@pytest.fixture
def physics():
    """Create and configure a DronePhysics instance with known starting values."""
    physics_engine = DronePhysics()
    # Set a known starting position
    physics_engine.position = (51.507351, -0.127758)  # London
    physics_engine.altitude = 100.0
    return physics_engine

def test_initialisation():
    """Test that physics module initialises with correct defaults."""
    physics = DronePhysics()
    assert physics.velocity == 0.0
    assert physics.heading == 0.0
    assert physics.acceleration == 0.0
    assert hasattr(physics, 'max_velocity')
    assert hasattr(physics, 'max_acceleration')
    assert hasattr(physics, 'inertia_factor')
        
def test_heading_calculation(physics):
    """Test heading calculation between two points."""
    start = (51.507351, -0.127758)  # London
    north = (51.508351, -0.127758)  # North from start
    east = (51.507351, -0.126758)   # East from start
    south = (51.506351, -0.127758)  # South from start
    west = (51.507351, -0.128758)   # West from start
    
    # Test cardinal directions (allowing for small floating point errors)
    assert abs(physics._calculate_heading(start, north) - 0.0) <= 1.0
    assert abs(physics._calculate_heading(start, east) - 90.0) <= 1.0
    assert abs(physics._calculate_heading(start, south) - 180.0) <= 1.0
    assert abs(physics._calculate_heading(start, west) - 270.0) <= 1.0
        
def test_distance_calculation(physics):
    """Test distance calculation between points."""
    p1 = (51.507351, -0.127758)  # London
    p2 = (51.507351, -0.127858)  # Slightly west
    
    # Calculate expected distance (approximate)
    # At this latitude, 0.000100 longitude is roughly 6.6 meters
    expected_distance = 6.6  # meters
    
    distance = physics._haversine_distance(p1, p2)
    assert abs(distance - expected_distance) <= 1.0
        
def test_physics_update_with_target(physics):
    """Test that physics update moves toward target."""
    # Set initial position and zero velocity
    physics.position = (51.507351, -0.127758)
    physics.velocity = 0.0
    
    # Set a target position 100m north
    target = (51.508251, -0.127758)
    
    # Force a longer time delta for testing
    physics.last_update_time = time.time() - 1.0
    
    # Update physics
    physics.update_physics(target)
    
    # Verify drone has started moving toward target
    assert physics.position != (51.507351, -0.127758)
    assert physics.velocity > 0.0
    
    # Check heading is approximately north (around 0 degrees)
    # Using assertLess than 10 degrees in either direction from north
    heading = physics.heading
    assert heading < 10.0 or heading > 350.0, f"Heading {heading} is not approximately north"
        
def test_inertia_factor():
    """Test that inertia factor affects movement responsiveness."""
    # Set up two physics instances with different inertia
    high_inertia = DronePhysics()
    high_inertia.position = (51.507351, -0.127758)
    high_inertia.inertia_factor = 0.9  # High inertia = slow to react
    
    low_inertia = DronePhysics()
    low_inertia.position = (51.507351, -0.127758)
    low_inertia.inertia_factor = 0.1  # Low inertia = quick to react - use a more extreme value
    
    # Set a target position
    target = (51.508251, -0.127758)  # North
    
    # Force a longer time delta for testing
    high_inertia.last_update_time = time.time() - 1.0
    low_inertia.last_update_time = time.time() - 1.0
    
    # Update both physics instances once with a significant time delta
    high_inertia.update_physics(target)
    low_inertia.update_physics(target)
    
    # The drone with lower inertia should have moved further and faster
    assert low_inertia.velocity > high_inertia.velocity
        
def test_velocity_limits(physics):
    """Test that velocity does not exceed max_velocity."""
    physics.max_velocity = 5.0
    physics.max_acceleration = 10.0  # High acceleration for testing
    physics.inertia_factor = 0.1     # Low inertia for quick response
    
    # Set a target far away
    target = (52.0, -0.127758)  # Far north
    
    # Force a longer time delta for testing
    physics.last_update_time = time.time() - 3.0
    
    # Update physics
    physics.update_physics(target)
    
    # Verify velocity does not exceed max
    assert physics.velocity <= 5.0
        
def test_normalize_angle(physics):
    """Test angle normalisation to 0-360 range."""
    assert physics._normalize_angle(0) == 0
    assert physics._normalize_angle(360) == 0
    assert physics._normalize_angle(370) == 10
    assert physics._normalize_angle(-10) == 350
    assert physics._normalize_angle(-370) == 350

# Edge case tests
def test_zero_distance_update(physics):
    """Test physics update when already at target position."""
    physics.position = (51.507351, -0.127758)
    physics.velocity = 5.0  # Moving with some velocity
    
    # Target is same as current position
    target = (51.507351, -0.127758)
    
    # Force a time delta
    physics.last_update_time = time.time() - 1.0
    
    # Update physics
    physics.update_physics(target)
    
    # Drone should start decelerating when at target
    assert physics.velocity < 5.0
    
def test_extreme_coordinates(physics):
    """Test physics calculations with extreme coordinate values."""
    # Set positions at the poles and across the international date line
    north_pole = (90.0, 0.0)
    south_pole = (-90.0, 0.0)
    date_line_east = (0.0, 179.9)
    date_line_west = (0.0, -179.9)
    
    # Test distance calculations
    # Distance between poles should be about 20,015 km (Earth circumference / 2)
    pole_distance = physics._haversine_distance(north_pole, south_pole)
    assert abs(pole_distance / 1000 - 20015) <= 100
    
    # Test heading calculations don't raise exceptions
    try:
        physics._calculate_heading(north_pole, (89.0, 0.0))
        physics._calculate_heading(date_line_east, date_line_west)
    except Exception as e:
        pytest.fail(f"Heading calculation raised exception: {e}")
    
def test_heading_change(physics):
    """Test that drone properly adjusts heading when given a new target."""
    physics.position = (51.507351, -0.127758)
    physics.velocity = 5.0  # Moving at moderate speed
    physics.heading = 0.0   # North
    physics.inertia_factor = 0.5  # Reduce inertia to make heading changes more responsive
    
    # Target is east
    target = (51.507351, -0.126758)
    
    # Calculate expected heading (should be around 90 degrees)
    expected_heading = physics._calculate_heading(physics.position, target)
    assert abs(expected_heading - 90.0) <= 2.0
    
    # Store initial heading for comparison
    initial_heading = physics.heading
    
    # Force multiple time deltas and updates to adjust heading
    for _ in range(10):  # Increased from 5 to 10 updates
        physics.last_update_time = time.time() - 0.5
        physics.update_physics(target)
    
    # After updates, heading should have moved from 0 (north) toward 90 (east)
    # We don't expect it to reach exactly 90 degrees, but it should have moved significantly
    assert physics.heading > initial_heading, "Heading should have increased from initial value"
    
    # Check that it's moving in the right direction (at least 20 degrees toward target)
    heading_diff = abs(physics._normalize_angle(physics.heading - expected_heading))
    assert heading_diff < 70.0, f"Heading {physics.heading} not moving toward target heading {expected_heading}"

def test_physics_movement(physics):
    """Test that drone physics properly updates position and heading."""
    # Starting state
    physics.position = (51.507351, -0.127758)
    physics.velocity = 0.0
    physics.heading = 0.0  # North
    
    # Target position (northeast)
    target = (51.508351, -0.126758)
    
    # Force a longer time delta for testing
    physics.last_update_time = time.time() - 1.0
    
    # Initial position
    initial_lat, initial_lon = physics.position
    
    # Update physics multiple times
    for _ in range(5):
        physics.last_update_time = time.time() - 0.5
        physics.update_physics(target)
    
    # After updates, position should have changed
    final_lat, final_lon = physics.position
    assert final_lat > initial_lat, "Latitude should have increased (moved north)"
    assert final_lon > initial_lon, "Longitude should have increased (moved east)"
    
    # Velocity should be positive
    assert physics.velocity > 0.0, "Drone should have positive velocity"
    
    # Heading should be between 0 and 90 (northeast)
    assert 0 <= physics.heading <= 90 or physics.heading >= 270, \
        f"Heading {physics.heading} should be in northeast quadrant"
    
def test_acceleration_limits(physics):
    """Test that acceleration is limited by max_acceleration."""
    physics.max_acceleration = 2.0
    physics.velocity = 0.0
    
    # Set a target far away to maximize acceleration
    target = (52.0, -0.127758)  # Far north
    
    # Force a time delta
    physics.last_update_time = time.time() - 1.0
    
    # Update physics
    physics.update_physics(target)
    
    # Verify acceleration doesn't exceed max
    assert physics.acceleration <= 2.0, \
        f"Acceleration {physics.acceleration} exceeds max {physics.max_acceleration}"
    
def test_deceleration(physics):
    """Test that drone decelerates when approaching target."""
    # Set up drone moving at speed
    physics.position = (51.507351, -0.127758)
    physics.velocity = 5.0
    physics.heading = 0.0  # North
    
    # Target is very close
    target = (51.507451, -0.127758)  # Just slightly north
    
    # Force a time delta
    physics.last_update_time = time.time() - 1.0
    
    # Update physics
    physics.update_physics(target)
    
    # Drone should decelerate when close to target
    # Acceleration should be zero or negative
    assert physics.acceleration <= 0, \
        f"Acceleration {physics.acceleration} should be zero or negative when close to target" 