"""
Integration tests for PostgreSQL functionality in run.py.
These tests interact with the actual PostgreSQL installation.
"""
import unittest
from unittest.mock import patch
import sys
import os
import time
import subprocess

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import run

class PostgreSQLIntegrationTests(unittest.TestCase):
    """Integration tests for PostgreSQL functionality."""
    
    def tearDown(self):
        """Clean up PostgreSQL state after tests."""
        try:
            # Stop PostgreSQL server if it's running
            subprocess.run(
                [r"C:\Program Files\PostgreSQL\16\bin\pg_ctl.exe", "stop", "-D", 
                 r"C:\Program Files\PostgreSQL\16\data", "-m", "fast"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=10
            )
        except Exception as e:
            print(f"Warning: Could not stop PostgreSQL during tearDown: {e}")
    
    def test_is_postgres_running_integration(self):
        """Test is_postgres_running against actual PostgreSQL installation."""
        # First stop PostgreSQL if it's running
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
        
        # Check that PostgreSQL is not running
        result = run.is_postgres_running()
        self.assertFalse(result, "PostgreSQL should not be running after being stopped")
        
        # Start PostgreSQL
        try:
            start_result = run.start_postgres(timeout=30)
            self.assertTrue(start_result, "PostgreSQL should start successfully")
            
            # Check that it's now running
            is_running = run.is_postgres_running()
            self.assertTrue(is_running, "PostgreSQL should be running after being started")
        except Exception as e:
            self.fail(f"Exception occurred during test: {e}")
    
    def test_start_postgres_already_running(self):
        """Test start_postgres when PostgreSQL is already running."""
        # First ensure PostgreSQL is running
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
            self.skipTest(f"Could not start PostgreSQL for test setup: {e}")
        
        # Confirm PostgreSQL is running
        is_running = run.is_postgres_running()
        if not is_running:
            self.skipTest("Could not start PostgreSQL for test setup")
        
        # Try to start it again
        start_result = run.start_postgres()
        
        # This should return True as PostgreSQL is already running
        # (since pg_ctl with -w waits for server startup)
        self.assertTrue(start_result, "start_postgres should succeed when PostgreSQL is already running")
    
    def test_full_startup_sequence(self):
        """Test the complete PostgreSQL startup sequence in the main function."""
        # First stop PostgreSQL if it's running
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
        
        # Create mock command-line arguments for PostgreSQL-only operation
        with patch('sys.argv', ['run.py', '--no-backend', '--no-frontend']):
            # Mock time.sleep to avoid blocking indefinitely
            with patch('run.time.sleep', side_effect=KeyboardInterrupt):
                # Run the main function
                try:
                    run.main()
                    # If we get here, no exceptions were raised
                    self.assertTrue(run.is_postgres_running(), 
                                    "PostgreSQL should be running after main function execution")
                except KeyboardInterrupt:
                    # This is expected due to our mock
                    # Check if PostgreSQL is running
                    self.assertTrue(run.is_postgres_running(), 
                                   "PostgreSQL should be running after KeyboardInterrupt")
                except Exception as e:
                    self.fail(f"Unexpected exception in main function: {e}")

if __name__ == '__main__':
    unittest.main() 