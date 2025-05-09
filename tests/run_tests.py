#!/usr/bin/env python3
"""
Test runner script for the drone simulation project.

This script runs all tests for the project, organised by module.
"""
import os
import sys
import subprocess

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def run_project_runner_tests():
    """Run the project_runner module tests."""
    print("\n=== Running project_runner tests ===")
    result = subprocess.run(["pytest", "tests/project_runner", "-v"], 
                          capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print("Errors:", result.stderr)
    return result.returncode == 0

def run_simulation_tests():
    """Run simulation tests."""
    print("\n=== Running simulation tests ===")
    # Run the main simulator tests
    simulator_result = subprocess.run(["pytest", "simulation/tests", "-v"], 
                                    capture_output=True, text=True)
    print(simulator_result.stdout)
    if simulator_result.stderr:
        print("Errors:", simulator_result.stderr)
    
    # Run the physics tests
    physics_result = subprocess.run(["pytest", "simulation/test_drone_physics.py", "-v"], 
                                  capture_output=True, text=True)
    print(physics_result.stdout)
    if physics_result.stderr:
        print("Errors:", physics_result.stderr)
    
    # Run the physics integration tests
    integration_result = subprocess.run(["pytest", "simulation/test_physics_integration.py", "-v"], 
                                      capture_output=True, text=True)
    print(integration_result.stdout)
    if integration_result.stderr:
        print("Errors:", integration_result.stderr)
    
    return (simulator_result.returncode == 0 and 
            physics_result.returncode == 0 and 
            integration_result.returncode == 0)

def run_backend_tests():
    """Run backend tests."""
    print("\n=== Running backend tests ===")
    result = subprocess.run(["pytest", "backend/tests", "-v"], 
                          capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print("Errors:", result.stderr)
    return result.returncode == 0

def run_integration_tests():
    """Run integration tests."""
    print("\n=== Running integration tests ===")
    result = subprocess.run(["pytest", "tests/test_postgres_integration.py", "-v"], 
                          capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print("Errors:", result.stderr)
    return result.returncode == 0

def run_all_tests():
    """Run all tests in the project."""
    print("\n=== Running all tests ===")
    result = subprocess.run(["pytest", "-v"], 
                          capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print("Errors:", result.stderr)
    return result.returncode == 0

if __name__ == "__main__":
    # Parse arguments
    import argparse
    parser = argparse.ArgumentParser(description="Run tests for the drone simulation project")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("--project-runner", action="store_true", help="Run project_runner tests")
    parser.add_argument("--simulation", action="store_true", help="Run simulation tests")
    parser.add_argument("--backend", action="store_true", help="Run backend tests")
    parser.add_argument("--integration", action="store_true", help="Run integration tests")
    
    args = parser.parse_args()
    
    # Default to running project_runner tests if no args provided
    if not any(vars(args).values()):
        args.project_runner = True
    
    # Track test success
    success = True
    
    # Run tests based on arguments
    if args.all:
        success = run_all_tests()
    else:
        if args.project_runner:
            success = run_project_runner_tests() and success
        
        if args.simulation:
            success = run_simulation_tests() and success
        
        if args.backend:
            success = run_backend_tests() and success
        
        if args.integration:
            success = run_integration_tests() and success
    
    # Exit with appropriate status code
    sys.exit(0 if success else 1) 