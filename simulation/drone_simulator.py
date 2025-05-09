import time
import random
import json
import requests
import os
import sys
from datetime import datetime
from simulation.drone_physics import DronePhysics
import argparse

class DroneSimulator:
    def __init__(self, api_url="http://localhost:5000", config=None):
        # Default configuration
        self.config = {
            "simulation_speed": 1.0,  # Speed multiplier (1.0 = normal, 2.0 = 2x speed, etc.)
            "waypoint_file": None,    # Path to a JSON file with waypoints, if None use default
            "sensor_noise_levels": {
                "temperature": 5.0,   # Temperature noise level in °C (+/-)
                "humidity": 20.0,     # Humidity noise level in % (+/-)
                "air_quality": 50.0,  # AQI noise level (+/-)
                "altitude": 20.0      # Altitude noise level in meters (+/-)
            },
            "physics": {
                "max_velocity": 10.0,      # m/s - maximum drone speed
                "max_acceleration": 2.0,   # m/s² - maximum acceleration
                "inertia_factor": 0.8,     # 0-1, higher means more resistance to change
                "enable_physics": True     # Whether to use physics simulation
            }
        }
        
        # Override defaults with any provided configuration
        if config:
            # Deep update for nested dictionaries
            self._deep_update(self.config, config)
        
        # Load waypoints from file if specified
        if self.config["waypoint_file"] and os.path.exists(self.config["waypoint_file"]):
            try:
                with open(self.config["waypoint_file"], 'r') as f:
                    self.waypoints = json.load(f)
                print(f"Loaded {len(self.waypoints)} waypoints from {self.config['waypoint_file']}")
            except Exception as e:
                print(f"Error loading waypoints from file: {e}")
                self._set_default_waypoints()
        else:
            self._set_default_waypoints()
            
        self.api_url = api_url
        self.flight_id = None
        
        # Initialize physics engine
        self.physics = DronePhysics()
        
        # Apply physics configuration
        if "physics" in self.config:
            if "max_velocity" in self.config["physics"]:
                self.physics.max_velocity = self.config["physics"]["max_velocity"]
            if "max_acceleration" in self.config["physics"]:
                self.physics.max_acceleration = self.config["physics"]["max_acceleration"]
            if "inertia_factor" in self.config["physics"]:
                self.physics.inertia_factor = self.config["physics"]["inertia_factor"]
    
    def _deep_update(self, d, u):
        """Deep update dictionary d with values from dictionary u"""
        for k, v in u.items():
            if isinstance(v, dict) and k in d and isinstance(d[k], dict):
                self._deep_update(d[k], v)
            else:
                d[k] = v
    
    def _set_default_waypoints(self):
        """Set default waypoints if not loaded from file"""
        # Default waypoints (example: flying around a park area)
        self.waypoints = [
            (51.507351, -0.127758),  # London coordinates (for example)
            (51.507951, -0.127158),
            (51.508351, -0.126758),
            (51.508751, -0.127358),
            (51.508351, -0.127958),
            (51.507751, -0.128358),
            (51.507351, -0.127758),  # Return to start
        ]
        
    def generate_sensor_reading(self, position, altitude=None):
        """Generate mock sensor data for the current position"""
        lat, lon = position
        
        # Use noise levels from config
        temp_noise = self.config["sensor_noise_levels"]["temperature"]
        humidity_noise = self.config["sensor_noise_levels"]["humidity"]
        aqi_noise = self.config["sensor_noise_levels"]["air_quality"]
        alt_noise = self.config["sensor_noise_levels"]["altitude"]
        
        # Use altitude from physics if not provided
        if altitude is None:
            altitude = self.physics.altitude
            
        # Add noise to altitude
        altitude = round(altitude + random.uniform(-alt_noise, alt_noise), 1)
        
        # Generate realistic but random sensor values
        temperature = round(20 + random.uniform(-temp_noise, temp_noise), 1)  # Around 20°C
        humidity = round(60 + random.uniform(-humidity_noise, humidity_noise), 1)   # Around 60%
        air_quality_index = round(50 + random.uniform(-aqi_noise/2, aqi_noise), 0)  # AQI (0-500)
        
        # Get additional telemetry data from physics
        telemetry = self.physics.get_telemetry()
        
        # Create reading with timestamp and location
        reading = {
            "timestamp": datetime.now().isoformat(),
            "latitude": lat,
            "longitude": lon,
            "altitude": altitude,
            "temperature": temperature,
            "humidity": humidity,
            "air_quality_index": air_quality_index,
            "velocity": telemetry["velocity"],
            "heading": telemetry["heading"],
            "acceleration": telemetry["acceleration"]
        }
        
        return reading
    
    def start_flight(self):
        """Start a new flight in the API"""
        try:
            response = requests.post(f"{self.api_url}/api/flights/start")
            if response.status_code == 201:
                self.flight_id = response.json()['flight_id']
                print(f"Started new flight with ID: {self.flight_id}")
                return self.flight_id
            else:
                print(f"Error starting flight: {response.text}")
                return None
        except requests.RequestException as e:
            print(f"Error connecting to API: {e}")
            return None
            
    def end_flight(self):
        """End the current flight in the API"""
        if not self.flight_id:
            print("No active flight to end")
            return False
            
        try:
            response = requests.post(f"{self.api_url}/api/flights/{self.flight_id}/end")
            if response.status_code == 200:
                print(f"Ended flight {self.flight_id}")
                return True
            else:
                print(f"Error ending flight: {response.text}")
                return False
        except requests.RequestException as e:
            print(f"Error connecting to API: {e}")
            return False
    
    def send_data_to_api(self, data):
        """Send sensor data to the API"""
        if not self.flight_id:
            print("No active flight ID. Data not sent.")
            return False
            
        try:
            response = requests.post(
                f"{self.api_url}/api/flights/{self.flight_id}/log_data", 
                json=data
            )
            
            if response.status_code == 201:
                result = response.json()
                anomaly_status = "ANOMALY DETECTED!" if result.get('is_anomaly', False) else "normal"
                print(f"Data sent successfully. Status: {anomaly_status}")
                return True
            else:
                print(f"Error sending data: {response.text}")
                return False
        except requests.RequestException as e:
            print(f"Error connecting to API: {e}")
            return False
    
    def simulate_path(self):
        """Simulate drone flight along waypoints, collecting and sending sensor data"""
        flight_data = []
        
        # Start a new flight
        if not self.start_flight():
            print("Could not start flight. Simulation aborted.")
            return flight_data
        
        print("Starting drone simulation...")
        print(f"Simulation speed: {self.config['simulation_speed']}x")
        print(f"Physics simulation: {'Enabled' if self.config['physics']['enable_physics'] else 'Disabled'}")
        
        # Set initial drone position to first waypoint
        if self.waypoints:
            self.physics.set_position(self.waypoints[0])
            
        # Start with first waypoint
        current_waypoint_idx = 0
        
        # Define waypoint arrival threshold in meters
        waypoint_threshold = 10.0
        
        # Main simulation loop
        simulation_running = True
        while simulation_running and current_waypoint_idx < len(self.waypoints):
            # Get current target waypoint
            target_waypoint = self.waypoints[current_waypoint_idx]
            
            # Update physics with current target
            use_physics = self.config["physics"]["enable_physics"]
            
            if use_physics:
                # Update drone position using physics engine
                current_position = self.physics.update_physics(target_waypoint)
                
                # Check if we've reached the waypoint
                distance = self.physics._haversine_distance(current_position, target_waypoint)
                if distance < waypoint_threshold:
                    print(f"Reached waypoint {current_waypoint_idx+1}/{len(self.waypoints)}")
                    current_waypoint_idx += 1
            else:
                # Simple waypoint movement without physics
                current_position = target_waypoint
                print(f"Moving to waypoint {current_waypoint_idx+1}/{len(self.waypoints)}: {target_waypoint}")
                current_waypoint_idx += 1
            
            # Generate sensor reading at current position
            sensor_data = self.generate_sensor_reading(current_position)
            flight_data.append(sensor_data)
            
            # Print sensor data
            print(f"Sensor readings: Temp: {sensor_data['temperature']}°C, " 
                  f"Humidity: {sensor_data['humidity']}%, " 
                  f"AQI: {sensor_data['air_quality_index']}, "
                  f"Velocity: {sensor_data['velocity']:.1f} m/s")
            
            # Send data to API
            self.send_data_to_api(sensor_data)
            
            # Wait based on simulation speed
            wait_time = 1.0 / self.config["simulation_speed"]
            time.sleep(wait_time)
            
            # Break at end of waypoints
            if current_waypoint_idx >= len(self.waypoints):
                simulation_running = False
        
        # End the flight
        self.end_flight()
        
        print("Simulation complete!")
        return flight_data

