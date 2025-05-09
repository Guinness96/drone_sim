"""
Tests for the run.py script
"""
import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import subprocess

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

    @patch('run.subprocess.run')
    def test_is_postgres_running_success(self, mock_run):
        """Test checking if PostgreSQL is running when it is running."""
        # Setup mock to simulate PostgreSQL running
        mock_process = MagicMock()
        mock_process.stdout = "localhost:5432 - accepting connections"
        mock_run.return_value = mock_process
        
        # Call the function
        result = run.is_postgres_running()
        
        # Verify the result is True
        self.assertTrue(result)
        # Verify subprocess.run was called correctly
        mock_run.assert_called_once_with(
            [r"C:\Program Files\PostgreSQL\16\bin\pg_isready.exe"],
            capture_output=True,
            text=True
        )

    @patch('run.subprocess.run')
    def test_is_postgres_running_not_running(self, mock_run):
        """Test checking if PostgreSQL is running when it is not running."""
        # Setup mock to simulate PostgreSQL not running
        mock_process = MagicMock()
        mock_process.stdout = "localhost:5432 - no response"
        mock_run.return_value = mock_process
        
        # Call the function
        result = run.is_postgres_running()
        
        # Verify the result is False
        self.assertFalse(result)
        # Verify subprocess.run was called correctly
        mock_run.assert_called_once()

    @patch('run.subprocess.run')
    def test_is_postgres_running_exception(self, mock_run):
        """Test checking if PostgreSQL is running when an exception occurs."""
        # Setup mock to raise an exception
        mock_run.side_effect = Exception("Command not found")
        
        # Call the function
        result = run.is_postgres_running()
        
        # Verify the result is False
        self.assertFalse(result)
        # Verify subprocess.run was called
        mock_run.assert_called_once()

    @patch('run.time.sleep')
    @patch('run.subprocess.Popen')
    @patch('run.subprocess.run')
    def test_start_postgres_success(self, mock_run, mock_popen, mock_sleep):
        """Test starting PostgreSQL when it succeeds."""
        # Setup mock for subprocess.Popen
        mock_process = MagicMock()
        mock_process.poll.side_effect = [None, 0]  # First None (still running), then 0 (success)
        mock_process.returncode = 0
        mock_popen.return_value = mock_process
        
        # Setup mock for subprocess.run (pg_isready check)
        mock_run_result = MagicMock()
        mock_run_result.stdout = "localhost:5432 - accepting connections"
        mock_run.return_value = mock_run_result
        
        # Call the function
        result = run.start_postgres()
        
        # Verify the result is True
        self.assertTrue(result)
        # Verify subprocess.Popen was called with correct arguments
        mock_popen.assert_called_once_with(
            [r"C:\Program Files\PostgreSQL\16\bin\pg_ctl.exe", "start", "-D", 
             r"C:\Program Files\PostgreSQL\16\data", "-w"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        # Verify subprocess.run was called for pg_isready
        mock_run.assert_called_with(
            [r"C:\Program Files\PostgreSQL\16\bin\pg_isready.exe"],
            capture_output=True,
            text=True,
            timeout=5
        )
        # Verify time.sleep was called
        mock_sleep.assert_called()

    @patch('run.time.sleep')
    @patch('run.subprocess.Popen')
    @patch('run.subprocess.run')
    def test_start_postgres_failure(self, mock_run, mock_popen, mock_sleep):
        """Test starting PostgreSQL when it fails."""
        # Setup mock for subprocess.Popen
        mock_process = MagicMock()
        mock_process.poll.side_effect = [None, 1]  # First None (still running), then 1 (error)
        mock_process.returncode = 1
        mock_process.stderr = MagicMock()
        mock_process.stderr.read.return_value = "some error message"
        mock_popen.return_value = mock_process
        
        # Call the function
        result = run.start_postgres()
        
        # Verify the result is False
        self.assertFalse(result)
        # Verify subprocess.Popen was called once
        mock_popen.assert_called_once()
        # Verify stderr.read was called to get error message
        mock_process.stderr.read.assert_called_once()
        # Verify time.sleep was called
        mock_sleep.assert_called()

    @patch('run.time.sleep')
    @patch('run.subprocess.Popen')
    def test_start_postgres_exception(self, mock_popen, mock_sleep):
        """Test starting PostgreSQL when an exception occurs."""
        # Setup mock to raise an exception
        mock_popen.side_effect = Exception("Command not found")
        
        # Call the function
        result = run.start_postgres()
        
        # Verify the result is False
        self.assertFalse(result)
        # Verify subprocess.Popen was called
        mock_popen.assert_called_once()
        # Verify sleep was not called
        mock_sleep.assert_not_called()

    @patch('run.os.path.exists')
    @patch('run.check_port_in_use')
    @patch('run.wait_for_server')
    @patch('run.subprocess.run')
    @patch('run.subprocess.Popen')
    def test_start_frontend_success(self, mock_popen, mock_run, mock_wait, mock_check_port, mock_exists):
        """Test the start_frontend function success case."""
        # Mock check_port_in_use
        mock_check_port.return_value = False
        
        # Mock subprocess.run (npm --version)
        mock_run.return_value = MagicMock()
        
        # Mock os.path.exists
        mock_exists.return_value = True
        
        # Mock wait_for_server
        mock_wait.return_value = True
        
        # Mock subprocess.Popen
        mock_process = MagicMock()
        mock_popen.return_value = mock_process
        
        # Call the function
        result = run.start_frontend()
        
        # Verify result is True
        self.assertTrue(result)
        # Verify npm --version check was called
        mock_run.assert_called_with(
            ["npm", "--version"], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            check=True
        )
        # Verify wait_for_server was called
        mock_wait.assert_called_once()
        # Verify subprocess.Popen was called
        mock_popen.assert_called_once()
        # Verify process added to global processes list
        self.assertIn(mock_process, run.processes)

    @patch('run.os.path.exists')
    @patch('run.subprocess.run')
    def test_start_frontend_npm_not_found(self, mock_run, mock_exists):
        """Test frontend start when npm is not found."""
        # Mock npm check to fail
        mock_run.side_effect = FileNotFoundError("npm not found")
        
        # Mock os.path.exists to return False for all npm paths
        mock_exists.return_value = False
        
        # Call the function
        result = run.start_frontend()
        
        # Verify result is False
        self.assertFalse(result)
        # Verify npm --version check was called
        mock_run.assert_called_once()
        # Verify os.path.exists was called at least once
        mock_exists.assert_called()

    @patch('run.os.path.exists')
    def test_start_frontend_no_frontend_dir(self, mock_exists):
        """Test frontend start when frontend directory doesn't exist."""
        # Set up mock returns for os.path.exists
        # First call is for npm check, second for frontend directory
        mock_exists.side_effect = [True, False]
        
        # Mock subprocess.run for npm check
        with patch('run.subprocess.run') as mock_run:
            mock_run.return_value = MagicMock()  # npm check succeeds
            
            # Call the function
            result = run.start_frontend()
            
            # Verify result is False
            self.assertFalse(result)
            # Verify npm check was called
            mock_run.assert_called_once()

    def test_clean_up(self):
        """Test the clean_up function."""
        # Create mock processes
        mock_process1 = MagicMock()
        mock_process1.poll.return_value = None  # Process is running
        mock_process2 = MagicMock()
        mock_process2.poll.return_value = 0  # Process has exited
        
        # Add the mock processes to the global processes list
        run.processes = [mock_process1, mock_process2]
        
        # Call the function
        with patch('run.time.sleep'):
            run.clean_up()
        
        # Verify that terminate was called on the running process
        mock_process1.terminate.assert_called_once()
        # Verify that poll was called on both processes
        mock_process1.poll.assert_called()
        mock_process2.poll.assert_called()
        # Verify terminate was not called on the exited process
        mock_process2.terminate.assert_not_called()

if __name__ == '__main__':
    unittest.main() 