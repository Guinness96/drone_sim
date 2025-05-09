#!/usr/bin/env python3
"""
Drone Simulation Project Runner

This script provides a unified way to start all components of the drone simulation project:
1. Checks if PostgreSQL is running and starts it if needed
2. Starts the Flask backend server
3. Starts the React frontend development server
4. Optionally starts a simulation (if requested)

Usage:
    python run.py [--no-backend] [--no-frontend] [--simulation]
    
For more options:
    python run.py --help
"""

import sys
import subprocess
import time
import os
import argparse
import signal
from project_runner import postgres, servers, process

# Global processes list for test compatibility
processes = []

def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Start Drone Simulation Project components")
    parser.add_argument("--no-backend", action="store_true", help="Don't start the backend server")
    parser.add_argument("--no-frontend", action="store_true", help="Don't start the frontend server")
    parser.add_argument("--simulation", action="store_true", help="Start a simulation")
    parser.add_argument("--simulation-config", type=str, help="Path to simulation configuration file")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    
    return parser.parse_args()

def is_postgres_running():
    """Check if PostgreSQL is running.
    
    Returns:
        bool: True if PostgreSQL is running, False otherwise
    """
    return postgres.is_postgres_running()

def start_postgres():
    """Start PostgreSQL server.
    
    Returns:
        bool: True if PostgreSQL was started successfully, False otherwise
    """
    result, process = postgres.start_postgres()
    if process:
        processes.append(process)
    return result

def check_port_in_use(port):
    """Check if a port is in use.
    
    Args:
        port: Port number to check
        
    Returns:
        bool: True if the port is in use, False otherwise
    """
    return servers.check_port_in_use(port)

def wait_for_server(url, max_attempts=5):
    """Wait for a server to become available.
    
    Args:
        url: URL to check
        max_attempts: Maximum number of attempts
        
    Returns:
        bool: True if server became available, False otherwise
    """
    return servers.wait_for_server(url, max_attempts)

