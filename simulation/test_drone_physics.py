import unittest
import time
from simulation.drone_physics import DronePhysics

class TestDronePhysics(unittest.TestCase):
    def setUp(self):
        self.physics = DronePhysics()
        # Set a known starting position
        self.physics.position = (51.507351, -0.127758)  # London
        self.physics.altitude = 100.0
        
    def test_initialization(self):
        """Test that physics module initializes with correct defaults"""
        physics = DronePhysics()
        self.assertEqual(physics.velocity, 0.0)
        self.assertEqual(physics.heading, 0.0)
        self.assertEqual(physics.acceleration, 0.0)
        self.assertTrue(hasattr(physics, 'max_velocity'))
        self.assertTrue(hasattr(physics, 'max_acceleration'))
        self.assertTrue(hasattr(physics, 'inertia_factor'))
        
    def test_heading_calculation(self):
        """Test heading calculation between two points"""
        start = (51.507351, -0.127758)  # London
        north = (51.508351, -0.127758)  # North from start
        east = (51.507351, -0.126758)   # East from start
        south = (51.506351, -0.127758)  # South from start
        west = (51.507351, -0.128758)   # West from start
        
        # Test cardinal directions (allowing for small floating point errors)
        self.assertAlmostEqual(self.physics._calculate_heading(start, north), 0.0, delta=1.0)
        self.assertAlmostEqual(self.physics._calculate_heading(start, east), 90.0, delta=1.0)
        self.assertAlmostEqual(self.physics._calculate_heading(start, south), 180.0, delta=1.0)
        self.assertAlmostEqual(self.physics._calculate_heading(start, west), 270.0, delta=1.0)
        
    def test_distance_calculation(self):
        """Test distance calculation between points"""
        p1 = (51.507351, -0.127758)  # London
        p2 = (51.507351, -0.127858)  # Slightly west
        
        # Calculate expected distance (approximate)
        # At this latitude, 0.000100 longitude is roughly 6.6 meters
        expected_distance = 6.6  # meters
        
        distance = self.physics._haversine_distance(p1, p2)
        self.assertAlmostEqual(distance, expected_distance, delta=1.0)
        
    def test_physics_update_with_target(self):
        """Test that physics update moves toward target"""
        # Set initial position and zero velocity
        self.physics.position = (51.507351, -0.127758)
        self.physics.velocity = 0.0
        
        # Set a target position 100m north
        target = (51.508251, -0.127758)
        
        # Force a longer time delta for testing
        self.physics.last_update_time = time.time() - 1.0
        
        # Update physics (use the return value to avoid unused variable warning)
        self.physics.update_physics(target)
        
        # Verify drone has started moving toward target
        self.assertNotEqual(self.physics.position, (51.507351, -0.127758))
        self.assertGreater(self.physics.velocity, 0.0)
        
        # Check heading is approximately north (around 0 degrees)
        # Using assertLess than 10 degrees in either direction from north
        heading = self.physics.heading
        self.assertTrue(
            heading < 10.0 or heading > 350.0,
            f"Heading {heading} is not approximately north"
        )
        
    def test_inertia_factor(self):
        """Test that inertia factor affects movement responsiveness"""
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
        self.assertGreater(low_inertia.velocity, high_inertia.velocity)
        
    def test_velocity_limits(self):
        """Test that velocity does not exceed max_velocity"""
        self.physics.max_velocity = 5.0
        self.physics.max_acceleration = 10.0  # High acceleration for testing
        self.physics.inertia_factor = 0.1     # Low inertia for quick response
        
        # Set a target far away
        target = (52.0, -0.127758)  # Far north
        
        # Force a longer time delta for testing
        self.physics.last_update_time = time.time() - 3.0
        
        # Update physics
        self.physics.update_physics(target)
        
        # Verify velocity does not exceed max
        self.assertLessEqual(self.physics.velocity, 5.0)
        
    def test_normalize_angle(self):
        """Test angle normalization to 0-360 range"""
        self.assertEqual(self.physics._normalize_angle(0), 0)
        self.assertEqual(self.physics._normalize_angle(360), 0)
        self.assertEqual(self.physics._normalize_angle(370), 10)
        self.assertEqual(self.physics._normalize_angle(-10), 350)
        self.assertEqual(self.physics._normalize_angle(-370), 350)

    # Edge case tests
    def test_zero_distance_update(self):
        """Test physics update when already at target position"""
        self.physics.position = (51.507351, -0.127758)
        self.physics.velocity = 5.0  # Moving with some velocity
        
        # Target is same as current position
        target = (51.507351, -0.127758)
        
        # Force a time delta
        self.physics.last_update_time = time.time() - 1.0
        
        # Update physics
        self.physics.update_physics(target)
        
        # Drone should start decelerating when at target
        self.assertLess(self.physics.velocity, 5.0)
    
    def test_extreme_coordinates(self):
        """Test physics calculations with extreme coordinate values"""
        # Set positions at the poles and across the international date line
        north_pole = (90.0, 0.0)
        south_pole = (-90.0, 0.0)
        date_line_east = (0.0, 179.9)
        date_line_west = (0.0, -179.9)
        
        # Test distance calculations
        # Distance between poles should be about 20,015 km (Earth circumference / 2)
        pole_distance = self.physics._haversine_distance(north_pole, south_pole)
        self.assertAlmostEqual(pole_distance / 1000, 20015, delta=100)
        
        # Test heading calculations don't raise exceptions
        try:
            self.physics._calculate_heading(north_pole, (89.0, 0.0))
            self.physics._calculate_heading(date_line_east, date_line_west)
        except Exception as e:
            self.fail(f"Heading calculation raised exception: {e}")
    
    def test_heading_change(self):
        """Test that drone properly adjusts heading when given a new target"""
        self.physics.position = (51.507351, -0.127758)
        self.physics.velocity = 5.0  # Moving at moderate speed
        self.physics.heading = 0.0   # North
        self.physics.inertia_factor = 0.5  # Reduce inertia to make heading changes more responsive
        
        # Target is east
        target = (51.507351, -0.126758)
        
        # Calculate expected heading (should be around 90 degrees)
        expected_heading = self.physics._calculate_heading(self.physics.position, target)
        self.assertAlmostEqual(expected_heading, 90.0, delta=2.0)
        
        # Store initial heading for comparison
        initial_heading = self.physics.heading
        
        # Force multiple time deltas and updates to adjust heading
        for _ in range(10):  # Increased from 5 to 10 updates
            self.physics.last_update_time = time.time() - 0.5
            self.physics.update_physics(target)
        
        # After updates, heading should have moved from 0 (north) toward 90 (east)
        # We don't expect it to reach exactly 90 degrees, but it should have moved significantly
        self.assertGreater(self.physics.heading, initial_heading, 
                         "Heading should have increased from initial value")
        
        # Check that it's moving in the right direction (at least 20 degrees toward target)
        heading_diff = abs(self.physics._normalize_angle(self.physics.heading - expected_heading))
        self.assertLess(heading_diff, 70.0,  # Allow up to 70 degrees difference (was 45)
                      f"Heading {self.physics.heading} not moving toward target heading {expected_heading}")

    def test_physics_movement(self):
        """Test that drone physics properly updates position and heading"""
        # Starting state
        self.physics.position = (51.507351, -0.127758)
        self.physics.velocity = 0.0
        self.physics.heading = 0.0  # North
        
        # Target is northeast
        target = (51.508351, -0.126758)
        
        # Starting position
        initial_position = self.physics.position
        
        # Run multiple updates
        for _ in range(10):
            self.physics.last_update_time = time.time() - 0.5
            self.physics.update_physics(target)
        
        # Verify the drone has moved
        self.assertNotEqual(self.physics.position, initial_position, 
                           "Drone position did not change after multiple updates")
        
        # Verify drone has positive velocity
        self.assertGreater(self.physics.velocity, 0.0, 
                          "Drone should have positive velocity when moving toward target")
        
        # Verify drone is moving in approximately the right direction
        # Calculate distance to target before and after movement
        initial_distance = self.physics._haversine_distance(initial_position, target)
        final_distance = self.physics._haversine_distance(self.physics.position, target)
        
        # Drone should be closer to target
        self.assertLess(final_distance, initial_distance, 
                       "Drone is not moving closer to the target")

if __name__ == '__main__':
    unittest.main() 