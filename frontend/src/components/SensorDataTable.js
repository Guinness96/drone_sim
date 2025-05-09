import React, { useState, useEffect } from 'react';
import { getLatestSensorReadings, getFlightData } from '../services/api';

/**
 * Component to display sensor readings in a tabular format
 * @param {Object} props - Component props
 * @param {number|null} props.selectedFlightId - Currently selected flight ID
 */
const SensorDataTable = ({ selectedFlightId }) => {
  const [sensorData, setSensorData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchSensorData = async () => {
      try {
        setLoading(true);
        let data;

        if (selectedFlightId) {
          // Fetch data for specific flight
          const flightData = await getFlightData(selectedFlightId);
          // Extract the sensor readings with position data
          data = flightData.positions.map(position => ({
            ...position.sensor_reading,
            latitude: position.latitude,
            longitude: position.longitude,
            altitude: position.altitude,
            timestamp: position.timestamp,
            is_anomaly: position.sensor_reading.is_anomaly
          }));
        } else {
          // Fetch latest readings
          const readings = await getLatestSensorReadings(20);
          
          // Map the API response structure to our component's expected format
          data = readings.map(reading => ({
            ...reading,
            // Extract position fields if they exist in a nested object
            latitude: reading.position ? reading.position.latitude : reading.latitude,
            longitude: reading.position ? reading.position.longitude : reading.longitude,
            altitude: reading.position ? reading.position.altitude : reading.altitude,
          }));
        }

        setSensorData(data);
        setError(null);
      } catch (err) {
        setError('Failed to load sensor data. Please try again later.');
        console.error('Error fetching sensor data:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchSensorData();
  }, [selectedFlightId]);

  // Format timestamp for display
  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleString('en-GB');
  };

  // Safely format coordinates with toFixed
  const formatCoordinate = (value, decimals = 6) => {
    return value !== undefined && value !== null 
      ? value.toFixed(decimals)
      : 'N/A';
  };

  if (loading) return <div data-testid="loading-sensor-data">Loading sensor data...</div>;
  if (error) return <div className="error" data-testid="sensor-data-error">{error}</div>;
  if (sensorData.length === 0) return <div data-testid="no-sensor-data">No sensor data available.</div>;

  return (
    <div className="sensor-data-table" data-testid="sensor-data-table">
      <h2 data-testid="sensor-data-title">
        {selectedFlightId 
          ? `Sensor Readings - Flight #${selectedFlightId}` 
          : 'Latest Sensor Readings'}
      </h2>
      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th>Time</th>
              <th>Location</th>
              <th>Temperature (°C)</th>
              <th>Humidity (%)</th>
              <th>Air Quality</th>
            </tr>
          </thead>
          <tbody>
            {sensorData.map((reading, index) => (
              <tr 
                key={index} 
                className={reading.is_anomaly ? 'anomaly' : ''}
                data-testid={`sensor-row-${index}`}
                data-is-anomaly={reading.is_anomaly ? 'true' : 'false'}
              >
                <td>{reading.timestamp ? formatTimestamp(reading.timestamp) : 'N/A'}</td>
                <td>
                  {formatCoordinate(reading.latitude)}, {formatCoordinate(reading.longitude)}
                  {reading.altitude !== undefined && reading.altitude !== null 
                    ? `, Alt: ${formatCoordinate(reading.altitude, 1)}m` 
                    : ''}
                </td>
                <td data-testid={`temperature-${index}`}>
                  {reading.temperature !== undefined ? `${reading.temperature}°C` : 'N/A'}
                </td>
                <td>
                  {reading.humidity !== undefined ? `${reading.humidity}%` : 'N/A'}
                </td>
                <td>
                  {reading.air_quality_index !== undefined ? `${reading.air_quality_index} AQI` : 'N/A'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default SensorDataTable; 