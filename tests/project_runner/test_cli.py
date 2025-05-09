"""
Tests for the project_runner.cli module.
"""
import pytest
from unittest.mock import patch, MagicMock, call
import sys
import os
import signal
import argparse
import logging

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, project_root)

# Import the project_runner module
from project_runner import cli

@pytest.fixture
def reset_processes():
    """Reset the cli.processes list before and after each test."""
    cli.processes = []
    yield
    cli.processes = []

def test_parse_args_defaults():
    """Test parsing command line arguments with defaults."""
    # Test with no args
    with patch('sys.argv', ['run.py']):
        args = cli.parse_args()
        
    assert not args.no_backend
    assert not args.no_frontend
    assert not args.simulation
    assert args.simulation_config is None
    assert not args.verbose

def test_parse_args_with_options():
    """Test parsing command line arguments with options."""
    # Test with all options
    with patch('sys.argv', [
        'run.py', 
        '--no-backend', 
        '--no-frontend', 
        '--simulation', 
        '--simulation-config', 'test_config.json',
        '--verbose'
    ]):
        args = cli.parse_args()
        
    assert args.no_backend
    assert args.no_frontend
    assert args.simulation
    assert args.simulation_config == 'test_config.json'
    assert args.verbose

@patch('logging.getLogger')
def test_setup_logging_verbose(mock_get_logger):
    """Test setting up logging with verbose flag."""
    mock_logger = MagicMock()
    mock_root_logger = MagicMock()
    
    # Mock the return values
    mock_get_logger.side_effect = lambda name=None: mock_root_logger if name is None else mock_logger
    
    # Call with verbose=True
    cli.setup_logging(verbose=True)
    
    # Root logger should be set to DEBUG
    mock_root_logger.setLevel.assert_called_once_with(logging.DEBUG)

@patch('logging.getLogger')
def test_setup_logging_normal(mock_get_logger):
    """Test setting up logging without verbose flag."""
    mock_logger = MagicMock()
    mock_root_logger = MagicMock()
    
    # Return root logger for getLogger() with no args
    # Return specific logger for getLogger() with args
    mock_get_logger.side_effect = lambda name=None: mock_root_logger if name is None else mock_logger
    
    # Call with verbose=False
    cli.setup_logging(verbose=False)
    
    # Root logger should be set to INFO
    mock_root_logger.setLevel.assert_called_once_with(logging.INFO)
    # Debug message should not be logged
    mock_logger.debug.assert_not_called()

@pytest.fixture
def mock_main_dependencies():
    """Create and patch all the dependencies for the main function."""
    with patch('project_runner.cli.parse_args') as mock_parse_args, \
         patch('project_runner.cli.setup_logging') as mock_setup_logging, \
         patch('project_runner.postgres.is_postgres_running') as mock_is_postgres, \
         patch('project_runner.postgres.start_postgres') as mock_start_postgres, \
         patch('project_runner.servers.start_backend') as mock_start_backend, \
         patch('project_runner.servers.start_frontend') as mock_start_frontend, \
         patch('project_runner.servers.start_simulation') as mock_start_sim, \
         patch('project_runner.process.monitor_processes') as mock_monitor, \
         patch('atexit.register') as mock_atexit, \
         patch('signal.signal') as mock_signal:
        
        # Create a mock args object that can be customised per test
        mock_args = MagicMock()
        mock_args.no_backend = False
        mock_args.no_frontend = False
        mock_args.simulation = False
        mock_args.simulation_config = None
        mock_args.verbose = False
        mock_parse_args.return_value = mock_args
        
        # Default behaviour for mocks
        mock_is_postgres.return_value = True  # Postgres is running
        mock_start_postgres.return_value = True
        mock_start_backend.return_value = True
        mock_start_frontend.return_value = True
        mock_start_sim.return_value = True
        
        # First call to monitor returns True, second returns False (to exit loop)
        mock_monitor.side_effect = [True, False]
        
        yield {
            'parse_args': mock_parse_args,
            'setup_logging': mock_setup_logging,
            'is_postgres': mock_is_postgres,
            'start_postgres': mock_start_postgres,
            'start_backend': mock_start_backend,
            'start_frontend': mock_start_frontend,
            'start_simulation': mock_start_sim,
            'monitor': mock_monitor,
            'atexit': mock_atexit,
            'signal': mock_signal,
            'args': mock_args
        }

