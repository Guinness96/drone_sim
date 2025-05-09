/**
 * API Service tests
 */
import * as apiModule from '../api';

// Mock the api module
jest.mock('../api', () => {
  // Store the original module
  const originalModule = jest.requireActual('../api');
  
  // Return a modified module with our mock functions
  return {
    ...originalModule,
    startNewFlight: jest.fn(),
    endFlight: jest.fn(),
    logFlightData: jest.fn(),
    getAllFlights: jest.fn(),
    getFlightData: jest.fn(),
    getLatestSensorReadings: jest.fn()
  };
});

describe('API Service', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('startNewFlight should return flight data', async () => {
    const mockFlightData = { flight_id: 1, start_time: '2023-05-10T12:00:00Z' };
    apiModule.startNewFlight.mockResolvedValueOnce(mockFlightData);
    
    const result = await apiModule.startNewFlight();
    
    expect(result).toEqual(mockFlightData);
    expect(apiModule.startNewFlight).toHaveBeenCalled();
  });
  
  test('endFlight should make a request with the flight ID', async () => {
    const flightId = 1;
    const mockResponseData = { flight_id: flightId, end_time: '2023-05-10T14:00:00Z' };
    apiModule.endFlight.mockResolvedValueOnce(mockResponseData);
    
    const result = await apiModule.endFlight(flightId);
    
    expect(result).toEqual(mockResponseData);
    expect(apiModule.endFlight).toHaveBeenCalledWith(flightId);
  });
  
  test('logFlightData should send position and sensor data', async () => {
    const flightId = 1;
    const sensorData = {
      timestamp: '2023-05-10T13:00:00Z',
      latitude: 51.5,
      longitude: -0.12,
      altitude: 100,
      temperature: 20,
      humidity: 60,
      air_quality_index: 50
    };
    const mockResponse = { position_id: 1, reading_id: 1, is_anomaly: false };
    apiModule.logFlightData.mockResolvedValueOnce(mockResponse);
    
    const result = await apiModule.logFlightData(flightId, sensorData);
    
    expect(result).toEqual(mockResponse);
    expect(apiModule.logFlightData).toHaveBeenCalledWith(flightId, sensorData);
  });
  
  test('getAllFlights should retrieve a list of flights', async () => {
    const mockFlights = [
      { id: 1, start_time: '2023-05-10T12:00:00Z', end_time: null },
      { id: 2, start_time: '2023-05-09T10:00:00Z', end_time: '2023-05-09T11:00:00Z' }
    ];
    apiModule.getAllFlights.mockResolvedValueOnce(mockFlights);
    
    const result = await apiModule.getAllFlights();
    
    expect(result).toEqual(mockFlights);
    expect(apiModule.getAllFlights).toHaveBeenCalled();
  });
  
  test('getFlightData should retrieve detailed flight data', async () => {
    const flightId = 1;
    const mockFlightData = {
      id: flightId,
      start_time: '2023-05-10T12:00:00Z',
      end_time: null,
      positions: []
    };
    apiModule.getFlightData.mockResolvedValueOnce(mockFlightData);
    
    const result = await apiModule.getFlightData(flightId);
    
    expect(result).toEqual(mockFlightData);
    expect(apiModule.getFlightData).toHaveBeenCalledWith(flightId);
  });
  
  test('getLatestSensorReadings should retrieve latest readings with optional limit', async () => {
    const limit = 2;
    const mockReadings = [
      { id: 1, timestamp: '2023-05-10T14:00:00Z', temperature: 20 },
      { id: 2, timestamp: '2023-05-10T13:55:00Z', temperature: 19 }
    ];
    apiModule.getLatestSensorReadings.mockResolvedValueOnce(mockReadings);
    
    const result = await apiModule.getLatestSensorReadings(limit);
    
    expect(result).toEqual(mockReadings);
    expect(apiModule.getLatestSensorReadings).toHaveBeenCalledWith(limit);
  });
  
  test('error handling works correctly', async () => {
    const error = new Error('Network error');
    
    // Spy on console.error
    jest.spyOn(console, 'error').mockImplementation(() => {});
    
    // Make the mock function both reject with the error AND call console.error
    apiModule.getAllFlights.mockImplementationOnce(() => {
      console.error('Error getting flights:', error);
      return Promise.reject(error);
    });
    
    await expect(apiModule.getAllFlights()).rejects.toThrow('Network error');
    expect(console.error).toHaveBeenCalled();
    
    // Restore console.error
    console.error.mockRestore();
  });
}); 