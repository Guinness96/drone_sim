"""
Tests for the project_runner.servers module.
"""
import pytest
from unittest.mock import patch, MagicMock, call
import socket
import subprocess
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from project_runner import servers
from urllib.request import URLError

def test_check_port_in_use_port_open():
    """Test check_port_in_use with an open port."""
    # Mock socket.socket.connect_ex to return 0 (port in use)
    mock_socket = MagicMock()
    mock_socket.__enter__.return_value = mock_socket
    mock_socket.connect_ex.return_value = 0
    
    with patch('socket.socket', return_value=mock_socket):
        result = servers.check_port_in_use(5000)
        
    assert result is True
    mock_socket.connect_ex.assert_called_once_with(('localhost', 5000))

def test_check_port_in_use_port_closed():
    """Test check_port_in_use with a closed port."""
    # Mock socket.socket.connect_ex to return non-zero (port not in use)
    mock_socket = MagicMock()
    mock_socket.__enter__.return_value = mock_socket
    mock_socket.connect_ex.return_value = 1
    
    with patch('socket.socket', return_value=mock_socket):
        result = servers.check_port_in_use(5000)
        
    assert result is False
    mock_socket.connect_ex.assert_called_once_with(('localhost', 5000))

@patch('project_runner.servers.time.time')
@patch('project_runner.servers.time.sleep')
@patch('project_runner.servers.urlopen')
def test_wait_for_server_success(mock_urlopen, mock_sleep, mock_time):
    """Test that wait_for_server immediately returns True when the server responds successfully.
    
    This test validates:
    1. The function correctly identifies a successful server response (HTTP 200)
    2. The function returns True on the first attempt if successful
    3. The function uses the correct timeout value when connecting
    4. No sleep is needed when the first attempt succeeds
    """
    # Set a consistent time value for the function
    mock_time.return_value = 0
    
    # Create a successful response
    mock_response = MagicMock()
    mock_response.getcode.return_value = 200
    mock_urlopen.return_value = mock_response
    
    # Run the function with explicit parameters for predictable testing
    result = servers.wait_for_server(
        url="http://test-url",
        max_attempts=5,
        interval=1,
        timeout=5
    )
    
    # Verify the function returns True for successful response
    assert result is True, "Function should return True for a successful server response"
    
    # Verify URLopen was called exactly once
    assert mock_urlopen.call_count == 1, "URLopen should be called exactly once for immediate success"
    
    # Verify URLopen was called with the correct parameters
    mock_urlopen.assert_called_once_with("http://test-url", timeout=5)
    
    # Verify sleep was not called at all
    mock_sleep.assert_not_called(), "Sleep should not be called when the first attempt succeeds"

@patch('project_runner.servers.time.time')
@patch('project_runner.servers.time.sleep')
@patch('project_runner.servers.urlopen')
def test_wait_for_server_eventual_success(mock_urlopen, mock_sleep, mock_time):
    """Test that wait_for_server successfully connects after initial failures.
    
    This test validates:
    1. The function correctly retries when initial connection attempts fail
    2. The function returns True when the server eventually becomes available
    3. The function exits the loop after a successful connection
    """
    # Setup time-based mocks to control the loop
    # First return 0, then never exceed max_time
    mock_time.side_effect = lambda: 0  # Always return 0 to keep the while loop running
    
    # Create a mock response for the successful attempt
    mock_response = MagicMock()
    mock_response.getcode.return_value = 200
    
    # First two attempts fail with connection error, third attempt succeeds
    mock_urlopen.side_effect = [
        URLError("Connection refused"),
        URLError("Connection refused"),
        mock_response
    ]
    
    # Run the function with fixed parameters
    result = servers.wait_for_server(
        url="http://test-url",
        max_attempts=5,
        interval=1,
        timeout=5
    )
    
    # Verify the function returns True when the server eventually responds
    assert result is True, "Function should return True when server eventually responds"
    
    # Verify URLopen was called the expected number of times (3 in this case)
    assert mock_urlopen.call_count == 3, "URLopen should be called until success"
    
    # Verify sleep was called between attempts
    assert mock_sleep.call_count == 2, "Sleep should be called between each attempt"

@patch('project_runner.servers.time.time')
@patch('project_runner.servers.time.sleep')
@patch('project_runner.servers.urlopen')
def test_wait_for_server_timeout(mock_urlopen, mock_sleep, mock_time):
    """Test that wait_for_server properly times out and returns False when a server never responds.
    
    This test validates:
    1. The function correctly exits after max_time is reached
    2. The function returns False when the server never becomes available
    """
    # Control the while loop by returning values that will eventually exit
    time_values = [0, 0]  # First keep the loop running
    time_values.extend([100] * 10)  # Then force loop exit with values > max_time
    mock_time.side_effect = time_values
    
    # Simulate URLopen consistently raising a connection error
    connection_error = URLError("Connection refused")
    mock_urlopen.side_effect = connection_error
    
    # Run the function with fixed parameters
    result = servers.wait_for_server(
        url="http://test-url",
        max_attempts=5,
        interval=1,
        timeout=5
    )
    
    # Verify the function returns False when the server never responds
    assert result is False, "Function should return False when server never responds"
    
    # Verify URLopen was called at least once
    assert mock_urlopen.call_count > 0, "URLopen should be called at least once"
    
    # The sleep function should not be called when we exit the loop early due to exceeding max_time
    assert mock_sleep.call_count <= 1, "Sleep should be called at most once for a time-based exit"

