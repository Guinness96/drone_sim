import math
import time

class DronePhysics:
    """
    Handles drone movement physics calculations including:
    - Velocity (speed and direction)
    - Acceleration (rate of velocity change)
    - Inertia (resistance to changes in velocity/direction)
    """
    def __init__(self):
        # Current drone state
        self.position = (0.0, 0.0)  # (latitude, longitude)
        self.altitude = 100.0  # meters
        self.velocity = 0.0  # meters per second
        self.heading = 0.0  # degrees (0 = North, 90 = East)
        self.acceleration = 0.0  # meters per second^2
        
        # Drone movement physics parameters
        self.max_velocity = 10.0  # m/s - maximum drone speed
        self.max_acceleration = 2.0  # m/s² - maximum acceleration
        self.max_deceleration = 3.0  # m/s² - maximum braking deceleration
        self.inertia_factor = 0.8  # 0-1, higher means more resistance to change
        self.turn_rate = 45.0  # maximum degrees per second the drone can turn
        
        # Earth radius (meters) for coordinate calculations
        self.earth_radius = 6371000
        
        # Timing for physics calculations
        self.last_update_time = time.time()
        
    def update_physics(self, target_position=None):
        """
        Update drone position, velocity, etc. based on physics.
        
        Args:
            target_position: (latitude, longitude) tuple if moving toward a waypoint
            
        Returns:
            current_position: (latitude, longitude) tuple
        """
        # Calculate time delta
        current_time = time.time()
        delta_t = current_time - self.last_update_time
        self.last_update_time = current_time
        
        # If no target, maintain current state
        if target_position is None:
            return self.position
            
        # Calculate heading to target
        target_heading = self._calculate_heading(self.position, target_position)
        distance = self._haversine_distance(self.position, target_position)
        
        # Update heading based on turn rate and inertia
        heading_diff = self._normalize_angle(target_heading - self.heading)
        max_turn = self.turn_rate * delta_t
        actual_turn = heading_diff * (1.0 - self.inertia_factor)
        
        # Limit turn based on maximum turn rate
        if abs(actual_turn) > max_turn:
            actual_turn = max_turn if actual_turn > 0 else -max_turn
            
        # Update heading
        self.heading = self._normalize_angle(self.heading + actual_turn)
        
        # Update acceleration based on distance to target
        target_velocity = self.max_velocity
        
        # If close to target, begin decelerating
        braking_distance = (self.velocity * self.velocity) / (2 * self.max_deceleration)
        if distance < braking_distance:
            target_velocity = self.velocity * (distance / braking_distance)
        
        # Apply acceleration with inertia factor
        velocity_diff = target_velocity - self.velocity
        max_accel_change = self.max_acceleration * delta_t
        actual_accel = velocity_diff * (1.0 - self.inertia_factor)
        
        # Limit acceleration change
        if abs(actual_accel) > max_accel_change:
            actual_accel = max_accel_change if actual_accel > 0 else -max_accel_change
            
        # Update velocity
        self.velocity += actual_accel
        self.velocity = max(0.0, min(self.velocity, self.max_velocity))
        
        # Calculate new position
        if self.velocity > 0:
            distance_moved = self.velocity * delta_t
            new_position = self._calculate_new_position(distance_moved)
            self.position = new_position
        
        return self.position
        
    def _calculate_heading(self, start_pos, end_pos):
        """Calculate heading in degrees from start to end point"""
        lat1, lon1 = math.radians(start_pos[0]), math.radians(start_pos[1])
        lat2, lon2 = math.radians(end_pos[0]), math.radians(end_pos[1])
        
        dlon = lon2 - lon1
        y = math.sin(dlon) * math.cos(lat2)
        x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
        
        heading = math.atan2(y, x)
        heading = math.degrees(heading)
        heading = (heading + 360) % 360  # Normalize to 0-360
        
        return heading
        
    def _haversine_distance(self, point1, point2):
        """Calculate distance between two coordinates in meters"""
        lat1, lon1 = math.radians(point1[0]), math.radians(point1[1])
        lat2, lon2 = math.radians(point2[0]), math.radians(point2[1])
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return self.earth_radius * c
        
    def _calculate_new_position(self, distance):
        """Calculate new position given distance and heading"""
        lat, lon = self.position
        lat_rad = math.radians(lat)
        lon_rad = math.radians(lon)
        heading_rad = math.radians(self.heading)
        
        # Convert distance to angular distance in radians
        angular_distance = distance / self.earth_radius
        
        # Calculate new latitude
        new_lat_rad = math.asin(math.sin(lat_rad) * math.cos(angular_distance) + 
                               math.cos(lat_rad) * math.sin(angular_distance) * math.cos(heading_rad))
        
        # Calculate new longitude
        new_lon_rad = lon_rad + math.atan2(math.sin(heading_rad) * math.sin(angular_distance) * math.cos(lat_rad),
                                          math.cos(angular_distance) - math.sin(lat_rad) * math.sin(new_lat_rad))
        
        # Convert back to degrees
        new_lat = math.degrees(new_lat_rad)
        new_lon = math.degrees(new_lon_rad)
        
        return (new_lat, new_lon)
        
    def _normalize_angle(self, angle):
        """Normalize angle to be between 0-360 degrees"""
        return (angle + 360) % 360
        
    def set_position(self, position, altitude=None):
        """Set the drone's current position"""
        self.position = position
        if altitude is not None:
            self.altitude = altitude
            
    def get_telemetry(self):
        """Get current drone telemetry data"""
        return {
            "position": self.position,
            "altitude": self.altitude,
            "velocity": self.velocity,
            "heading": self.heading,
            "acceleration": self.acceleration
        } 