def test_main_default_behaviour(mock_main_dependencies, reset_processes):
    """Test the default behaviour of the main function."""
    mocks = mock_main_dependencies
    
    # Ensure the processes list will be populated for monitoring
    mocks['start_backend'].return_value = True
    
    # Add a mock process to the processes list to ensure monitoring is called
    mock_process = MagicMock()
    cli.processes.append(mock_process)
    
    # Call main with patched atexit.register using a context manager
    # to capture the call made inside the function
    with patch('atexit.register') as mock_atexit_register:
        cli.main()
        
        # Verify atexit registration occurred
        mock_atexit_register.assert_called_once()
    
    # Verify expected function calls
    mocks['parse_args'].assert_called_once()
    mocks['setup_logging'].assert_called_once_with(mocks['args'].verbose)
    
    # Verify PostgreSQL checks
    mocks['is_postgres'].assert_called_once()
    mocks['start_postgres'].assert_not_called()  # PostgreSQL already running
    
    # Verify server starts
    mocks['start_backend'].assert_called_once_with(cli.processes)
    mocks['start_frontend'].assert_called_once_with(cli.processes)
    mocks['start_simulation'].assert_not_called()  # Simulation not requested
    
    # Verify process monitoring
    assert mocks['monitor'].call_count == 2

def test_main_with_postgres_not_running(mock_main_dependencies, reset_processes):
    """Test main when PostgreSQL is not running."""
    mocks = mock_main_dependencies
    
    # Set PostgreSQL as not running
    mocks['is_postgres'].return_value = False
    
    # Exit after first monitor call to keep test focused
    mocks['monitor'].side_effect = [False]
    
    # Call main
    cli.main()
    
    # Verify PostgreSQL start was attempted
    mocks['is_postgres'].assert_called_once()
    mocks['start_postgres'].assert_called_once()

def test_main_with_no_backend(mock_main_dependencies, reset_processes):
    """Test main with --no-backend flag."""
    mocks = mock_main_dependencies
    
    # Configure args for --no-backend
    mocks['args'].no_backend = True
    
    # Exit after first monitor call to keep test focused
    mocks['monitor'].side_effect = [False]
    
    # Call main
    cli.main()
    
    # Verify backend was not started but frontend was
    mocks['start_backend'].assert_not_called()
    mocks['start_frontend'].assert_called_once_with(cli.processes)

def test_main_with_no_frontend(mock_main_dependencies, reset_processes):
    """Test main with --no-frontend flag."""
    mocks = mock_main_dependencies
    
    # Configure args for --no-frontend
    mocks['args'].no_frontend = True
    
    # Exit after first monitor call to keep test focused
    mocks['monitor'].side_effect = [False]
    
    # Call main
    cli.main()
    
    # Verify backend was started but frontend was not
    mocks['start_backend'].assert_called_once_with(cli.processes)
    mocks['start_frontend'].assert_not_called()

def test_main_with_simulation(mock_main_dependencies, reset_processes):
    """Test main with --simulation flag."""
    mocks = mock_main_dependencies
    
    # Configure args for --simulation
    mocks['args'].simulation = True
    mocks['args'].simulation_config = 'test_config.json'
    
    # Exit after first monitor call to keep test focused
    mocks['monitor'].side_effect = [False]
    
    # Call main
    cli.main()
    
    # Verify simulation was started with correct configuration
    # Parameter order matches the implementation
    mocks['start_simulation'].assert_called_once_with('test_config.json', cli.processes)

def test_main_no_components_started(reset_processes):
    """Test main when no components are started."""
    with patch('project_runner.cli.parse_args') as mock_parse_args, \
         patch('project_runner.cli.setup_logging') as mock_setup_logging, \
         patch('project_runner.postgres.is_postgres_running') as mock_is_postgres, \
         patch('project_runner.process.monitor_processes') as mock_monitor:
        
        # Configure args with all components disabled
        mock_args = MagicMock()
        mock_args.no_backend = True
        mock_args.no_frontend = True
        mock_args.simulation = False
        mock_args.verbose = False
        mock_parse_args.return_value = mock_args
        
        # Set PostgreSQL as running
        mock_is_postgres.return_value = True
        
        # Monitor should not be called when no components are started
        mock_monitor.assert_not_called()
        
        # Call main
        cli.main()
        
        # Verify initial setup was performed
        mock_parse_args.assert_called_once()
        mock_setup_logging.assert_called_once()
        mock_is_postgres.assert_called_once()

def test_main_keyboard_interrupt(mock_main_dependencies, reset_processes):
    """Test main with a KeyboardInterrupt."""
    mocks = mock_main_dependencies
    
    # Configure server starts to succeed
    mocks['start_backend'].return_value = True
    mocks['start_frontend'].return_value = True
    
    # Add a mock process to the processes list to ensure monitoring is called
    mock_process = MagicMock()
    cli.processes.append(mock_process)
    
    # Set monitor process to raise KeyboardInterrupt on first call
    mocks['monitor'].side_effect = KeyboardInterrupt()
    
    # Call main
    cli.main()
    
    # Verify services were started
    mocks['start_backend'].assert_called_once_with(cli.processes)
    mocks['start_frontend'].assert_called_once_with(cli.processes)
    
    # Verify monitor was called once then exited due to KeyboardInterrupt
    mocks['monitor'].assert_called_once_with(cli.processes) 