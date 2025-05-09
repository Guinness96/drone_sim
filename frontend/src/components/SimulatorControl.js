import React, { useState } from 'react';
import axios from 'axios';

/**
 * Component for controlling drone simulator parameters
 */
const SimulatorControl = () => {
  const [config, setConfig] = useState({
    simulation_speed: 1.0,
    sensor_noise_levels: {
      temperature: 5.0,
      humidity: 20.0,
      air_quality: 50.0,
      altitude: 20.0
    }
  });
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState(null);

  const handleSpeedChange = (e) => {
    setConfig({
      ...config,
      simulation_speed: parseFloat(e.target.value)
    });
  };

  const handleNoiseChange = (sensor, value) => {
    setConfig({
      ...config,
      sensor_noise_levels: {
        ...config.sensor_noise_levels,
        [sensor]: parseFloat(value)
      }
    });
  };

  const startSimulation = async () => {
    try {
      setLoading(true);
      setStatus('Starting simulation...');
      
      // Make API call to start simulation with the specified config
      await axios.post('http://localhost:5000/api/simulation/start', { config });
      
      setStatus('Simulation started successfully.');
    } catch (error) {
      console.error('Error starting simulation:', error);
      setStatus('Error starting simulation. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="simulator-control">
      <h2>Drone Simulator Control</h2>
      
      <div className="control-section">
        <h3>Simulation Speed</h3>
        <div className="slider-container">
          <input
            type="range"
            min="0.1"
            max="5"
            step="0.1"
            value={config.simulation_speed}
            onChange={handleSpeedChange}
            disabled={loading}
          />
          <span className="slider-value">{config.simulation_speed.toFixed(1)}x</span>
        </div>
      </div>
      
      <div className="control-section">
        <h3>Sensor Noise Levels</h3>
        
        <div className="noise-control">
          <label>Temperature (°C):</label>
          <div className="slider-container">
            <input
              type="range"
              min="0.1"
              max="20"
              step="0.1"
              value={config.sensor_noise_levels.temperature}
              onChange={(e) => handleNoiseChange('temperature', e.target.value)}
              disabled={loading}
            />
            <span className="slider-value">±{config.sensor_noise_levels.temperature.toFixed(1)}°C</span>
          </div>
        </div>
        
        <div className="noise-control">
          <label>Humidity (%):</label>
          <div className="slider-container">
            <input
              type="range"
              min="1"
              max="50"
              step="1"
              value={config.sensor_noise_levels.humidity}
              onChange={(e) => handleNoiseChange('humidity', e.target.value)}
              disabled={loading}
            />
            <span className="slider-value">±{config.sensor_noise_levels.humidity.toFixed(0)}%</span>
          </div>
        </div>
        
        <div className="noise-control">
          <label>Air Quality Index:</label>
          <div className="slider-container">
            <input
              type="range"
              min="1"
              max="100"
              step="1"
              value={config.sensor_noise_levels.air_quality}
              onChange={(e) => handleNoiseChange('air_quality', e.target.value)}
              disabled={loading}
            />
            <span className="slider-value">±{config.sensor_noise_levels.air_quality.toFixed(0)} AQI</span>
          </div>
        </div>
        
        <div className="noise-control">
          <label>Altitude (m):</label>
          <div className="slider-container">
            <input
              type="range"
              min="1"
              max="50"
              step="1"
              value={config.sensor_noise_levels.altitude}
              onChange={(e) => handleNoiseChange('altitude', e.target.value)}
              disabled={loading}
            />
            <span className="slider-value">±{config.sensor_noise_levels.altitude.toFixed(0)}m</span>
          </div>
        </div>
      </div>
      
      <div className="control-actions">
        <button 
          className="start-button"
          onClick={startSimulation}
          disabled={loading}
        >
          {loading ? 'Starting...' : 'Start Simulation'}
        </button>
        
        {status && <div className="status-message">{status}</div>}
      </div>
    </div>
  );
};

export default SimulatorControl; 