"""
Drone Simulation Project Runner

This script provides a unified way to start all components of the drone simulation project:
1. Checks if PostgreSQL is running and starts it if needed
2. Starts the Flask backend server
3. Starts the React frontend development server
4. Optionally starts a simulation (if requested)

Usage:
    python run.py [--no-backend] [--no-frontend] [--simulation]
"""

import os
import sys
import time
import argparse
import subprocess
import signal
import atexit
import socket
from urllib.request import urlopen, URLError

# Global variables to track running processes
processes = []

def check_port_in_use(port):
    """Check if a port is already in use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def wait_for_server(url, timeout=60, interval=1):
    """Wait for a server to be ready."""
    start_time = time.time()
    while True:
        if time.time() - start_time > timeout:
            print(f"Timeout waiting for {url}")
            return False
        try:
            urlopen(url)
            return True
        except URLError:
            time.sleep(interval)

def is_postgres_running():
    """Check if PostgreSQL is running."""
    try:
        # Try to connect to PostgreSQL
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            result = s.connect_ex(('localhost', 5432))
            if result == 0:
                print("PostgreSQL is running (port 5432 is open)")
                return True
            
        # If connection fails, try platform-specific checks
        if sys.platform.startswith('win'):
            # Windows - check service
            possible_service_names = ['postgresql-x64-14', 'postgresql', 'postgresql-x64']
            for service_name in possible_service_names:
                result = subprocess.run(
                    ["sc", "query", service_name], 
                    capture_output=True, 
                    text=True
                )
                if "RUNNING" in result.stdout:
                    print(f"PostgreSQL service '{service_name}' is running")
                    return True
        elif sys.platform.startswith('linux') or sys.platform == 'darwin':
            # Linux/Mac - use ps to check
            result = subprocess.run(
                ["ps", "aux"], 
                capture_output=True, 
                text=True
            )
            if "postgres" in result.stdout:
                print("PostgreSQL process is running")
                return True
                
        print("PostgreSQL does not appear to be running")
        return False
    except Exception as e:
        print(f"Failed to check PostgreSQL status: {e}")
        return False

def start_postgres():
    """Start PostgreSQL service."""
    try:
        if sys.platform.startswith('win'):
            # Windows - find the correct service name
            possible_service_names = ['postgresql-x64-14', 'postgresql', 'postgresql-x64']
            for service_name in possible_service_names:
                print(f"Attempting to start PostgreSQL service '{service_name}'...")
                result = subprocess.run(
                    ["net", "start", service_name],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    print(f"PostgreSQL service '{service_name}' started successfully")
                    return True
                elif "already been started" in result.stderr:
                    print(f"PostgreSQL service '{service_name}' is already running")
                    return True
            print("Could not find PostgreSQL service to start")
        elif sys.platform == 'darwin':
            # macOS
            print("Starting PostgreSQL on macOS...")
            result = subprocess.run(
                ["brew", "services", "start", "postgresql"],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        elif sys.platform.startswith('linux'):
            # Linux
            print("Starting PostgreSQL on Linux...")
            result = subprocess.run(
                ["sudo", "service", "postgresql", "start"],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        else:
            print(f"Unsupported platform: {sys.platform}")
            return False
    except Exception as e:
        print(f"Error starting PostgreSQL: {e}")
        return False

def clean_up():
    """Terminate all child processes when the script exits."""
    print("\nShutting down all processes...")
    for process in processes:
        if process.poll() is None:  # Check if process is still running
            try:
                process.terminate()
                # Give it a moment to terminate gracefully
                time.sleep(1)
                if process.poll() is None:
                    process.kill()
            except Exception as e:
                print(f"Error terminating process: {e}")

def start_backend():
    """Start the Flask backend server."""
    # Check if port is already in use
    if check_port_in_use(5000):
        print("WARNING: Port 5000 is already in use. Backend may not start correctly.")
    
    print("Starting backend server...")
    # Fix the import issue by using module notation
    backend_process = subprocess.Popen(
        [sys.executable, "-m", "backend.app"],
        cwd=os.getcwd()
    )
    processes.append(backend_process)
    
    # Wait for backend to be ready
    print("Waiting for backend server to be ready...")
    if wait_for_server("http://localhost:5000", timeout=30):
        print("Backend server is running")
        return True
    else:
        print("Failed to start backend server")
        return False

def start_frontend():
    """Start the React frontend development server."""
    # Check if port is already in use
    if check_port_in_use(3000):
        print("WARNING: Port 3000 is already in use. Frontend may not start correctly.")
        
    print("Starting frontend development server...")
    # Check if node_modules exists
    if not os.path.exists(os.path.join('frontend', 'node_modules')):
        print("Installing frontend dependencies...")
        subprocess.run(["npm", "install"], cwd="frontend", check=True)
    
    frontend_process = subprocess.Popen(
        ["npm", "start"],
        cwd=os.path.join(os.getcwd(), "frontend"),
        env={**os.environ, "BROWSER": "none"}  # Prevent browser from opening automatically
    )
    processes.append(frontend_process)
    
    # Wait for frontend to be ready
    print("Waiting for frontend to be ready...")
    if wait_for_server("http://localhost:3000", timeout=90):
        print("Frontend server is running")
        return True
    else:
        print("Failed to start frontend server")
        return False

def start_simulation(config=None):
    """Start a drone simulation."""
    print("Starting drone simulation...")
    cmd = [sys.executable, "-m", "simulation.drone_simulator"]
    
    if config:
        cmd.extend(["--config", config])
    
    simulation_process = subprocess.Popen(cmd, cwd=os.getcwd())
    processes.append(simulation_process)
    print("Simulation started")
    return True

def main():
    """Main function to parse arguments and start the required components."""
    parser = argparse.ArgumentParser(description="Start Drone Simulation Project components")
    parser.add_argument("--no-backend", action="store_true", help="Don't start the backend server")
    parser.add_argument("--no-frontend", action="store_true", help="Don't start the frontend server")
    parser.add_argument("--simulation", action="store_true", help="Start a simulation")
    parser.add_argument("--simulation-config", type=str, help="Path to simulation configuration file")
    
    args = parser.parse_args()
    
    # Register cleanup handler
    atexit.register(clean_up)
    signal.signal(signal.SIGINT, lambda sig, frame: sys.exit(0))
    
    # Check PostgreSQL status
    if not is_postgres_running():
        if not start_postgres():
            print("WARNING: PostgreSQL could not be started. Database functionality may not work.")
    else:
        print("PostgreSQL is already running")
    
    # Start backend if requested
    backend_running = False
    if not args.no_backend:
        backend_running = start_backend()
    
    # Start frontend if requested
    frontend_running = False
    if not args.no_frontend:
        frontend_running = start_frontend()
        if not frontend_running:
            print("WARNING: Frontend server failed to start.")
    
    # Start simulation if requested
    if args.simulation:
        if not backend_running:
            print("WARNING: Backend is not running. Simulation may not work correctly.")
        if not frontend_running and not args.no_frontend:
            print("WARNING: Frontend is not running. You won't be able to visualize the simulation.")
        start_simulation(args.simulation_config)
    
    print("\nAll requested components are running.")
    print("Press Ctrl+C to shut down all components.")
    
    # Keep the script running until interrupted
    try:
        while True:
            time.sleep(1)
            # Check if any process has exited
            for process in processes[:]:
                if process.poll() is not None:
                    processes.remove(process)
                    print("A component has stopped running.")
            if not processes:
                print("All components have stopped. Exiting.")
                break
    except KeyboardInterrupt:
        # Cleanup will be handled by atexit
        pass

if __name__ == "__main__":
    main() 