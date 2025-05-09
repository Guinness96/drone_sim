"""
Process management module for the project runner.

This module handles tracking and cleaning up child processes.
"""

import time
import logging

# Configure logger
logger = logging.getLogger(__name__)

def monitor_processes(processes_list):
    """Monitor processes and remove any that have exited.
    
    Args:
        processes_list: List of subprocess.Popen objects
        
    Returns:
        bool: True if at least one process is still running, False otherwise
    """
    for process in processes_list[:]:  # Create a copy of the list for iteration
        if process.poll() is not None:
            logger.info(f"Process {process.pid} has exited with code {process.returncode}")
            processes_list.remove(process)
            print("A component has stopped running.")
    
    return len(processes_list) > 0

def clean_up(processes_list):
    """Terminate all child processes gracefully.
    
    Args:
        processes_list: List of subprocess.Popen objects
    """
    print("\nShutting down all processes...")
    for process in processes_list:
        if process.poll() is None:  # Check if process is still running
            try:
                logger.info(f"Terminating process {process.pid}")
                process.terminate()
                # Give it a moment to terminate gracefully
                time.sleep(1)
                
                if process.poll() is None:
                    logger.warning(f"Process {process.pid} did not terminate gracefully, killing")
                    process.kill()
            except Exception as e:
                logger.error(f"Error terminating process {process.pid}: {e}")
                print(f"Error terminating process: {e}") 