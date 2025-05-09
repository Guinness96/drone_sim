import os
import sys
from datetime import datetime, UTC
from flask import Flask, request, jsonify
from flask_cors import CORS

# Adjust import paths based on how the file is being run
if __name__ == "__main__":
    # When running as a script directly (python app.py)
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from models import db, Flight, DronePosition, SensorReading
    from config import Config
else:
    # When imported as a module (e.g., in tests)
    from backend.models import db, Flight, DronePosition, SensorReading
    from backend.config import Config

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)
db.init_app(app)

# Initialise database tables
with app.app_context():
    db.create_all()

@app.route('/')
def hello_world():
    return {'message': 'Drone Monitoring API is running.'}

# API Endpoint: Start a new flight
@app.route('/api/flights/start', methods=['POST'])
def start_flight():
    new_flight = Flight(start_time=datetime.now(UTC))
    db.session.add(new_flight)
    db.session.commit()
    return jsonify({'flight_id': new_flight.id, 'start_time': new_flight.start_time}), 201

# API Endpoint: Log drone position and sensor data
@app.route('/api/flights/<int:flight_id>/log_data', methods=['POST'])
def log_flight_data(flight_id):
    data = request.json
    
    # Find the flight
    flight = db.session.get(Flight, flight_id)
    if not flight:
        return jsonify({'error': 'Flight not found'}), 404
    
    # Create drone position
    position = DronePosition(
        flight_id=flight_id,
        timestamp=datetime.fromisoformat(data['timestamp']) if 'timestamp' in data else datetime.now(UTC),
        latitude=data['latitude'],
        longitude=data['longitude'],
        altitude=data['altitude']
    )
    
    db.session.add(position)
    db.session.flush()  # Get ID before commit
    
    # Create sensor reading
    # Check for anomalies - simple threshold-based detection
    is_anomaly = False
    if data['temperature'] > 30 or data['temperature'] < 0 or data['humidity'] > 90 or data['air_quality_index'] > 150:
        is_anomaly = True
        
    reading = SensorReading(
        drone_position_id=position.id,
        timestamp=datetime.fromisoformat(data['timestamp']) if 'timestamp' in data else datetime.now(UTC),
        temperature=data['temperature'],
        humidity=data['humidity'],
        air_quality_index=data['air_quality_index'],
        is_anomaly=is_anomaly
    )
    
    db.session.add(reading)
    db.session.commit()
    
    return jsonify({
        'position_id': position.id,
        'reading_id': reading.id,
        'is_anomaly': is_anomaly
    }), 201

# API Endpoint: End a flight
@app.route('/api/flights/<int:flight_id>/end', methods=['POST'])
def end_flight(flight_id):
    flight = db.session.get(Flight, flight_id)
    if not flight:
        return jsonify({'error': 'Flight not found'}), 404
    
    flight.end_time = datetime.now(UTC)
    db.session.commit()
    
    return jsonify({'flight_id': flight.id, 'end_time': flight.end_time}), 200

# API Endpoint: Get all flights
@app.route('/api/flights', methods=['GET'])
def get_all_flights():
    flights = Flight.query.all()
    flights_data = [
        {
            'id': flight.id,
            'start_time': flight.start_time,
            'end_time': flight.end_time
        } for flight in flights
    ]
    
    return jsonify(flights_data), 200

# API Endpoint: Get flight data
@app.route('/api/flights/<int:flight_id>/data', methods=['GET'])
def get_flight_data(flight_id):
    flight = db.session.get(Flight, flight_id)
    if not flight:
        return jsonify({'error': 'Flight not found'}), 404
    
    positions = DronePosition.query.filter_by(flight_id=flight_id).all()
    positions_data = []
    
    for position in positions:
        readings = SensorReading.query.filter_by(drone_position_id=position.id).all()
        
        readings_data = [
            {
                'id': reading.id,
                'timestamp': reading.timestamp,
                'temperature': reading.temperature,
                'humidity': reading.humidity,
                'air_quality_index': reading.air_quality_index,
                'is_anomaly': reading.is_anomaly
            } for reading in readings
        ]
        
        positions_data.append({
            'id': position.id,
            'timestamp': position.timestamp,
            'latitude': position.latitude,
            'longitude': position.longitude,
            'altitude': position.altitude,
            'sensor_readings': readings_data
        })
    
    flight_data = {
        'id': flight.id,
        'start_time': flight.start_time,
        'end_time': flight.end_time,
        'positions': positions_data
    }
    
    return jsonify(flight_data), 200

# API Endpoint: Get latest sensor readings
@app.route('/api/sensor_readings/latest', methods=['GET'])
def get_latest_sensor_readings():
    limit = request.args.get('limit', 10, type=int)
    
    readings = SensorReading.query.join(DronePosition).order_by(SensorReading.timestamp.desc()).limit(limit).all()
    readings_data = []
    
    for reading in readings:
        position = reading.position
        readings_data.append({
            'id': reading.id,
            'timestamp': reading.timestamp,
            'position': {
                'latitude': position.latitude,
                'longitude': position.longitude,
                'altitude': position.altitude
            },
            'temperature': reading.temperature,
            'humidity': reading.humidity,
            'air_quality_index': reading.air_quality_index,
            'is_anomaly': reading.is_anomaly
        })
    
    return jsonify(readings_data), 200

if __name__ == '__main__':
    app.run(debug=True) 