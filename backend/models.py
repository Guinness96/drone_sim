from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Flight(db.Model):
    __tablename__ = 'flights'
    
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)
    
    # Relationships
    positions = db.relationship('DronePosition', backref='flight', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<Flight {self.id} - {self.start_time}>'

class DronePosition(db.Model):
    __tablename__ = 'drone_positions'
    
    id = db.Column(db.Integer, primary_key=True)
    flight_id = db.Column(db.Integer, db.ForeignKey('flights.id'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    altitude = db.Column(db.Float, nullable=False)
    
    # Relationships
    sensor_readings = db.relationship('SensorReading', backref='position', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<DronePosition {self.id} - Flight {self.flight_id} - {self.timestamp}>'

class SensorReading(db.Model):
    __tablename__ = 'sensor_readings'
    
    id = db.Column(db.Integer, primary_key=True)
    drone_position_id = db.Column(db.Integer, db.ForeignKey('drone_positions.id'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    temperature = db.Column(db.Float, nullable=False)  # in degrees Celsius
    humidity = db.Column(db.Float, nullable=False)     # in %
    air_quality_index = db.Column(db.Float, nullable=False)  # AQI value
    is_anomaly = db.Column(db.Boolean, default=False)  # Flag for anomalous readings
    
    def __repr__(self):
        return f'<SensorReading {self.id} - Position {self.drone_position_id} - {self.timestamp}>' 