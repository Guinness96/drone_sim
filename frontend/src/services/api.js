/**
 * API service for communicating with the backend
 */
import axios from 'axios';

const API_URL = 'http://localhost:5000';

// Create an axios instance with default config
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Starts a new drone flight
 * @returns {Promise<Object>} Flight data with id and start time
 */
export const startNewFlight = async () => {
  try {
    const response = await api.post('/api/flights/start');
    return response.data;
  } catch (error) {
    console.error('Error starting flight:', error);
    throw error;
  }
};

/**
 * Ends an active flight
 * @param {number} flightId - The ID of the flight to end
 * @returns {Promise<Object>} Flight data with id and end time
 */
export const endFlight = async (flightId) => {
  try {
    const response = await api.post(`/api/flights/${flightId}/end`);
    return response.data;
  } catch (error) {
    console.error('Error ending flight:', error);
    throw error;
  }
};

/**
 * Logs drone position and sensor data for a flight
 * @param {number} flightId - The ID of the flight
 * @param {Object} data - The sensor and position data
 * @returns {Promise<Object>} Response with position_id, reading_id, and is_anomaly
 */
export const logFlightData = async (flightId, data) => {
  try {
    const response = await api.post(`/api/flights/${flightId}/log_data`, data);
    return response.data;
  } catch (error) {
    console.error('Error logging flight data:', error);
    throw error;
  }
};

/**
 * Retrieves a list of all flights
 * @returns {Promise<Array>} List of flights
 */
export const getAllFlights = async () => {
  try {
    const response = await api.get('/api/flights');
    return response.data;
  } catch (error) {
    console.error('Error getting flights:', error);
    throw error;
  }
};

/**
 * Retrieves data for a specific flight
 * @param {number} flightId - The ID of the flight
 * @returns {Promise<Object>} Complete flight data with positions and sensor readings
 */
export const getFlightData = async (flightId) => {
  try {
    const response = await api.get(`/api/flights/${flightId}/data`);
    return response.data;
  } catch (error) {
    console.error('Error getting flight data:', error);
    throw error;
  }
};

/**
 * Retrieves the latest sensor readings
 * @param {number} limit - Maximum number of readings to return
 * @returns {Promise<Array>} List of sensor readings with position data
 */
export const getLatestSensorReadings = async (limit = 10) => {
  try {
    const response = await api.get(`/api/sensor_readings/latest`, {
      params: { limit }
    });
    return response.data;
  } catch (error) {
    console.error('Error getting latest sensor readings:', error);
    throw error;
  }
}; 