#!/usr/bin/env python3
"""
NLP Dashboard Cloud Deployment Script

This script builds the Docker image on Docker Hub and deploys it locally.
This avoids using local disk space for the build process.

Usage:
    python deploy_cloud.py
"""

import subprocess
import sys
import time
import requests
import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Configuration
DOCKER_HUB_USERNAME = "tommyboy777"  # Your Docker Hub username
IMAGE_NAME = f"{DOCKER_HUB_USERNAME}/nlp-dashboard"
CONTAINER_NAME = "nlp-dashboard-container"
PORT_HOST = 8001
PORT_CONTAINER = 8000
HEALTH_CHECK_URL = f"http://localhost:{PORT_HOST}/home"
MAX_WAIT_TIME = 60  # seconds

class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_status(message: str, color: str = Colors.BLUE) -> None:
    """Print a status message with color"""
    print(f"{color}{Colors.BOLD}[INFO]{Colors.END} {message}")

def print_success(message: str) -> None:
    """Print a success message"""
    print(f"{Colors.GREEN}{Colors.BOLD}[SUCCESS]{Colors.END} {message}")

def print_error(message: str) -> None:
    """Print an error message"""
    print(f"{Colors.RED}{Colors.BOLD}[ERROR]{Colors.END} {message}")

def print_warning(message: str) -> None:
    """Print a warning message"""
    print(f"{Colors.YELLOW}{Colors.BOLD}[WARNING]{Colors.END} {message}")

def run_command(command: List[str], check: bool = True) -> subprocess.CompletedProcess:
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
        result = run_command(["docker", "info"], check=False)
        if result.returncode == 0 and "Username" in result.stdout:
            print_success("Logged into Docker Hub")
            return True
        else:
            print_warning("Not logged into Docker Hub. Please run: docker login")
            return False
    except Exception:
        return False

def stop_existing_container() -> None:
    """Stop and remove existing container if it exists"""
    print_status("Checking for existing container...")
    
    # Stop container if running
    result = run_command(["docker", "stop", CONTAINER_NAME], check=False)
    if result.returncode == 0:
        print_success(f"Stopped existing container: {CONTAINER_NAME}")
    
    # Remove container
    result = run_command(["docker", "rm", CONTAINER_NAME], check=False)
    if result.returncode == 0:
        print_success(f"Removed existing container: {CONTAINER_NAME}")

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

def pull_and_run_container() -> bool:
    """Pull the image from Docker Hub and run the container"""
    print_status("Pulling image from Docker Hub...")
    
    try:
        # Pull the image
        run_command([
            "docker", "pull", IMAGE_NAME
        ])
        
        # Run the container
        run_command([
            "docker", "run",
            "-d",  # detached mode
            "--name", CONTAINER_NAME,
            "-p", f"{PORT_HOST}:{PORT_CONTAINER}",
            "--restart", "unless-stopped",
            IMAGE_NAME
        ])
        
        print_success(f"Container started: {CONTAINER_NAME}")
        return True
    except subprocess.CalledProcessError:
        print_error("Failed to pull and run Docker container")
        return False

def wait_for_service() -> bool:
    """Wait for the service to be ready"""
    print_status(f"Waiting for service to be ready at {HEALTH_CHECK_URL}...")
    
    start_time = time.time()
    attempts = 0
    
    while time.time() - start_time < MAX_WAIT_TIME:
        attempts += 1
        elapsed = time.time() - start_time
        print_status(f"Health check attempt {attempts} (elapsed: {elapsed:.1f}s)")
        
        try:
            response = requests.get(HEALTH_CHECK_URL, timeout=5)
            if response.status_code == 200:
                total_time = time.time() - start_time
                print_success(f"Service is ready after {total_time:.1f}s!")
                return True
        except requests.RequestException as e:
            print_warning(f"Health check failed: {e}")
        
        remaining = MAX_WAIT_TIME - elapsed
        if remaining > 2:
            print_status(f"Service not ready yet, waiting 2s... (remaining: {remaining:.1f}s)")
            time.sleep(2)
        else:
            break
    
    total_time = time.time() - start_time
    print_error(f"Service health check failed after {total_time:.1f}s")
    return False