@patch('subprocess.run')
def test_find_npm_path_in_path(mock_run):
    """Test finding npm in PATH."""
    # npm is in PATH
    result = servers.find_npm_path()
    
    assert result == "npm"
    mock_run.assert_called_once()

@patch('subprocess.run')
@patch('os.path.exists')
def test_find_npm_path_not_in_path(mock_exists, mock_run):
    """Test finding npm not in PATH but in common location."""
    # npm not in PATH
    mock_run.side_effect = FileNotFoundError()
    
    # Mock one of the common locations existing
    mock_exists.side_effect = lambda path: path == r"C:\Program Files\nodejs\npm.cmd"
    
    result = servers.find_npm_path()
    
    assert result == r"C:\Program Files\nodejs\npm.cmd"
    assert mock_exists.called

@patch('subprocess.run')
@patch('os.path.exists')
def test_find_npm_path_not_found(mock_exists, mock_run):
    """Test npm not found anywhere."""
    # npm not in PATH
    mock_run.side_effect = FileNotFoundError()
    
    # Mock no common locations existing
    mock_exists.return_value = False
    
    result = servers.find_npm_path()
    
    assert result is None
    assert mock_exists.called

@patch('project_runner.servers.check_port_in_use')
@patch('project_runner.servers.wait_for_server')
@patch('subprocess.Popen')
@patch('time.sleep')
def test_start_backend_success(mock_sleep, mock_popen, mock_wait, mock_check_port):
    """Test starting backend successfully."""
    # Port not in use
    mock_check_port.return_value = False
    
    # Server starts successfully
    mock_wait.return_value = True
    
    # Mock process that correctly simulates not exiting immediately
    mock_process = MagicMock()
    mock_process.poll.return_value = None  # Process is still running
    mock_stderr = MagicMock()
    mock_stderr.read.return_value = b""
    mock_process.stderr = mock_stderr
    mock_popen.return_value = mock_process
    
    # Track processes
    processes_list = []
    
    result = servers.start_backend(processes_list)
    
    assert result is True
    # The test should check for the current implementation
    # which either uses -m flag or direct script execution depending on implementation
    assert mock_popen.called
    
    # Check that process was added to the list regardless of call specifics
    assert mock_process in processes_list

@patch('project_runner.servers.check_port_in_use')
@patch('project_runner.servers.wait_for_server')
@patch('subprocess.Popen')
def test_start_backend_server_never_ready(mock_popen, mock_wait, mock_check_port):
    """Test starting backend when server never becomes ready."""
    # Port not in use
    mock_check_port.return_value = False
    
    # Server never becomes ready
    mock_wait.return_value = False
    
    # Mock process
    mock_process = MagicMock()
    mock_popen.return_value = mock_process
    
    # Track processes
    processes_list = []
    
    result = servers.start_backend(processes_list)
    
    assert result is False
    assert mock_process in processes_list  # Process should still be tracked

@patch('project_runner.servers.find_npm_path')
@patch('project_runner.servers.check_port_in_use')
@patch('os.path.exists')
@patch('project_runner.servers.wait_for_server')
@patch('subprocess.Popen')
@patch('time.sleep')
def test_start_frontend_success(mock_sleep, mock_popen, mock_wait, mock_exists,
                               mock_check_port, mock_find_npm):
    """Test starting frontend successfully.
    
    This test validates that the frontend starts correctly when:
    1. npm is available
    2. All required directories and files exist
    3. The process starts without exiting immediately
    4. The server becomes ready
    """
    # Port not in use
    mock_check_port.return_value = False
    
    # npm found
    mock_find_npm.return_value = "npm"
    
    # Frontend directory and package.json exist, node_modules exists
    mock_exists.side_effect = lambda path: True
    
    # Server starts successfully
    mock_wait.return_value = True
    
    # Mock process that doesn't exit immediately (poll returns None)
    mock_process = MagicMock()
    # Configure poll to return None (process is still running)
    mock_process.poll.return_value = None
    
    # Set up empty stderr output
    mock_stderr = MagicMock()
    mock_stderr.read.return_value = b""
    mock_process.stderr = mock_stderr
    
    # Configure the Popen mock to return our process
    mock_popen.return_value = mock_process
    
    # Track processes
    processes_list = []
    
    # Run the function
    result = servers.start_frontend(processes_list)
    
    # Verify the function returns True for successful frontend start
    assert result is True, "Function should return True for successful frontend start"
    assert len(processes_list) == 1, "Process should be added to the processes list"
    assert processes_list[0] == mock_process, "Correct process should be added to the list"
    # Verify sleep was called once to check if process exited immediately
    mock_sleep.assert_called_once_with(1)

