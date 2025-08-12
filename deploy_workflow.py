#!/usr/bin/env python3
"""
NLP Dashboard Complete Deployment Workflow

This script orchestrates the complete deployment process:
1. Build and push Docker image to Docker Hub (using local Docker Desktop)
2. Deploy to Digital Ocean droplet by pulling from Docker Hub

Usage:
    python deploy_workflow.py
"""

import subprocess
import sys
import time
import os
from pathlib import Path

# Import the deployment functions
from deploy_local_docker_hub import (
    check_docker_installed, check_docker_running, check_docker_login,
    build_and_push_to_dockerhub, print_status, print_success, print_error, print_warning
)

from deploy_droplet import (
    check_prerequisites, setup_droplet, deploy_to_droplet, setup_firewall,
    wait_for_service, run_remote_tests, print_deployment_info
)

class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_workflow_status(message: str) -> None:
    """Print a workflow status message"""
    print(f"{Colors.BLUE}{Colors.BOLD}[WORKFLOW]{Colors.END} {message}")

def main() -> int:
    """Main workflow function"""
    print_workflow_status("Starting Complete NLP Dashboard Deployment Workflow")
    print("="*70)
    overall_start = time.time()
    
    # Phase 1: Local Docker Hub Setup
    print_workflow_status("Phase 1/4: Setting up local Docker environment...")
    
    if not check_docker_installed():
        return 1
    
    if not check_docker_running():
        return 1
    
    if not check_docker_login():
        print_warning("Please login to Docker Hub first: docker login")
        return 1
    
    # Phase 2: Build and Push to Docker Hub
    print_workflow_status("Phase 2/4: Building and pushing to Docker Hub...")
    if not build_and_push_to_dockerhub():
        print_error("Failed to build and push to Docker Hub")
        return 1
    
    # Phase 3: Droplet Prerequisites
    print_workflow_status("Phase 3/4: Checking droplet prerequisites...")
    if not check_prerequisites():
        print_error("Droplet prerequisites check failed")
        return 1
    
    # Phase 4: Deploy to Droplet
    print_workflow_status("Phase 4/4: Deploying to droplet...")
    
    # Set up droplet (only if needed)
    setup_choice = input("Set up droplet with Docker? (y/n): ").lower().strip()
    if setup_choice == 'y':
        if not setup_droplet():
            print_error("Failed to set up droplet")
            return 1
    
    # Deploy application
    if not deploy_to_droplet():
        print_error("Failed to deploy to droplet")
        return 1
    
    # Set up firewall
    firewall_choice = input("Set up firewall? (y/n): ").lower().strip()
    if firewall_choice == 'y':
        if not setup_firewall():
            print_warning("Firewall setup failed, but continuing...")
    
    # Wait for service
    if not wait_for_service():
        print_error("Service health check failed")
        return 1
    
    # Run remote tests
    test_choice = input("Run remote tests? (y/n): ").lower().strip()
    if test_choice == 'y':
        if not run_remote_tests():
            print_warning("Some remote tests failed")
    
    # Print deployment info
    overall_time = time.time() - overall_start
    print_success(f"Complete workflow finished in {overall_time:.2f}s")
    print_deployment_info()
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print_error("\nWorkflow interrupted by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)