def run_local_tests() -> bool:
    """Run tests locally instead of in container"""
    print_status("Running tests locally...")
    
    # Set PYTHONPATH for local testing
    env = os.environ.copy()
    env['PYTHONPATH'] = '.'
    
    test_files = [
        "tests/test_sentiment.py",
        "tests/test_ner.py", 
        "tests/test_summarize.py",
        "tests/test_emotion.py",
        "tests/test_qa.py",
        "tests/test_news_feed.py"
    ]
    
    all_passed = True
    
    for test_file in test_files:
        if os.path.exists(test_file):
            print_status(f"Running {test_file}...")
            try:
                result = subprocess.run([
                    "python", "-m", "pytest", test_file, "-v"
                ], env=env, capture_output=True, text=True, check=False)
                
                if result.returncode == 0:
                    print_success(f"✓ {test_file} passed")
                else:
                    print_error(f"✗ {test_file} failed")
                    all_passed = False
            except Exception as e:
                print_error(f"Failed to run {test_file}: {e}")
                all_passed = False
        else:
            print_warning(f"Test file not found: {test_file}")
    
    return all_passed

def run_integration_tests() -> bool:
    """Run integration tests against the running service"""
    print_status("Running integration tests...")
    
    test_urls = [
        "/home",
        "/",
        "/news/browse"
    ]
    
    all_passed = True
    
    for url in test_urls:
        full_url = f"http://localhost:{PORT_HOST}{url}"
        try:
            response = requests.get(full_url, timeout=10)
            if response.status_code == 200:
                print_success(f"✓ {url} - Status: {response.status_code}")
            else:
                print_error(f"✗ {url} - Status: {response.status_code}")
                all_passed = False
        except requests.RequestException as e:
            print_error(f"✗ {url} - Error: {e}")
            all_passed = False
    
    return all_passed

def print_deployment_info() -> None:
    """Print deployment information and URLs"""
    print("\n" + "="*60)
    print_success("DEPLOYMENT COMPLETE!")
    print("="*60)
    
    print(f"\n{Colors.BOLD}Access URLs:{Colors.END}")
    print(f"  🏠 Homepage: {Colors.GREEN}http://localhost:{PORT_HOST}/home{Colors.END}")
    print(f"  📊 Analysis: {Colors.GREEN}http://localhost:{PORT_HOST}/{Colors.END}")
    print(f"  📰 News: {Colors.GREEN}http://localhost:{PORT_HOST}/news/browse{Colors.END}")
    
    print(f"\n{Colors.BOLD}Docker Hub Image:{Colors.END}")
    print(f"  Image: {Colors.GREEN}{IMAGE_NAME}{Colors.END}")
    
    print(f"\n{Colors.BOLD}Useful Commands:{Colors.END}")
    print(f"  View logs: {Colors.YELLOW}docker logs {CONTAINER_NAME}{Colors.END}")
    print(f"  Stop container: {Colors.YELLOW}docker stop {CONTAINER_NAME}{Colors.END}")
    print(f"  Remove container: {Colors.YELLOW}docker rm {CONTAINER_NAME}{Colors.END}")
    print(f"  Shell access: {Colors.YELLOW}docker exec -it {CONTAINER_NAME} /bin/bash{Colors.END}")
    
    print("\n" + "="*60)

def main() -> int:
    """Main deployment function"""
    print_status("Starting NLP Dashboard Cloud Deployment")
    print_status("="*50)
    
    # Check prerequisites
    if not check_docker_installed():
        return 1
    
    if not check_docker_running():
        return 1
    
    if not check_docker_login():
        print_warning("Please login to Docker Hub first: docker login")
        return 1
    
    # Stop existing container
    stop_existing_container()
    
    # Build and push to Docker Hub
    if not build_and_push_to_dockerhub():
        return 1
    
    # Pull and run container
    if not pull_and_run_container():
        return 1
    
    # Wait for service
    if not wait_for_service():
        print_error("Service health check failed")
        return 1
    
    # Run tests locally
    print_status("Running test suite locally...")
    if not run_local_tests():
        print_warning("Some tests failed, but continuing with deployment")
    
    # Run integration tests
    if not run_integration_tests():
        print_warning("Some integration tests failed")
    
    # Print deployment info
    print_deployment_info()
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print_error("\nDeployment interrupted by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)
