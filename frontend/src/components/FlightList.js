import React, { useState, useEffect } from 'react';
import { getAllFlights } from '../services/api';

/**
 * Component to display a list of drone flights
 * @param {Object} props - Component props
 * @param {number|null} props.selectedFlightId - Currently selected flight ID
 * @param {Function} props.onSelectFlight - Callback when a flight is selected
 */
const FlightList = ({ selectedFlightId, onSelectFlight }) => {
  const [flights, setFlights] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchFlights = async () => {
      try {
        setLoading(true);
        const data = await getAllFlights();
        setFlights(data);
        setError(null);
      } catch (err) {
        setError('Failed to load flights. Please try again later.');
        console.error('Error fetching flights:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchFlights();
  }, []);

  // Format date for display
  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleString('en-GB');
  };

  if (loading) return <div>Loading flights...</div>;
  if (error) return <div className="error">{error}</div>;
  if (flights.length === 0) return <div>No flights found.</div>;

  return (
    <div className="flight-list">
      <h2>Drone Flights</h2>
      <div className="list-container">
        {flights.map((flight) => (
          <div
            key={flight.id}
            className={`flight-item ${selectedFlightId === flight.id ? 'selected' : ''}`}
            onClick={() => onSelectFlight(flight.id)}
            data-testid={`flight-item-${flight.id}`}
          >
            <div className="flight-info">
              <span className="flight-id" data-testid={`flight-id-${flight.id}`}>Flight #{flight.id}</span>
              <span className="flight-time">
                {formatDate(flight.start_time)}
                {flight.end_time ? ` - ${formatDate(flight.end_time)}` : ' (Active)'}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default FlightList; 