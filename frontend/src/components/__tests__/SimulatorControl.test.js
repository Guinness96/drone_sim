import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import SimulatorControl from '../SimulatorControl';
import axios from 'axios';

// Mock axios
jest.mock('axios');

describe('SimulatorControl Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders simulator controls correctly', () => {
    render(<SimulatorControl />);
    
    // Check headings and labels
    expect(screen.getByText('Drone Simulator Control')).toBeInTheDocument();
    expect(screen.getByText('Simulation Speed')).toBeInTheDocument();
    expect(screen.getByText('Sensor Noise Levels')).toBeInTheDocument();
    expect(screen.getByText('Temperature (°C):')).toBeInTheDocument();
    expect(screen.getByText('Humidity (%):')).toBeInTheDocument();
    expect(screen.getByText('Air Quality Index:')).toBeInTheDocument();
    expect(screen.getByText('Altitude (m):')).toBeInTheDocument();
    
    // Check slider values are displayed
    expect(screen.getByText('1.0x')).toBeInTheDocument();
    expect(screen.getByText('±5.0°C')).toBeInTheDocument();
    expect(screen.getByText('±20%')).toBeInTheDocument();
    expect(screen.getByText('±50 AQI')).toBeInTheDocument();
    expect(screen.getByText('±20m')).toBeInTheDocument();
    
    // Check start button
    expect(screen.getByText('Start Simulation')).toBeInTheDocument();
  });

  test('updates simulation speed when slider is changed', () => {
    render(<SimulatorControl />);
    
    // Get the simulation speed slider and change its value
    const speedSlider = screen.getAllByRole('slider')[0];
    fireEvent.change(speedSlider, { target: { value: '2.5' } });
    
    // Check that the displayed value is updated
    expect(screen.getByText('2.5x')).toBeInTheDocument();
  });

  test('updates sensor noise levels when sliders are changed', () => {
    render(<SimulatorControl />);
    
    // Get all sliders (first is speed, then temperature, humidity, air quality, altitude)
    const sliders = screen.getAllByRole('slider');
    
    // Change temperature noise
    fireEvent.change(sliders[1], { target: { value: '10.5' } });
    expect(screen.getByText('±10.5°C')).toBeInTheDocument();
    
    // Change humidity noise
    fireEvent.change(sliders[2], { target: { value: '35' } });
    expect(screen.getByText('±35%')).toBeInTheDocument();
    
    // Change air quality noise
    fireEvent.change(sliders[3], { target: { value: '75' } });
    expect(screen.getByText('±75 AQI')).toBeInTheDocument();
    
    // Change altitude noise
    fireEvent.change(sliders[4], { target: { value: '30' } });
    expect(screen.getByText('±30m')).toBeInTheDocument();
  });

  test('starts simulation with correct configuration', async () => {
    // Mock axios.post to resolve successfully
    axios.post.mockResolvedValueOnce({ data: { success: true } });
    
    render(<SimulatorControl />);
    
    // Get all sliders and update their values
    const sliders = screen.getAllByRole('slider');
    fireEvent.change(sliders[0], { target: { value: '3.0' } }); // Speed
    fireEvent.change(sliders[1], { target: { value: '7.5' } }); // Temperature
    
    // Click the start button
    const startButton = screen.getByText('Start Simulation');
    fireEvent.click(startButton);
    
    // Check loading state
    expect(screen.getByText('Starting...')).toBeInTheDocument();
    expect(screen.getByText('Starting simulation...')).toBeInTheDocument();
    
    // Wait for the axios call to complete
    await waitFor(() => {
      expect(axios.post).toHaveBeenCalledWith(
        'http://localhost:5000/api/simulation/start',
        {
          config: {
            simulation_speed: 3.0,
            sensor_noise_levels: {
              temperature: 7.5,
              humidity: 20.0,
              air_quality: 50.0,
              altitude: 20.0
            }
          }
        }
      );
    });
    
    // Wait for the success message to appear
    await waitFor(() => {
      expect(screen.getByText('Simulation started successfully.')).toBeInTheDocument();
    });
    
    // Check that the button is enabled again after loading is complete
    await waitFor(() => {
      const startButtonAfterLoading = screen.getByRole('button');
      expect(startButtonAfterLoading).toBeEnabled();
    });
    
    // Check button text is back to normal
    await waitFor(() => {
      expect(screen.getByRole('button')).toHaveTextContent('Start Simulation');
    });
  });

  test('handles errors when starting simulation', async () => {
    // Mock axios.post to reject with an error
    axios.post.mockRejectedValueOnce(new Error('Network error'));
    
    render(<SimulatorControl />);
    
    // Click the start button
    const startButton = screen.getByText('Start Simulation');
    fireEvent.click(startButton);
    
    // Wait for the axios call to fail
    await waitFor(() => {
      expect(screen.getByText('Error starting simulation. Please try again.')).toBeInTheDocument();
    });
    
    // Check that the button is enabled again
    expect(screen.getByText('Start Simulation')).toBeEnabled();
  });
}); 