"""
Tests for the project_runner.process module.
"""
import pytest
from unittest.mock import patch, MagicMock
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from project_runner import process

def test_monitor_processes_all_running():
    """Test monitoring processes when all are running."""
    # Create mock processes
    process1 = MagicMock()
    process1.poll.return_value = None  # Process is still running
    process2 = MagicMock()
    process2.poll.return_value = None  # Process is still running
    
    processes_list = [process1, process2]
    
    # Monitor processes
    result = process.monitor_processes(processes_list)
    
    # Both processes still running, so list length unchanged and result is True
    assert result is True
    assert len(processes_list) == 2
    process1.poll.assert_called_once()
    process2.poll.assert_called_once()

def test_monitor_processes_some_exited():
    """Test monitoring processes when some have exited."""
    # Create mock processes
    process1 = MagicMock()
    process1.poll.return_value = None  # Process is still running
    process2 = MagicMock()
    process2.poll.return_value = 0  # Process has exited with code 0
    process2.pid = 12345
    process2.returncode = 0
    
    processes_list = [process1, process2]
    
    # Monitor processes
    with patch('logging.Logger.info') as mock_log:
        result = process.monitor_processes(processes_list)
    
    # One process still running, so list length is 1 and result is True
    assert result is True
    assert len(processes_list) == 1
    assert process1 in processes_list
    assert process2 not in processes_list
    # Check logging
    mock_log.assert_called_once_with(f"Process {process2.pid} has exited with code {process2.returncode}")

def test_monitor_processes_all_exited():
    """Test monitoring processes when all have exited."""
    # Create mock processes
    process1 = MagicMock()
    process1.poll.return_value = 0  # Process has exited with code 0
    process1.pid = 12345
    process1.returncode = 0
    process2 = MagicMock()
    process2.poll.return_value = 1  # Process has exited with code 1
    process2.pid = 67890
    process2.returncode = 1
    
    processes_list = [process1, process2]
    
    # Monitor processes
    with patch('logging.Logger.info'):
        result = process.monitor_processes(processes_list)
    
    # No processes running, so list is empty and result is False
    assert result is False
    assert len(processes_list) == 0

def test_clean_up_all_running():
    """Test cleaning up processes that are still running."""
    # Create mock processes
    process1 = MagicMock()
    process1.poll.return_value = None  # Process is still running
    process1.pid = 12345
    process2 = MagicMock()
    process2.poll.return_value = None  # Process is still running
    process2.pid = 67890
    
    processes_list = [process1, process2]
    
    # Clean up processes
    with patch('logging.Logger.info') as mock_log_info:
        with patch('time.sleep') as mock_sleep:
            process.clean_up(processes_list)
    
    # Verify that terminate was called for each process
    process1.terminate.assert_called_once()
    process2.terminate.assert_called_once()
    # Verify logging
    assert mock_log_info.call_count == 2
    # Verify sleep was called
    mock_sleep.assert_called()

def test_clean_up_graceful_termination():
    """Test cleaning up processes with graceful termination."""
    # Create mock processes
    process1 = MagicMock()
    # First poll returns None (running), second returns 0 (exited after terminate)
    process1.poll.side_effect = [None, 0]
    process1.pid = 12345
    
    processes_list = [process1]
    
    # Clean up processes
    with patch('logging.Logger.info'):
        with patch('time.sleep'):
            process.clean_up(processes_list)
    
    # Verify that terminate was called but not kill
    process1.terminate.assert_called_once()
    process1.kill.assert_not_called()

def test_clean_up_forced_termination():
    """Test cleaning up processes with forced termination (kill)."""
    # Create mock processes
    process1 = MagicMock()
    # Process doesn't terminate gracefully
    process1.poll.side_effect = [None, None]
    process1.pid = 12345
    
    processes_list = [process1]
    
    # Clean up processes
    with patch('logging.Logger.info'):
        with patch('logging.Logger.warning') as mock_log_warning:
            with patch('time.sleep'):
                process.clean_up(processes_list)
    
    # Verify that both terminate and kill were called
    process1.terminate.assert_called_once()
    process1.kill.assert_called_once()
    # Verify warning was logged
    mock_log_warning.assert_called_once()

def test_clean_up_exception():
    """Test cleaning up processes when an exception occurs."""
    # Create mock processes
    process1 = MagicMock()
    process1.poll.return_value = None  # Process is still running
    process1.pid = 12345
    process1.terminate.side_effect = Exception("Failed to terminate")
    
    processes_list = [process1]
    
    # Clean up processes
    with patch('logging.Logger.info'):
        with patch('logging.Logger.error') as mock_log_error:
            process.clean_up(processes_list)
    
    # Verify that terminate was called
    process1.terminate.assert_called_once()
    # Verify error was logged
    mock_log_error.assert_called_once() 