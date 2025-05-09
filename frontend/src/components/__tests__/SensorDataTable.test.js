import React from 'react';
import { render, screen } from '@testing-library/react';
import SensorDataTable from '../SensorDataTable';
import { getLatestSensorReadings, getFlightData } from '../../services/api';

// Mock the API module
jest.mock('../../services/api');

describe('SensorDataTable Component', () => {
  // Sample sensor data for tests - updated to match actual API format
  const mockLatestReadings = [
    {
      id: 1,
      timestamp: '2023-10-25T09:10:00',
      temperature: 22.5,
      humidity: 65,
      air_quality_index: 45,
      position: {
        latitude: 51.507351,
        longitude: -0.127758,
        altitude: 120
      },
      is_anomaly: false
    },
    {
      id: 2,
      timestamp: '2023-10-25T09:15:00',
      temperature: 38.2,
      humidity: 80,
      air_quality_index: 180,
      position: {
        latitude: 51.507900,
        longitude: -0.128000,
        altitude: 125
      },
      is_anomaly: true
    }
  ];

  const mockFlightData = {
    id: 1,
    start_time: '2023-10-25T09:00:00',
    end_time: '2023-10-25T09:30:00',
    positions: [
      {
        id: 1,
        timestamp: '2023-10-25T09:10:00',
        latitude: 51.507351,
        longitude: -0.127758,
        altitude: 120,
        sensor_reading: {
          id: 1,
          temperature: 22.5,
          humidity: 65,
          air_quality_index: 45,
          is_anomaly: false
        }
      },
      {
        id: 2,
        timestamp: '2023-10-25T09:15:00',
        latitude: 51.507900,
        longitude: -0.128000,
        altitude: 125,
        sensor_reading: {
          id: 2,
          temperature: 38.2,
          humidity: 80,
          air_quality_index: 180,
          is_anomaly: true
        }
      }
    ]
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('displays loading state initially', () => {
    getLatestSensorReadings.mockResolvedValueOnce([]);
    render(<SensorDataTable selectedFlightId={null} />);
    
    expect(screen.getByTestId('loading-sensor-data')).toBeInTheDocument();
  });

  test('displays latest sensor readings when no flight is selected', async () => {
    getLatestSensorReadings.mockResolvedValueOnce(mockLatestReadings);
    render(<SensorDataTable selectedFlightId={null} />);
    
    // Wait for the component to finish loading
    await screen.findByTestId('sensor-data-table');
    
    // Check that the title is correct
    expect(screen.getByTestId('sensor-data-title')).toHaveTextContent('Latest Sensor Readings');
    
    // Check that temperature values are displayed
    expect(screen.getByTestId('temperature-0')).toHaveTextContent('22.5°C');
    expect(screen.getByTestId('temperature-1')).toHaveTextContent('38.2°C');
    
    // Check that the API was called correctly
    expect(getLatestSensorReadings).toHaveBeenCalledWith(20);
  });

  test('displays flight sensor data when a flight is selected', async () => {
    getFlightData.mockResolvedValueOnce(mockFlightData);
    render(<SensorDataTable selectedFlightId={1} />);
    
    // Wait for the component to finish loading
    await screen.findByTestId('sensor-data-table');
    
    // Check that the title is correct
    expect(screen.getByTestId('sensor-data-title')).toHaveTextContent('Sensor Readings - Flight #1');
    
    // Check that temperature values are displayed
    expect(screen.getByTestId('temperature-0')).toHaveTextContent('22.5°C');
    expect(screen.getByTestId('temperature-1')).toHaveTextContent('38.2°C');
    
    // Check that the API was called correctly
    expect(getFlightData).toHaveBeenCalledWith(1);
  });

  test('shows empty state when no sensor data is available', async () => {
    getLatestSensorReadings.mockResolvedValueOnce([]);
    render(<SensorDataTable selectedFlightId={null} />);
    
    await screen.findByTestId('no-sensor-data');
    expect(screen.getByTestId('no-sensor-data')).toHaveTextContent('No sensor data available.');
  });

  test('shows error message when API call fails', async () => {
    getLatestSensorReadings.mockRejectedValueOnce(new Error('API Error'));
    render(<SensorDataTable selectedFlightId={null} />);
    
    await screen.findByTestId('sensor-data-error');
    expect(screen.getByTestId('sensor-data-error')).toHaveTextContent('Failed to load sensor data. Please try again later.');
  });

  test('applies anomaly class to rows with anomalies', async () => {
    getLatestSensorReadings.mockResolvedValueOnce(mockLatestReadings);
    render(<SensorDataTable selectedFlightId={null} />);
    
    // Wait for the component to finish loading
    await screen.findByTestId('sensor-data-table');
    
    // Check anomaly status using data attributes
    const row0 = screen.getByTestId('sensor-row-0');
    const row1 = screen.getByTestId('sensor-row-1');
    
    // The second row should have the anomaly class (index 1)
    expect(row1).toHaveClass('anomaly');
    expect(row1).toHaveAttribute('data-is-anomaly', 'true');
    
    // The first row should not have the anomaly class (index 0)
    expect(row0).not.toHaveClass('anomaly');
    expect(row0).toHaveAttribute('data-is-anomaly', 'false');
  });
}); 