"""
Tests for the run.py script
"""
import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import run

class TestRunScript(unittest.TestCase):
    """Test the run.py script functionality"""
    
    @patch('run.is_postgres_running')
    @patch('run.start_postgres')
    @patch('run.start_backend')
    @patch('run.start_frontend')
    @patch('run.start_simulation')
    def test_main_default_behavior(self, mock_start_sim, mock_start_frontend, 
                                  mock_start_backend, mock_start_postgres, 
                                  mock_is_postgres):
        """Test the default behavior of the main function with no args"""
        # Setup mocks
        mock_is_postgres.return_value = True  # Postgres is running
        mock_start_backend.return_value = True
        mock_start_frontend.return_value = True
        
        # Mock sys.argv
        with patch('sys.argv', ['run.py']):
            # Call main with Ctrl+C simulated after a moment
            with patch('run.time.sleep', side_effect=KeyboardInterrupt):
                run.main()
        
        # Assert postgres check was called
        mock_is_postgres.assert_called_once()
        # Postgres should not be started since it's already running
        mock_start_postgres.assert_not_called()
        # Backend and frontend should be started
        mock_start_backend.assert_called_once()
        mock_start_frontend.assert_called_once()
        # Simulation should not be started without --simulation flag
        mock_start_sim.assert_not_called()

    @patch('run.is_postgres_running')
    @patch('run.start_postgres')
    @patch('run.start_backend')
    @patch('run.start_frontend')
    @patch('run.start_simulation')
    def test_main_with_simulation(self, mock_start_sim, mock_start_frontend, 
                                 mock_start_backend, mock_start_postgres, 
                                 mock_is_postgres):
        """Test with simulation flag enabled"""
        # Setup mocks
        mock_is_postgres.return_value = True
        mock_start_backend.return_value = True
        mock_start_frontend.return_value = True
        
        # Mock sys.argv with simulation flag
        with patch('sys.argv', ['run.py', '--simulation']):
            # Call main with Ctrl+C simulated after a moment
            with patch('run.time.sleep', side_effect=KeyboardInterrupt):
                run.main()
        
        # Simulation should be started
        mock_start_sim.assert_called_once()
        mock_start_sim.assert_called_with(None)  # No config provided

    @patch('run.is_postgres_running')
    @patch('run.start_postgres')
    @patch('run.start_backend')
    @patch('run.start_frontend')
    @patch('run.start_simulation')
    def test_main_no_frontend(self, mock_start_sim, mock_start_frontend, 
                             mock_start_backend, mock_start_postgres, 
                             mock_is_postgres):
        """Test with --no-frontend flag"""
        # Setup mocks
        mock_is_postgres.return_value = True
        mock_start_backend.return_value = True
        
        # Mock sys.argv with no-frontend flag
        with patch('sys.argv', ['run.py', '--no-frontend']):
            # Call main with Ctrl+C simulated after a moment
            with patch('run.time.sleep', side_effect=KeyboardInterrupt):
                run.main()
        
        # Frontend should not be started
        mock_start_frontend.assert_not_called()
        # Backend should be started
        mock_start_backend.assert_called_once()

    @patch('run.check_port_in_use')
    @patch('run.wait_for_server')
    @patch('run.subprocess.Popen')
    def test_start_backend(self, mock_popen, mock_wait, mock_check_port):
        """Test the start_backend function"""
        # Mock port check (port not in use)
        mock_check_port.return_value = False
        # Mock server becoming available
        mock_wait.return_value = True
        # Mock subprocess
        mock_process = MagicMock()
        mock_popen.return_value = mock_process
        
        # Call function
        result = run.start_backend()
        
        # Verify result is True (backend started successfully)
        self.assertTrue(result)
        # Verify subprocess.Popen was called with correct args
        mock_popen.assert_called_once()
        # Verify process added to global processes list
        self.assertIn(mock_process, run.processes)

    @patch('run.check_port_in_use')
    @patch('run.wait_for_server')
    @patch('run.subprocess.Popen')
    def test_start_backend_failure(self, mock_popen, mock_wait, mock_check_port):
        """Test backend start failure"""
        # Mock server never becoming available
        mock_wait.return_value = False
        # Mock subprocess
        mock_process = MagicMock()
        mock_popen.return_value = mock_process
        
        # Call function
        result = run.start_backend()
        
        # Verify result is False (backend failed to start)
        self.assertFalse(result)
        # Process should still be in the list even if server didn't respond
        self.assertIn(mock_process, run.processes)

if __name__ == '__main__':
    unittest.main() 