import React, { useState } from 'react';
import './App.css';
import FlightList from './components/FlightList';
import SensorDataTable from './components/SensorDataTable';

function App() {
  const [selectedFlightId, setSelectedFlightId] = useState(null);

  // Handle flight selection
  const handleSelectFlight = (flightId) => {
    setSelectedFlightId(flightId === selectedFlightId ? null : flightId);
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Autonomous Drone Dashboard</h1>
      </header>
      <main>
        <div className="dashboard-container">
          <div className="sidebar">
            <FlightList 
              selectedFlightId={selectedFlightId}
              onSelectFlight={handleSelectFlight}
            />
          </div>
          <div className="main-content">
            <SensorDataTable selectedFlightId={selectedFlightId} />
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
