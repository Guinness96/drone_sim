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
        # Try to connect to PostgreSQL using pg_isready
        result = subprocess.run(
            [r"C:\Program Files\PostgreSQL\16\bin\pg_isready.exe"],
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
    """Start PostgreSQL using pg_ctl with timeout handling."""
    try:
        print("Starting PostgreSQL server...")
        
        # Start PostgreSQL as a background process
        process = subprocess.Popen(
            [r"C:\Program Files\PostgreSQL\16\bin\pg_ctl.exe", "start", "-D", 
             r"C:\Program Files\PostgreSQL\16\data", "-w"],
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
                return False
            time.sleep(0.5)
        
        # Check the process return code
        if process.returncode != 0:
            stderr_output = process.stderr.read()
            print(f"Failed to start PostgreSQL. Return code: {process.returncode}")
            print(f"Error output: {stderr_output}")
            return False
        
        # Verify PostgreSQL is now running
        for _ in range(5):  # Try checking a few times
            check_result = subprocess.run(
                [r"C:\Program Files\PostgreSQL\16\bin\pg_isready.exe"],
                capture_output=True,
                text=True,
                timeout=5  # Add timeout to pg_isready call
            )
            
            if "accepting connections" in check_result.stdout:
                print("PostgreSQL started successfully")
                return True
            
            time.sleep(1)
        
        print("PostgreSQL process started but not accepting connections")
        return False
        
    except subprocess.TimeoutExpired:
        print("PostgreSQL command timed out")
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
    
    # Check if npm exists in the system
    try:
        # First check if npm is in PATH
        npm_path = "npm"
        subprocess.run([npm_path, "--version"], 
                      stdout=subprocess.PIPE, 
                      stderr=subprocess.PIPE, 
                      check=True)
    except (subprocess.SubprocessError, FileNotFoundError):
        # If npm is not in PATH, try common installation locations
        possible_paths = [
            r"C:\Program Files\nodejs\npm.cmd",
            r"C:\Program Files (x86)\nodejs\npm.cmd",
            os.path.expanduser("~\\AppData\\Roaming\\npm\\npm.cmd")
        ]
        
        npm_found = False
        for path in possible_paths:
            if os.path.exists(path):
                npm_path = path
                npm_found = True
                print(f"Found npm at: {npm_path}")
                break
                
        if not npm_found:
            print("ERROR: npm not found. Please ensure Node.js is installed and added to PATH.")
            return False
    
    # Check if frontend directory exists
    if not os.path.exists("frontend"):
        print("ERROR: Frontend directory not found. Please ensure the project structure is correct.")
        return False
        
    # Check if package.json exists in frontend directory
    if not os.path.exists(os.path.join("frontend", "package.json")):
        print("ERROR: package.json not found in frontend directory. Please ensure the frontend project is properly set up.")
        return False
    
    # Check if node_modules exists
    if not os.path.exists(os.path.join('frontend', 'node_modules')):
        print("Installing frontend dependencies...")
        try:
            subprocess.run([npm_path, "install"], 
                          cwd="frontend", 
                          check=True,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE)
        except subprocess.SubprocessError as e:
            print(f"ERROR: Failed to install frontend dependencies: {e}")
            return False
    
    try:
        frontend_process = subprocess.Popen(
            [npm_path, "start"],
            cwd=os.path.join(os.getcwd(), "frontend"),
            env={**os.environ, "BROWSER": "none"}  # Prevent browser from opening automatically
        )
        processes.append(frontend_process)
    except Exception as e:
        print(f"ERROR: Failed to start frontend: {e}")
        return False
    
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