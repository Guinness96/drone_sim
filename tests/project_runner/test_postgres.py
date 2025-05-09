"""
Tests for the project_runner.postgres module.
"""
import pytest
from unittest.mock import patch, MagicMock
import subprocess
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from project_runner import postgres

@pytest.mark.parametrize("system,expected", [
    ('Windows', {
        'pg_isready': r"C:\Program Files\PostgreSQL\16\bin\pg_isready.exe",
        'pg_ctl': r"C:\Program Files\PostgreSQL\16\bin\pg_ctl.exe",
        'data_dir': r"C:\Program Files\PostgreSQL\16\data"
    }),
    ('Linux', {
        'pg_isready': '/usr/bin/pg_isready',
        'pg_ctl': '/usr/bin/pg_ctl',
        'data_dir': '/var/lib/postgresql/16/main'
    })
])
def test_get_config_default(system, expected):
    """Test getting config on different platforms."""
    with patch('platform.system', return_value=system):
        with patch('pathlib.Path.exists', return_value=False):
            config = postgres.get_config()
            assert config['pg_isready'] == expected['pg_isready']
            assert config['pg_ctl'] == expected['pg_ctl']
            assert config['data_dir'] == expected['data_dir']

def test_get_config_from_file():
    """Test getting config from file."""
    mock_config = {
        'PostgreSQL': {
            'pg_isready': '/custom/pg_isready',
            'pg_ctl': '/custom/pg_ctl',
            'data_dir': '/custom/data'
        }
    }
    
    with patch('platform.system', return_value='Windows'):
        with patch('pathlib.Path.exists', return_value=True):
            with patch('configparser.ConfigParser.read'):
                with patch('configparser.ConfigParser.__getitem__', 
                          side_effect=lambda k: mock_config[k]):
                    with patch('configparser.ConfigParser.__contains__', 
                              return_value=True):
                        config = postgres.get_config()
                        assert config['pg_isready'] == '/custom/pg_isready'
                        assert config['pg_ctl'] == '/custom/pg_ctl'
                        assert config['data_dir'] == '/custom/data'

@patch('project_runner.postgres.get_config')
@patch('subprocess.run')
def test_is_postgres_running_success(mock_run, mock_get_config):
    """Test checking if PostgreSQL is running when it is running."""
    # Setup mocks
    mock_get_config.return_value = {
        'pg_isready': '/path/to/pg_isready'
    }
    
    mock_process = MagicMock()
    mock_process.stdout = "localhost:5432 - accepting connections"
    mock_run.return_value = mock_process
    
    # Call the function
    result = postgres.is_postgres_running()
    
    # Verify the result is True
    assert result is True
    # Verify subprocess.run was called correctly
    mock_run.assert_called_once_with(
        ['/path/to/pg_isready'],
        capture_output=True,
        text=True
    )

@patch('project_runner.postgres.get_config')
@patch('subprocess.run')
def test_is_postgres_running_not_running(mock_run, mock_get_config):
    """Test checking if PostgreSQL is running when it is not running."""
    # Setup mocks
    mock_get_config.return_value = {
        'pg_isready': '/path/to/pg_isready'
    }
    
    mock_process = MagicMock()
    mock_process.stdout = "localhost:5432 - no response"
    mock_run.return_value = mock_process
    
    # Call the function
    result = postgres.is_postgres_running()
    
    # Verify the result is False
    assert result is False
    # Verify subprocess.run was called correctly
    mock_run.assert_called_once()

@patch('project_runner.postgres.get_config')
@patch('subprocess.run')
def test_is_postgres_running_exception(mock_run, mock_get_config):
    """Test checking if PostgreSQL is running when an exception occurs."""
    # Setup mocks
    mock_get_config.return_value = {
        'pg_isready': '/path/to/pg_isready'
    }
    
    # Setup mock to raise an exception
    mock_run.side_effect = Exception("Command not found")
    
    # Call the function
    result = postgres.is_postgres_running()
    
    # Verify the result is False
    assert result is False
    # Verify subprocess.run was called
    mock_run.assert_called_once()

@patch('project_runner.postgres.get_config')
@patch('time.sleep')
@patch('subprocess.Popen')
@patch('subprocess.run')
def test_start_postgres_success(mock_run, mock_popen, mock_sleep, mock_get_config):
    """Test starting PostgreSQL when it succeeds."""
    # Setup mocks
    mock_get_config.return_value = {
        'pg_ctl': '/path/to/pg_ctl',
        'data_dir': '/path/to/data',
        'pg_isready': '/path/to/pg_isready'
    }
    
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
    result, process = postgres.start_postgres()
    
    # Verify the result is True and process is our mock
    assert result is True
    assert process is mock_process or process is None  # Could be None if "already running" case

@patch('project_runner.postgres.get_config')
@patch('time.sleep')
@patch('subprocess.Popen')
def test_start_postgres_failure(mock_popen, mock_sleep, mock_get_config):
    """Test starting PostgreSQL when it fails."""
    # Setup mocks
    mock_get_config.return_value = {
        'pg_ctl': '/path/to/pg_ctl',
        'data_dir': '/path/to/data'
    }
    
    # Setup mock for subprocess.Popen
    mock_process = MagicMock()
    mock_process.poll.side_effect = [None, 1]  # First None (still running), then 1 (error)
    mock_process.returncode = 1
    mock_process.stderr = MagicMock()
    mock_process.stderr.read.return_value = "some error message"
    mock_popen.return_value = mock_process
    
    # Call the function
    result, process = postgres.start_postgres()
    
    # Verify the result is False
    assert result is False
    assert process is mock_process

@patch('project_runner.postgres.get_config')
@patch('subprocess.Popen')
def test_start_postgres_exception(mock_popen, mock_get_config):
    """Test starting PostgreSQL when an exception occurs."""
    # Setup mocks
    mock_get_config.return_value = {
        'pg_ctl': '/path/to/pg_ctl',
        'data_dir': '/path/to/data'
    }
    
    # Setup mock to raise an exception
    mock_popen.side_effect = Exception("Command not found")
    
    # Call the function
    result, process = postgres.start_postgres()
    
    # Verify the result is False
    assert result is False
    assert process is None 