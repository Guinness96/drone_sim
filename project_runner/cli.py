"""
Command-line interface for the project runner.

This module provides the main CLI functionality for starting project components.
"""

import sys
import time
import signal
import argparse
import logging
import atexit

from project_runner import postgres, servers, process

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('project_runner.log')
    ]
)
logger = logging.getLogger(__name__)

# Global process list
processes = []

def parse_args():
    """Parse command-line arguments.
    
    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(description="Start Drone Simulation Project components")
    parser.add_argument("--no-backend", action="store_true", help="Don't start the backend server")
    parser.add_argument("--no-frontend", action="store_true", help="Don't start the frontend server")
    parser.add_argument("--simulation", action="store_true", help="Start a simulation")
    parser.add_argument("--simulation-config", type=str, help="Path to simulation configuration file")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    
    return parser.parse_args()

def setup_logging(verbose=False):
    """Configure logging level based on verbosity.
    
    Args:
        verbose: Whether to enable verbose logging
    """
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Verbose logging enabled")
    else:
        logging.getLogger().setLevel(logging.INFO)

def main():
    """Main entry point for the CLI."""
    args = parse_args()
    setup_logging(args.verbose)
    
    # Register cleanup handler
    atexit.register(process.clean_up, processes)
    signal.signal(signal.SIGINT, lambda sig, frame: sys.exit(0))
    
    logger.info("Starting Drone Simulation Project components")
    
    # Check PostgreSQL status
    if not postgres.is_postgres_running():
        if not postgres.start_postgres():
            logger.warning("PostgreSQL could not be started. Database functionality may not work.")
    else:
        logger.info("PostgreSQL is already running")
    
    # Start backend if requested
    backend_running = False
    if not args.no_backend:
        backend_running = servers.start_backend(processes)
    
    # Start frontend if requested
    frontend_running = False
    if not args.no_frontend:
        frontend_running = servers.start_frontend(processes)
        if not frontend_running:
            logger.warning("Frontend server failed to start.")
    
    # Start simulation if requested
    if args.simulation:
        if not backend_running:
            logger.warning("Backend is not running. Simulation may not work correctly.")
        if not frontend_running and not args.no_frontend:
            logger.warning("Frontend is not running. You won't be able to visualize the simulation.")
        servers.start_simulation(args.simulation_config, processes)
    
    if not processes:
        logger.error("No components were started. Exiting.")
        return
    
    print("\nAll requested components are running.")
    print("Press Ctrl+C to shut down all components.")
    
    # Keep the script running until interrupted
    try:
        while process.monitor_processes(processes):
            time.sleep(1)
        
        print("All components have stopped. Exiting.")
    except KeyboardInterrupt:
        # Cleanup will be handled by atexit
        pass

if __name__ == "__main__":
    main() 