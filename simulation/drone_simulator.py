import time
import random
import json
import requests
from datetime import datetime

class DroneSimulator:
    def __init__(self, api_url="http://localhost:5000"):
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
        self.api_url = api_url
        self.flight_id = None
        
    def generate_sensor_reading(self, position):
        """Generate mock sensor data for the current position"""
        lat, lon = position
        
        # Generate realistic but random sensor values
        temperature = round(20 + random.uniform(-5, 5), 1)  # Around 20°C
        humidity = round(60 + random.uniform(-20, 20), 1)   # Around 60%
        air_quality_index = round(50 + random.uniform(-30, 100), 0)  # AQI (0-500)
        altitude = round(100 + random.uniform(-20, 20), 1)  # Around 100m
        
        # Create reading with timestamp and location
        reading = {
            "timestamp": datetime.now().isoformat(),
            "latitude": lat,
            "longitude": lon,
            "altitude": altitude,
            "temperature": temperature,
            "humidity": humidity,
            "air_quality_index": air_quality_index
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
        
        for i, waypoint in enumerate(self.waypoints):
            print(f"Moving to waypoint {i+1}/{len(self.waypoints)}: {waypoint}")
            
            # Generate sensor reading at this waypoint
            sensor_data = self.generate_sensor_reading(waypoint)
            flight_data.append(sensor_data)
            
            # Print sensor data
            print(f"Sensor readings: Temp: {sensor_data['temperature']}°C, " 
                  f"Humidity: {sensor_data['humidity']}%, " 
                  f"AQI: {sensor_data['air_quality_index']}")
            
            # Send data to API
            self.send_data_to_api(sensor_data)
            
            # Wait before moving to next waypoint (except for the last one)
            if i < len(self.waypoints) - 1:
                time.sleep(1)  # Simulate time between waypoints
        
        # End the flight
        self.end_flight()
        
        print("Simulation complete!")
        return flight_data

if __name__ == "__main__":
    # Create and run simulation
    simulator = DroneSimulator()
    flight_data = simulator.simulate_path()
    
    # Output the collected data as JSON
    print("\nFlight Data JSON:")
    print(json.dumps(flight_data, indent=2)) 