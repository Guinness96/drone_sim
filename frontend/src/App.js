import React, { useState } from 'react';
import './App.css';
import FlightList from './components/FlightList';
import SensorDataTable from './components/SensorDataTable';
import SimulatorControl from './components/SimulatorControl';

function App() {
  const [selectedFlightId, setSelectedFlightId] = useState(null);
  const [showSimulatorControl, setShowSimulatorControl] = useState(false);

  // Handle flight selection
  const handleSelectFlight = (flightId) => {
    setSelectedFlightId(flightId === selectedFlightId ? null : flightId);
  };

  // Toggle simulator control panel
  const toggleSimulatorControl = () => {
    setShowSimulatorControl(!showSimulatorControl);
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Autonomous Drone Dashboard</h1>
        <button 
          className="simulator-toggle"
          onClick={toggleSimulatorControl}
        >
          {showSimulatorControl ? 'Hide Simulator Controls' : 'Show Simulator Controls'}
        </button>
      </header>
      <main>
        {showSimulatorControl && (
          <div className="simulator-panel">
            <SimulatorControl />
          </div>
        )}
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
