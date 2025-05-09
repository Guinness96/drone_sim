"""
Integration tests for PostgreSQL functionality in run.py.
These tests interact with the actual PostgreSQL installation.
"""
import pytest
from unittest.mock import patch, MagicMock
import sys
import os
import time
import subprocess
import threading
from queue import Queue

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the correct modules
from project_runner import postgres
from project_runner.cli import main

# List to track processes for cleanup
processes = []

@pytest.fixture
def cleanup_postgres():
    """Fixture to clean up PostgreSQL after tests."""
    # Run the test
    yield
    
    # Teardown - stop PostgreSQL server if it's running
    try:
        subprocess.run(
            [r"C:\Program Files\PostgreSQL\16\bin\pg_ctl.exe", "stop", "-D", 
             r"C:\Program Files\PostgreSQL\16\data", "-m", "fast"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=10
        )
    except Exception as e:
        print(f"Warning: Could not stop PostgreSQL during cleanup: {e}")

@pytest.fixture
def stop_postgres():
    """Fixture to stop PostgreSQL before a test."""
    try:
        subprocess.run(
            [r"C:\Program Files\PostgreSQL\16\bin\pg_ctl.exe", "stop", "-D", 
             r"C:\Program Files\PostgreSQL\16\data", "-m", "fast"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=10
        )
        time.sleep(2)  # Give it time to stop
    except Exception:
        pass  # Ignore errors here

@pytest.fixture
def start_postgres():
    """Fixture to ensure PostgreSQL is running."""
    # First check if PostgreSQL is already running
    config = postgres.get_config()
    try:
        is_running = subprocess.run(
            [config['pg_isready']],
            capture_output=True,
            text=True,
            timeout=5
        )
        if "accepting connections" in is_running.stdout:
            # Already running, no need to start
            return
    except Exception:
        pass  # Continue to start it
        
    try:
        subprocess.run(
            [r"C:\Program Files\PostgreSQL\16\bin\pg_ctl.exe", "start", "-D", 
             r"C:\Program Files\PostgreSQL\16\data", "-w"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=30
        )
        time.sleep(2)  # Give it time to start
    except Exception as e:
        pytest.skip(f"Could not start PostgreSQL for test setup: {e}")

def test_is_postgres_running_integration(cleanup_postgres, stop_postgres):
    """Test is_postgres_running against actual PostgreSQL installation."""
    # Verify PostgreSQL is not running after being stopped
    result = postgres.is_postgres_running()
    assert result is False, "PostgreSQL should not be running after being stopped"
    
    # Start PostgreSQL
    try:
        start_result, _ = postgres.start_postgres(timeout=30)
        assert start_result is True, "PostgreSQL should start successfully"
        
        # Verify it's now running
        is_running = postgres.is_postgres_running()
        assert is_running is True, "PostgreSQL should be running after being started"
    except Exception as e:
        pytest.fail(f"Exception occurred during test: {e}")

@patch('subprocess.run')
def test_start_postgres_already_running(mock_run, cleanup_postgres):
    """Test start_postgres when PostgreSQL is already running.
    
    This test verifies that when PostgreSQL is already running,
    the start_postgres function returns True without starting a new process.
    """
    # Create a mock response with PostgreSQL already running
    mock_success = MagicMock()
    mock_success.stdout = "localhost:5432 - accepting connections"
    
    # Configure subprocess.run to always return success
    mock_run.return_value = mock_success
    
    # Call the function with a short timeout for safety
    start_result, process = postgres.start_postgres(timeout=3)
    
    # Verify the result is True (indicating success)
    assert start_result is True, "start_postgres should return True when PostgreSQL is already running"
    
    # Verify no process was returned (since we didn't start one)
    assert process is None, "No process should be returned when PostgreSQL is already running"

def test_full_startup_sequence(cleanup_postgres):
    """Test the full startup sequence for PostgreSQL.
    
    This tests the sequence of operations:
    1. Check if PostgreSQL is running
    2. Start PostgreSQL if needed
    3. Verify PostgreSQL is running
    """
    # First, capture the initial state
    initial_running = postgres.is_postgres_running()
    print(f"Initial PostgreSQL status: {'Running' if initial_running else 'Not running'}")
    
    # If PostgreSQL is already running, we can't test the startup sequence accurately
    # since we don't want to restart an already running system
    if initial_running:
        pytest.skip("PostgreSQL is already running - skipping full startup test")
    
    # Start PostgreSQL
    start_result, process = postgres.start_postgres()
    
    # Cleanup the process if it was newly started
    if process:
        processes.append(process)
    
    # Verify the start worked
    assert start_result is True, "PostgreSQL failed to start"
    
    # Verify PostgreSQL is now running
    final_running = postgres.is_postgres_running()
    assert final_running is True, "PostgreSQL should be running after start" 