def load_config_from_file(file_path):
    """Load configuration from a JSON file"""
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                return json.load(f)
        else:
            print(f"Config file not found: {file_path}")
            return None
    except Exception as e:
        print(f"Error loading config file: {e}")
        return None

if __name__ == "__main__":
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(description='Drone Simulator with Physics Engine')
    parser.add_argument('--config', type=str, help='Path to a JSON configuration file')
    parser.add_argument('--speed', type=float, help='Simulation speed multiplier (e.g., 2.0 for 2x speed)')
    parser.add_argument('--api-url', type=str, default='http://localhost:5000', help='URL of the backend API')
    args = parser.parse_args()
    
    # Load configuration
    config = None
    if args.config:
        config = load_config_from_file(args.config)
        print(f"Using configuration from: {args.config}")
    else:
        # Example configuration
        config = {
            "simulation_speed": 2.0,  # Run at 2x speed
            "waypoint_file": None,    # Use default waypoints
            "sensor_noise_levels": {
                "temperature": 3.0,   # Lower temperature variability
                "humidity": 15.0,     # Lower humidity variability
                "air_quality": 80.0,  # Higher AQI variability
                "altitude": 10.0      # Lower altitude variability
            },
            "physics": {
                "max_velocity": 8.0,      # Maximum velocity in m/s
                "max_acceleration": 2.5,   # Maximum acceleration in m/s²
                "inertia_factor": 0.7,     # Lower value = more responsive drone
                "enable_physics": True     # Enable physics simulation
            }
        }
        print("Using default configuration")
    
    # Override simulation speed if provided via command line
    if args.speed and config:
        config["simulation_speed"] = args.speed
        print(f"Overriding simulation speed to: {args.speed}x")
    
    # Create and run simulation with config
    simulator = DroneSimulator(api_url=args.api_url, config=config)
    flight_data = simulator.simulate_path()
    
    # Output the collected data as JSON
    print("\nFlight Data JSON:")
    print(json.dumps(flight_data, indent=2)) 