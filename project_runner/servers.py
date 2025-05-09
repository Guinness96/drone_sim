"""
Server management module for the project runner.

This module handles starting and managing the backend and frontend servers.
"""

import os
import sys
import time
import socket
import subprocess
from urllib.request import urlopen, URLError

def check_port_in_use(port):
    """Check if a port is already in use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def wait_for_server(url, max_attempts=5, interval=1, timeout=5):
    """Wait for a server to be ready.
    
    Args:
        url: URL to check
        max_attempts: Maximum number of attempts (default: 5)
        interval: Time between attempts in seconds (default: 1)
        timeout: Connection timeout in seconds (default: 5)
        
    Returns:
        bool: True if server became available, False otherwise
    """
    print(f"Waiting for {url} to become available...")
    attempt = 0
    start_time = time.time()
    max_time = start_time + (max_attempts * interval)
    
    while time.time() < max_time:
        try:
            response = urlopen(url, timeout=timeout)
            status = response.getcode()
            if status == 200:
                print(f"Server at {url} is available (status code: {status})")
                return True
            else:
                print(f"Server at {url} returned status code: {status}")
        except URLError as e:
            # More informative error message
            if hasattr(e, 'reason'):
                if isinstance(e.reason, ConnectionRefusedError):
                    message = "Connection refused"
                else:
                    message = str(e.reason)
            else:
                message = str(e)
                
            # Only log every 5 attempts to reduce noise
            if attempt % 5 == 0 or attempt == 0:
                print(f"Attempt {attempt+1}/{max_attempts}: {message}")
        except Exception as e:
            if attempt % 5 == 0 or attempt == 0:
                print(f"Attempt {attempt+1}/{max_attempts}: Unexpected error: {e}")
            
        attempt += 1
        
        # Sleep until next interval, but don't exceed max time
        next_check = min(time.time() + interval, max_time)
        sleep_time = max(0, next_check - time.time())
        if sleep_time > 0:
            time.sleep(sleep_time)
    
    elapsed = time.time() - start_time
    print(f"Timed out after {elapsed:.1f} seconds waiting for {url}")
    return False

def find_npm_path():
    """Find the path to the npm executable."""
    # First check if npm is in PATH
    try:
        npm_path = "npm"
        subprocess.run([npm_path, "--version"], 
                      stdout=subprocess.PIPE, 
                      stderr=subprocess.PIPE, 
                      check=True)
        return npm_path
    except (subprocess.SubprocessError, FileNotFoundError):
        # If npm is not in PATH, try common installation locations
        possible_paths = [
            r"C:\Program Files\nodejs\npm.cmd",
            r"C:\Program Files (x86)\nodejs\npm.cmd",
            os.path.expanduser("~\\AppData\\Roaming\\npm\\npm.cmd")
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                print(f"Found npm at: {path}")
                return path
        
        return None  # npm not found

def start_backend(processes_list=None):
    """Start the Flask backend server.
    
    Args:
        processes_list: Optional list to track child processes
        
    Returns:
        bool: True if backend started successfully, False otherwise
    """
    # Check if port is already in use
    if check_port_in_use(5000):
        print("WARNING: Port 5000 is already in use. Backend may not start correctly.")
    
    print("Starting backend server...")
    
    # Get the project root path
    project_root = os.getcwd()
    
    # Set up environment with PYTHONPATH to help with imports
    env = os.environ.copy()
    env["PYTHONPATH"] = project_root
    env["FLASK_DEBUG"] = "1"  # Enable Flask debug mode
    
    # Start the Flask app as a module rather than a script
    backend_process = subprocess.Popen(
        [sys.executable, "-m", "backend.app"],
        cwd=project_root,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Add to processes list if provided
    if processes_list is not None:
        processes_list.append(backend_process)
    
    # Check if process failed immediately
    time.sleep(1)
    if backend_process.poll() is not None:
        stderr = backend_process.stderr.read().decode('utf-8')
        print(f"ERROR: Backend process exited immediately with code {backend_process.returncode}")
        print(f"Error details: {stderr}")
        return False
    
    # Wait for backend to be ready
    print("Waiting for backend server to be ready...")
    if wait_for_server("http://localhost:5000", max_attempts=60):
        print("Backend server is running")
        return True
    else:
        print("Failed to start backend server")
        return False

def start_frontend(processes_list=None):
    """Start the React frontend development server.
    
    Args:
        processes_list: Optional list to track child processes
        
    Returns:
        bool: True if frontend started successfully, False otherwise
    """
    # Check if port is already in use
    if check_port_in_use(3000):
        print("WARNING: Port 3000 is already in use. Frontend may not start correctly.")
        
    print("Starting frontend development server...")
    
    # Find npm executable
    npm_path = find_npm_path()
    if not npm_path:
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
            env={**os.environ, "BROWSER": "none"},  # Prevent browser from opening automatically
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Add to processes list if provided
        if processes_list is not None:
            processes_list.append(frontend_process)
            
    except Exception as e:
        print(f"ERROR: Failed to start frontend: {e}")
        return False
    
    # Check if process failed immediately
    time.sleep(1)
    if frontend_process.poll() is not None:
        stderr = frontend_process.stderr.read().decode('utf-8')
        print(f"ERROR: Frontend process exited immediately with code {frontend_process.returncode}")
        print(f"Error details: {stderr}")
        return False
    
    # Wait for frontend to be ready
    print("Waiting for frontend to be ready...")
    if wait_for_server("http://localhost:3000", max_attempts=90):
        print("Frontend server is running")
        return True
    else:
        print("Failed to start frontend server")
        return False

def start_simulation(config=None, processes_list=None):
    """Start a drone simulation.
    
    Args:
        config: Optional path to simulation configuration file
        processes_list: Optional list to track child processes
        
    Returns:
        bool: True if simulation started successfully, False otherwise
    """
    print("Starting drone simulation...")
    cmd = [sys.executable, "-m", "simulation.drone_simulator"]
    
    if config:
        cmd.extend(["--config", config])
    
    try:
        simulation_process = subprocess.Popen(cmd, cwd=os.getcwd())
        
        # Add to processes list if provided
        if processes_list is not None:
            processes_list.append(simulation_process)
            
        print("Simulation started")
        return True
    except Exception as e:
        print(f"ERROR: Failed to start simulation: {e}")
        return False 