def start_backend():
    """Start the backend server.
    
    Returns:
        bool: True if server started successfully, False otherwise
    """
    if check_port_in_use(5000):
        print("WARNING: Port 5000 is already in use. Backend may not start correctly.")
    
    print("Starting backend server...")
    
    try:
        # Start Flask backend as a module instead of directly
        backend_path = os.path.join(os.path.dirname(__file__), 'backend')
        
        # Run Flask with debug mode using the -m flag to properly handle imports
        process = subprocess.Popen(
            [sys.executable, "-m", "backend.app"],
            env={**os.environ, 'FLASK_DEBUG': '1'},
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Add to processes list
        processes.append(process)
        
        # Check if process failed immediately
        time.sleep(1)
        if process.poll() is not None:
            stderr = process.stderr.read().decode('utf-8')
            print(f"ERROR: Backend process exited immediately with code {process.returncode}")
            print(f"Error details: {stderr}")
            return False
        
        # Wait for server to become available with longer timeout (60 seconds)
        print("Waiting for backend server to be ready...")
        if not wait_for_server("http://127.0.0.1:5000", max_attempts=5):
            print("ERROR: Backend server did not start properly.")
            return False
        
        print("Backend server is running")
        return True
    
    except Exception as e:
        print(f"ERROR: Failed to start backend server: {e}")
        return False

def start_frontend():
    """Start the frontend development server.
    
    Returns:
        bool: True if server started successfully, False otherwise
    """
    # Check if frontend directory exists
    frontend_dir = os.path.join(os.path.dirname(__file__), 'frontend')
    if not os.path.exists(frontend_dir):
        print(f"ERROR: Frontend directory not found at {frontend_dir}")
        return False
    
    if check_port_in_use(3000):
        print("WARNING: Port 3000 is already in use. Frontend may not start correctly.")
    
    print("Starting frontend development server...")
    
    try:
        # Try to find npm
        npm_path = servers.find_npm_path()
        if not npm_path:
            print("ERROR: npm not found. Please ensure Node.js is installed and added to PATH.")
            return False
        
        print(f"Found npm at: {npm_path}")
        
        # Start frontend server
        process = subprocess.Popen(
            [npm_path, "start"],
            cwd=frontend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Add to processes list
        processes.append(process)
        
        # Wait for server to become available
        print("Waiting for frontend to be ready...")
        if not wait_for_server("http://127.0.0.1:3000", max_attempts=5):
            print("ERROR: Frontend server did not start properly.")
            return False
        
        print("Frontend server is running")
        return True
    
    except Exception as e:
        print(f"ERROR: Failed to start frontend server: {e}")
        return False

def start_simulation(config_file=None):
    """Start a drone simulation.
    
    Args:
        config_file: Path to simulation configuration file
        
    Returns:
        bool: True if simulation started successfully, False otherwise
    """
    result = servers.start_simulation(config_file, processes)
    return result

def clean_up():
    """Clean up all processes."""
    print("\nShutting down all processes...")
    
    for proc in processes:
        if hasattr(proc, 'poll') and proc.poll() is None:
            try:
                # Try to terminate gracefully first
                proc.terminate()
                
                # Give it a short time to terminate
                for _ in range(5):  # Wait up to 0.5 seconds
                    if proc.poll() is not None:
                        break  # Process terminated successfully
                    time.sleep(0.1)
                
                # If still running, kill it
                if proc.poll() is None:
                    print(f"Process {proc.pid if hasattr(proc, 'pid') else 'unknown'} did not terminate gracefully, killing")
                    proc.kill()
            except Exception as e:
                print(f"Error terminating process: {e}")
    
    # Also delegate to process module's clean_up for any additional handling
    # Import the process module to access its clean_up function
    from project_runner import process
    process.clean_up(processes)

def main():
    """Main entry point."""
    args = parse_args()
    
    # Register cleanup handler
    signal.signal(signal.SIGINT, lambda sig, frame: sys.exit(0))
    
    print("Starting Drone Simulation Project components")
    
    # Track component status
    status = {
        "postgres": False,
        "backend": False,
        "frontend": False,
        "simulation": False
    }
    
    # Check PostgreSQL status
    if not is_postgres_running():
        if not start_postgres():
            print("PostgreSQL could not be started. Database functionality may not work.")
        else:
            status["postgres"] = True
    else:
        print("PostgreSQL is already running")
        status["postgres"] = True
    
    # Start backend if requested
    if not args.no_backend:
        status["backend"] = start_backend()
    
    # Start frontend if requested
    if not args.no_frontend:
        status["frontend"] = start_frontend()
        if not status["frontend"]:
            print("Frontend server failed to start.")
    
    # Start simulation if requested
    if args.simulation:
        if not status["backend"]:
            print("Backend is not running. Simulation may not work correctly.")
        if not status["frontend"] and not args.no_frontend:
            print("Frontend is not running. You won't be able to visualize the simulation.")
        status["simulation"] = start_simulation(args.simulation_config)
    
    # Check if any components were started
    if not any(value for key, value in status.items() if key != "postgres"):
        print("No components were started. Exiting.")
        return 1
    
    # Report status
    print("\nComponent status:")
    print(f"PostgreSQL: {'Running' if status['postgres'] else 'Not running'}")
    if not args.no_backend:
        print(f"Backend: {'Running' if status['backend'] else 'Failed to start'}")
    if not args.no_frontend:
        print(f"Frontend: {'Running' if status['frontend'] else 'Failed to start'}")
    if args.simulation:
        print(f"Simulation: {'Running' if status['simulation'] else 'Failed to start'}")
    
    print("\nPress Ctrl+C to shut down all components.")
    
    # Keep the script running until interrupted
    try:
        while True:
            time.sleep(1)
            # Check if all processes have exited
            if not any(p.poll() is None for p in processes if hasattr(p, 'poll')):
                print("All components have stopped. Exiting.")
                break
    except KeyboardInterrupt:
        clean_up()
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 