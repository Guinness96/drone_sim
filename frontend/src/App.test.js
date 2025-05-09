import React from 'react';
import { render, screen } from '@testing-library/react';
import App from './App';

// Mock the components to simplify the test
jest.mock('./components/FlightList', () => {
  return function MockFlightList(props) {
    return (
      <div data-testid="flight-list-component">
        FlightList Component (Selected Flight: {props.selectedFlightId || 'none'})
      </div>
    );
  };
});

jest.mock('./components/SensorDataTable', () => {
  return function MockSensorDataTable(props) {
    return (
      <div data-testid="sensor-data-table-component">
        SensorDataTable Component (Selected Flight: {props.selectedFlightId || 'none'})
      </div>
    );
  };
});

describe('App Component', () => {
  test('renders the header and both components', () => {
    render(<App />);
    
    // Check for the header
    expect(screen.getByText('Autonomous Drone Dashboard')).toBeInTheDocument();
    
    // Check for the components
    expect(screen.getByTestId('flight-list-component')).toBeInTheDocument();
    expect(screen.getByTestId('sensor-data-table-component')).toBeInTheDocument();
    
    // Check that initially no flight is selected
    expect(screen.getByText('FlightList Component (Selected Flight: none)')).toBeInTheDocument();
    expect(screen.getByText('SensorDataTable Component (Selected Flight: none)')).toBeInTheDocument();
  });
});
