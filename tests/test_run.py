"""
Tests for the run.py script
"""
import pytest
from unittest.mock import patch, MagicMock
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import run

@pytest.fixture
def reset_processes():
    """Reset the processes list before and after each test."""
    old_processes = run.processes.copy()
    run.processes = []
    yield
    run.processes = old_processes

@patch('run.is_postgres_running')
@patch('run.start_postgres')
@patch('run.start_backend')
@patch('run.start_frontend')
@patch('run.start_simulation')
def test_main_default_behaviour(mock_start_sim, mock_start_frontend, 
                              mock_start_backend, mock_start_postgres, 
                              mock_is_postgres):
    """Test the default behaviour of the main function with no args"""
    # Setup mocks
    mock_is_postgres.return_value = True  # Postgres is running
    mock_start_backend.return_value = True
    mock_start_frontend.return_value = True
    
    # Mock sys.argv
    with patch('sys.argv', ['run.py']):
        # Call main with Ctrl+C simulated after a moment
        with patch('run.time.sleep', side_effect=KeyboardInterrupt):
            run.main()
    
    # Verify postgres check was called
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
def test_main_with_simulation(mock_start_sim, mock_start_frontend, 
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
def test_main_no_frontend(mock_start_sim, mock_start_frontend, 
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
@patch('run.time.sleep')
def test_start_backend(mock_sleep, mock_popen, mock_wait, mock_check_port, reset_processes):
    """Test the start_backend function
    
    This test verifies that:
    1. The backend server starts correctly
    2. The process continues running (poll returns None)
    3. The server becomes available (wait_for_server returns True)
    4. The function returns True for successful startup
    """
    # Mock port check (port not in use)
    mock_check_port.return_value = False
    
    # Mock server becoming available
    mock_wait.return_value = True
    
    # Configure mock subprocess with additional details
    mock_process = MagicMock()
    mock_process.poll.return_value = None  # Process is still running
    
    # Set up mock stderr stream
    mock_stderr = MagicMock()
    mock_stderr.read.return_value = b""  # Empty stderr (no errors)
    mock_process.stderr = mock_stderr
    
    # Configure the Popen mock to return our process
    mock_popen.return_value = mock_process
    
    # Call function
    result = run.start_backend()
    
    # Verify result is True (backend started successfully)
    assert result is True, "start_backend should return True when the server starts successfully"
    
    # Verify subprocess.Popen was called with correct args
    mock_popen.assert_called_once()
    
    # Verify process was added to global processes list
    assert mock_process in run.processes

@patch('run.check_port_in_use')
@patch('run.wait_for_server')
@patch('run.subprocess.Popen')
def test_start_backend_failure(mock_popen, mock_wait, mock_check_port, reset_processes):
    """Test backend start failure"""
    # Mock server never becoming available
    mock_wait.return_value = False
    # Mock subprocess
    mock_process = MagicMock()
    mock_popen.return_value = mock_process
    
    # Call function
    result = run.start_backend()
    
    # Verify result is False (backend failed to start)
    assert result is False
    # Process should still be in the list even if server didn't respond
    assert mock_process in run.processes

@patch('run.subprocess.run')
def test_is_postgres_running_success(mock_run):
    """Test checking if PostgreSQL is running when it is running."""
    # Setup mock to simulate PostgreSQL running
    mock_process = MagicMock()
    mock_process.stdout = "localhost:5432 - accepting connections"
    mock_run.return_value = mock_process
    
    # Call the function
    result = run.is_postgres_running()
    
    # Verify the result is True
    assert result is True
    # Verify subprocess.run was called correctly
    mock_run.assert_called_once_with(
        [r"C:\Program Files\PostgreSQL\16\bin\pg_isready.exe"],
        capture_output=True,
        text=True
    )

@patch('run.subprocess.run')
def test_is_postgres_running_not_running(mock_run):
    """Test checking if PostgreSQL is running when it is not running."""
    # Setup mock to simulate PostgreSQL not running
    mock_process = MagicMock()
    mock_process.stdout = "localhost:5432 - no response"
    mock_run.return_value = mock_process
    
    # Call the function
    result = run.is_postgres_running()
    
    # Verify the result is False
    assert result is False
    # Verify subprocess.run was called correctly
    mock_run.assert_called_once()

@patch('run.subprocess.run')
def test_is_postgres_running_exception(mock_run):
    """Test checking if PostgreSQL is running when an exception occurs."""
    # Setup mock to raise an exception
    mock_run.side_effect = Exception("Command not found")
    
    # Call the function
    result = run.is_postgres_running()
    
    # Verify the result is False
    assert result is False
    # Verify subprocess.run was called
    mock_run.assert_called_once()

@patch('run.time.sleep')
@patch('run.subprocess.Popen')
@patch('run.subprocess.run')
@patch('project_runner.postgres.start_postgres')
def test_start_postgres_success(mock_postgres_start, mock_run, mock_popen, mock_sleep, reset_processes):
    """Test starting PostgreSQL when it succeeds."""
    # Setup mock process
    mock_process = MagicMock()
    
    # Setup mock for postgres.start_postgres to return success and the process
    mock_postgres_start.return_value = (True, mock_process)
    
    # Call function
    result = run.start_postgres()
    
    # Verify result is True (PostgreSQL started successfully)
    assert result is True
    # Verify process added to global processes list
    assert mock_process in run.processes

@patch('run.time.sleep')
@patch('run.subprocess.Popen')
@patch('run.subprocess.run')
def test_start_postgres_failure(mock_run, mock_popen, mock_sleep, reset_processes):
    """Test starting PostgreSQL when it fails."""
    # Setup mock for subprocess.Popen
    mock_process = MagicMock()
    mock_process.poll.return_value = 1  # Failed with exit code 1
    mock_process.returncode = 1
    mock_popen.return_value = mock_process
    
    # Setup mock for subprocess.run (pg_isready check)
    mock_run_result = MagicMock()
    mock_run_result.stdout = "localhost:5432 - no response"
    mock_run.return_value = mock_run_result
    
    # Call function
    result = run.start_postgres()
    
    # Verify result is False (PostgreSQL failed to start)
    assert result is False
    # Verify process added to global processes list
    assert mock_process in run.processes

@patch('run.time.sleep')
@patch('run.subprocess.Popen')
def test_start_postgres_exception(mock_popen, mock_sleep, reset_processes):
    """Test starting PostgreSQL when an exception occurs."""
    # Setup mock to raise an exception
    mock_popen.side_effect = Exception("Command not found")
    
    # Call function
    result = run.start_postgres()
    
    # Verify result is False (PostgreSQL failed to start)
    assert result is False

@patch('run.os.path.exists')
@patch('run.check_port_in_use')
@patch('run.wait_for_server')
@patch('run.subprocess.run')
@patch('run.subprocess.Popen')
def test_start_frontend_success(mock_popen, mock_run, mock_wait, mock_check_port, mock_exists, reset_processes):
    """Test starting frontend when it succeeds."""
    # Mock directory exists
    mock_exists.return_value = True
    # Mock port check (port not in use)
    mock_check_port.return_value = False
    # Mock server becoming available
    mock_wait.return_value = True
    # Mock subprocess.run for npm path discovery
    mock_run.return_value = MagicMock(stdout="C:\\path\\to\\npm.cmd")
    # Mock subprocess
    mock_process = MagicMock()
    mock_popen.return_value = mock_process
    
    # Call function
    result = run.start_frontend()
    
    # Verify result is True (frontend started successfully)
    assert result is True
    # Verify subprocess.run was called to find npm
    mock_run.assert_called_once()
    # Verify subprocess.Popen was called to start frontend
    mock_popen.assert_called_once()
    # Verify process added to global processes list
    assert mock_process in run.processes

@patch('run.os.path.exists')
@patch('run.subprocess.run')
def test_start_frontend_npm_not_found(mock_run, mock_exists, reset_processes):
    """Test starting frontend when npm is not found."""
    # Mock directory exists
    mock_exists.return_value = True
    # Mock npm not found
    mock_run.side_effect = Exception("npm not found")
    
    # Call function
    result = run.start_frontend()
    
    # Verify result is False (frontend failed to start)
    assert result is False
    # Verify subprocess.run was called to find npm
    mock_run.assert_called_once()

@patch('run.os.path.exists')
def test_start_frontend_no_frontend_dir(mock_exists, reset_processes):
    """Test starting frontend when frontend directory doesn't exist."""
    # Mock directory doesn't exist
    mock_exists.return_value = False
    
    # Call function
    result = run.start_frontend()
    
    # Verify result is False (frontend failed to start)
    assert result is False
    # Verify os.path.exists was called with the correct path
    mock_exists.assert_called_with(os.path.join(os.path.dirname(os.path.abspath(run.__file__)), 'frontend'))

@patch('project_runner.process.clean_up')  # Patch imported process.clean_up
def test_clean_up(mock_process_clean_up, reset_processes):
    """Test the clean_up function.
    
    This test verifies that:
    1. Running processes are terminated gracefully
    2. Already exited processes are not terminated
    3. Processes that don't terminate gracefully are killed
    4. The process module's clean_up function is called correctly
    """
    # Create some mock processes
    process1 = MagicMock()
    # Set up poll to return None first time (running), then 0 (terminated)
    process1.poll.side_effect = [None, 0, 0, 0]
    process1.terminate = MagicMock()
    process1.kill = MagicMock()
    
    process2 = MagicMock()
    process2.poll.return_value = 0  # Already exited
    process2.terminate = MagicMock()
    process2.kill = MagicMock()
    
    # Add processes to global list
    run.processes = [process1, process2]
    
    # Call clean_up
    run.clean_up()
    
    # Verify process1 was terminated (it was still running)
    process1.terminate.assert_called_once()
    # Since process1 responded to terminate, kill should not be called
    process1.kill.assert_not_called()
    
    # Verify process2 was not terminated (it already exited)
    process2.terminate.assert_not_called()
    process2.kill.assert_not_called()
    
    # Verify the imported process.clean_up was called with the processes list
    mock_process_clean_up.assert_called_once_with(run.processes)
    
    # Now create a new test with a process that doesn't respond to terminate
    run.processes = []
    process3 = MagicMock()
    # Will always return None - indicating it's never terminating
    process3.poll.return_value = None
    process3.terminate = MagicMock()
    process3.kill = MagicMock()
    
    run.processes = [process3]
    
    # Reset the process clean_up mock for this second test case
    mock_process_clean_up.reset_mock()
    
    # Call clean_up again
    with patch('run.time.sleep'):  # Skip sleeps for speed
        run.clean_up()
    
    # Verify process3 was terminated and then killed
    process3.terminate.assert_called_once()
    process3.kill.assert_called_once()
    
    # Verify the imported process.clean_up was called again
    mock_process_clean_up.assert_called_once_with(run.processes) 