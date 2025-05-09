import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import FlightList from '../FlightList';
import { getAllFlights } from '../../services/api';

// Mock the API module
jest.mock('../../services/api');

describe('FlightList Component', () => {
  // Sample flight data for tests
  const mockFlights = [
    { id: 1, start_time: '2023-10-25T09:00:00', end_time: '2023-10-25T09:30:00' },
    { id: 2, start_time: '2023-10-25T10:00:00', end_time: null }
  ];

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('displays loading state initially', () => {
    getAllFlights.mockResolvedValueOnce([]);
    render(<FlightList selectedFlightId={null} onSelectFlight={() => {}} />);
    
    expect(screen.getByText('Loading flights...')).toBeInTheDocument();
  });

  test('displays flights when data is loaded', async () => {
    getAllFlights.mockResolvedValueOnce(mockFlights);
    render(<FlightList selectedFlightId={null} onSelectFlight={() => {}} />);
    
    // Wait for first flight to appear
    await screen.findByText('Flight #1');
    
    // Check other elements separately
    expect(screen.getByText('Flight #2')).toBeInTheDocument();
    expect(screen.getByText(/\(Active\)/)).toBeInTheDocument(); // Flight 2 is active
  });

  test('shows empty state when no flights are available', async () => {
    getAllFlights.mockResolvedValueOnce([]);
    render(<FlightList selectedFlightId={null} onSelectFlight={() => {}} />);
    
    await screen.findByText('No flights found.');
  });

  test('shows error message when API call fails', async () => {
    getAllFlights.mockRejectedValueOnce(new Error('API Error'));
    render(<FlightList selectedFlightId={null} onSelectFlight={() => {}} />);
    
    await screen.findByText('Failed to load flights. Please try again later.');
  });

  test('calls onSelectFlight when a flight is clicked', async () => {
    getAllFlights.mockResolvedValueOnce(mockFlights);
    const mockSelectFlight = jest.fn();
    
    render(
      <FlightList 
        selectedFlightId={null} 
        onSelectFlight={mockSelectFlight} 
      />
    );
    
    // Wait for the flight item to appear using the testid
    await screen.findByTestId('flight-id-1');
    
    // Click the flight item using the data-testid
    const flightListItem = screen.getByTestId('flight-item-1');
    fireEvent.click(flightListItem);
    
    expect(mockSelectFlight).toHaveBeenCalledWith(1);
  });

  test('applies selected class to the selected flight', async () => {
    getAllFlights.mockResolvedValueOnce(mockFlights);
    
    render(<FlightList selectedFlightId={2} onSelectFlight={() => {}} />);
    
    // Wait for flights to appear
    await screen.findByTestId('flight-id-1');
    
    // Get flight items by testid
    const flight1Item = screen.getByTestId('flight-item-1');
    const flight2Item = screen.getByTestId('flight-item-2');
    
    expect(flight1Item).not.toHaveClass('selected');
    expect(flight2Item).toHaveClass('selected');
  });
}); 