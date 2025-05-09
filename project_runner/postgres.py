"""
PostgreSQL management module for the project runner.

This module handles checking if PostgreSQL is running and starting it if needed.
"""

import time
import subprocess
import platform
import configparser
import pathlib

# Default PostgreSQL paths by platform
DEFAULT_PATHS = {
    'Windows': {
        'pg_isready': r"C:\Program Files\PostgreSQL\16\bin\pg_isready.exe",
        'pg_ctl': r"C:\Program Files\PostgreSQL\16\bin\pg_ctl.exe",
        'data_dir': r"C:\Program Files\PostgreSQL\16\data"
    },
    'Linux': {
        'pg_isready': '/usr/bin/pg_isready',
        'pg_ctl': '/usr/bin/pg_ctl',
        'data_dir': '/var/lib/postgresql/16/main'
    },
    'Darwin': {  # macOS
        'pg_isready': '/usr/local/bin/pg_isready',
        'pg_ctl': '/usr/local/bin/pg_ctl',
        'data_dir': '/usr/local/var/postgres'
    }
}

def get_config():
    """Get PostgreSQL configuration from config file or use defaults."""
    config = {}
    config_path = pathlib.Path('config.ini')
    
    # Set defaults based on platform
    system = platform.system()
    if system in DEFAULT_PATHS:
        config.update(DEFAULT_PATHS[system])
    else:
        config.update(DEFAULT_PATHS['Linux'])  # Default to Linux paths
    
    # Override with config file if it exists
    if config_path.exists():
        parser = configparser.ConfigParser()
        parser.read(config_path)
        if 'PostgreSQL' in parser:
            for key, value in parser['PostgreSQL'].items():
                if key in ['pg_isready', 'pg_ctl', 'data_dir'] and value:
                    config[key] = value
    
    return config

def is_postgres_running():
    """Check if PostgreSQL is running using pg_isready."""
    config = get_config()
    try:
        result = subprocess.run(
            [config['pg_isready']],
            capture_output=True,
            text=True
        )
        if "accepting connections" in result.stdout:
            print("PostgreSQL is running and accepting connections")
            return True
        else:
            print("PostgreSQL is installed but not running")
            return False
    except Exception as e:
        print(f"Failed to check PostgreSQL status: {e}")
        return False

def start_postgres(timeout=30):
    """Start PostgreSQL using pg_ctl with timeout handling.
    
    Returns:
        tuple: (bool, subprocess.Popen) - Success status and the process (or None if already running)
    """
    config = get_config()
    
    # First check if PostgreSQL is already running
    try:
        check_result = subprocess.run(
            [config['pg_isready']],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if "accepting connections" in check_result.stdout:
            print("PostgreSQL is already running and accepting connections")
            return True, None
    except Exception:
        # Continue with startup if check fails
        pass
    
    try:
        print("Starting PostgreSQL server...")
        
        # Start PostgreSQL as a background process
        process = subprocess.Popen(
            [config['pg_ctl'], "start", "-D", config['data_dir'], "-w"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Add a timeout to prevent hanging
        start_time = time.time()
        max_wait_time = timeout  # Maximum wait time in seconds
        
        # Wait for the process to complete or timeout
        while process.poll() is None:
            if time.time() - start_time > max_wait_time:
                print(f"PostgreSQL startup timeout after {max_wait_time} seconds")
                process.terminate()
                return False, process
            time.sleep(0.5)
        
        # Check the process return code
        if process.returncode != 0:
            stderr_output = process.stderr.read()
            # Check if it's already running (common error case)
            if "already running" in stderr_output:
                print("PostgreSQL is already running")
                return True, None
                
            print(f"Failed to start PostgreSQL. Return code: {process.returncode}")
            print(f"Error output: {stderr_output}")
            return False, process
        
        # Verify PostgreSQL is now running
        for _ in range(5):  # Try checking a few times
            check_result = subprocess.run(
                [config['pg_isready']],
                capture_output=True,
                text=True,
                timeout=5  # Add timeout to pg_isready call
            )
            
            if "accepting connections" in check_result.stdout:
                print("PostgreSQL started successfully")
                return True, process
            
            time.sleep(1)
        
        print("PostgreSQL process started but not accepting connections")
        return False, process
        
    except subprocess.TimeoutExpired:
        print("PostgreSQL command timed out")
        return False, None
    except Exception as e:
        print(f"Error starting PostgreSQL: {e}")
        return False, None 