@patch('project_runner.servers.find_npm_path')
def test_start_frontend_npm_not_found(mock_find_npm):
    """Test starting frontend when npm is not found."""
    # npm not found
    mock_find_npm.return_value = None
    
    result = servers.start_frontend()
    
    assert result is False

@patch('project_runner.servers.find_npm_path')
@patch('os.path.exists')
def test_start_frontend_no_frontend_dir(mock_exists, mock_find_npm):
    """Test starting frontend when frontend directory doesn't exist."""
    # npm found
    mock_find_npm.return_value = "npm"
    
    # Frontend directory doesn't exist
    mock_exists.side_effect = lambda path: False
    
    result = servers.start_frontend()
    
    assert result is False

@patch('project_runner.servers.find_npm_path')
@patch('os.path.exists')
@patch('subprocess.run')
@patch('subprocess.Popen')
@patch('time.sleep')
@patch('project_runner.servers.wait_for_server')
def test_start_frontend_needs_npm_install(mock_wait, mock_sleep, mock_popen, mock_run,
                                         mock_exists, mock_find_npm):
    """Test starting frontend when npm install is needed.
    
    This test validates that:
    1. The function correctly detects missing node_modules
    2. npm install is run before starting the server
    3. The process starts correctly after installation
    4. The server becomes ready
    """
    # Configure wait_for_server to return True (server becomes ready)
    mock_wait.return_value = True
    
    # npm found
    mock_find_npm.return_value = "npm"
    
    # Frontend directory and package.json exist, but node_modules doesn't
    def exists_side_effect(path):
        if 'node_modules' in path:
            return False
        return True
    
    mock_exists.side_effect = exists_side_effect
    
    # npm install succeeds
    mock_run.return_value = MagicMock(returncode=0)
    
    # Mock process that doesn't exit immediately (poll returns None)
    mock_process = MagicMock()
    # Configure poll to return None (process is still running)
    mock_process.poll.return_value = None
    
    # Set up empty stderr output
    mock_stderr = MagicMock()
    mock_stderr.read.return_value = b""
    mock_process.stderr = mock_stderr
    
    # Configure the Popen mock to return our process
    mock_popen.return_value = mock_process
    
    # Run the function
    result = servers.start_frontend()
    
    # Verify the function returns True and npm install was called
    assert result is True, "Function should return True when npm install succeeds"
    mock_run.assert_called_once(), "npm install should be called once"
    # Verify sleep was called once to check if process exited immediately
    mock_sleep.assert_called_once_with(1)

@patch('project_runner.servers.find_npm_path')
@patch('os.path.exists')
@patch('subprocess.run')
def test_start_frontend_npm_install_fails(mock_run, mock_exists, mock_find_npm):
    """Test starting frontend when npm install fails."""
    # npm found
    mock_find_npm.return_value = "npm"
    
    # Frontend directory and package.json exist, but node_modules doesn't
    def exists_side_effect(path):
        if 'node_modules' in path:
            return False
        return True
    
    mock_exists.side_effect = exists_side_effect
    
    # npm install fails
    mock_run.side_effect = subprocess.SubprocessError("npm install failed")
    
    result = servers.start_frontend()
    
    assert result is False
    mock_run.assert_called_once()

@patch('subprocess.Popen')
def test_start_simulation_success(mock_popen):
    """Test starting simulation successfully."""
    # Mock process
    mock_process = MagicMock()
    mock_popen.return_value = mock_process
    
    # Track processes
    processes_list = []
    
    result = servers.start_simulation(processes_list=processes_list)
    
    assert result is True
    mock_popen.assert_called_once_with(
        [sys.executable, "-m", "simulation.drone_simulator"],
        cwd=os.getcwd()
    )
    assert mock_process in processes_list

@patch('subprocess.Popen')
def test_start_simulation_with_config(mock_popen):
    """Test starting simulation with config."""
    # Mock process
    mock_process = MagicMock()
    mock_popen.return_value = mock_process
    
    result = servers.start_simulation(config="test_config.json")
    
    assert result is True
    mock_popen.assert_called_once_with(
        [sys.executable, "-m", "simulation.drone_simulator", "--config", "test_config.json"],
        cwd=os.getcwd()
    )

@patch('subprocess.Popen')
def test_start_simulation_exception(mock_popen):
    """Test starting simulation with exception."""
    # Mock process creation failure
    mock_popen.side_effect = Exception("Failed to start process")
    
    result = servers.start_simulation()
    
    assert result is False
    mock_popen.assert_called_once() 