#!/usr/bin/env python3
"""
NLP Dashboard Docker Hub Push Script

This script only builds and pushes the Docker image to Docker Hub.
It doesn't run the container locally - useful for droplet deployment.

Usage:
    python push_to_dockerhub.py
"""

import subprocess
import sys
import time
import os
from pathlib import Path

# Configuration
DOCKER_HUB_USERNAME = "tommyboy777"
IMAGE_NAME = f"{DOCKER_HUB_USERNAME}/nlp-dashboard"

class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_status(message: str) -> None:
    """Print a status message with color"""
    print(f"{Colors.BLUE}{Colors.BOLD}[INFO]{Colors.END} {message}")

def print_success(message: str) -> None:
    """Print a success message"""
    print(f"{Colors.GREEN}{Colors.BOLD}[SUCCESS]{Colors.END} {message}")

def print_error(message: str) -> None:
    """Print an error message"""
    print(f"{Colors.RED}{Colors.BOLD}[ERROR]{Colors.END} {message}")

def print_warning(message: str) -> None:
    """Print a warning message"""
    print(f"{Colors.YELLOW}{Colors.BOLD}[WARNING]{Colors.END} {message}")

def run_command(command: list, check: bool = True) -> subprocess.CompletedProcess:
    """Run a shell command and return the result"""
    start_time = time.time()
    print_status(f"Running: {' '.join(command)}")
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=check)
        elapsed = time.time() - start_time
        if result.stdout:
            print(f"{Colors.BLUE}[STDOUT]{Colors.END} {result.stdout}")
        if result.stderr:
            print(f"{Colors.YELLOW}[STDERR]{Colors.END} {result.stderr}")
        print_success(f"Command completed in {elapsed:.2f}s")
        return result
    except subprocess.CalledProcessError as e:
        elapsed = time.time() - start_time
        print_error(f"Command failed after {elapsed:.2f}s: {' '.join(command)}")
        if e.stderr:
            print(f"{Colors.RED}[ERROR]{Colors.END} {e.stderr}")
        if check:
            raise
        return e

def check_docker_installed() -> bool:
    """Check if Docker is installed and running"""
    try:
        result = run_command(["docker", "--version"], check=False)
        if result.returncode == 0:
            print_success("Docker is installed")
            return True
        else:
            print_error("Docker is not installed or not accessible")
            return False
    except FileNotFoundError:
        print_error("Docker command not found. Please install Docker Desktop.")
        return False

def check_docker_running() -> bool:
    """Check if Docker daemon is running"""
    try:
        result = run_command(["docker", "info"], check=False)
        if result.returncode == 0:
            print_success("Docker daemon is running")
            return True
        else:
            print_error("Docker daemon is not running. Please start Docker Desktop.")
            return False
    except Exception as e:
        print_error(f"Failed to check Docker status: {e}")
        return False

def check_docker_login() -> bool:
    """Check if user is logged into Docker Hub"""
    try:
        # Try to check login status by attempting a simple Docker Hub operation
        result = run_command(["docker", "search", "hello-world"], check=False)
        if result.returncode == 0:
            print_success("Docker Hub access confirmed")
            return True
        else:
            print_warning("Docker Hub access may be limited. Please run: docker login")
            return False
    except Exception:
        print_warning("Could not verify Docker Hub access. Continuing anyway...")
        return True

def build_and_push_to_dockerhub() -> bool:
    """Build and push the Docker image to Docker Hub"""
    print_status("Building and pushing to Docker Hub...")
    start_time = time.time()
    
    try:
        # Build the image
        print_status("Step 1/2: Building Docker image...")
        build_start = time.time()
        run_command([
            "docker", "build", 
            "-t", IMAGE_NAME, 
            "."
        ])
        build_time = time.time() - build_start
        print_success(f"Docker build completed in {build_time:.2f}s")
        
        # Push to Docker Hub
        print_status("Step 2/2: Pushing to Docker Hub...")
        push_start = time.time()
        run_command([
            "docker", "push", IMAGE_NAME
        ])
        push_time = time.time() - push_start
        print_success(f"Docker push completed in {push_time:.2f}s")
        
        total_time = time.time() - start_time
        print_success(f"Image built and pushed to Docker Hub: {IMAGE_NAME}")
        print_success(f"Total build and push time: {total_time:.2f}s")
        return True
    except subprocess.CalledProcessError:
        total_time = time.time() - start_time
        print_error(f"Failed to build and push Docker image after {total_time:.2f}s")
        return False

def main() -> int:
    """Main function"""
    print_status("Starting Docker Hub Push")
    print_status("="*40)
    
    # Check prerequisites
    if not check_docker_installed():
        return 1
    
    if not check_docker_running():
        return 1
    
    if not check_docker_login():
        print_warning("Please login to Docker Hub first: docker login")
        return 1
    
    # Build and push to Docker Hub
    if not build_and_push_to_dockerhub():
        return 1
    
    print_success("Docker Hub push completed successfully!")
    print(f"Image available at: {Colors.GREEN}{IMAGE_NAME}{Colors.END}")
    print(f"You can now deploy to your droplet using: python deploy_droplet.py")
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print_error("\nPush interrupted by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)
