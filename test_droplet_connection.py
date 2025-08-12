#!/usr/bin/env python3
"""
Test Droplet Connection Script

This script tests the SSH connection to the droplet to ensure deployment will work.

Usage:
    python test_droplet_connection.py
"""

import subprocess
import sys
import os

# Configuration (same as deploy_droplet.py)
DROPLET_IP = "209.38.89.159"
DROPLET_USER = "root"
SSH_KEY_PATH = "C:/Users/tommy/.ssh/id_rsa"

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

def test_ssh_connection() -> bool:
    """Test SSH connection to the droplet"""
    print_status("Testing SSH connection to droplet...")
    
    ssh_key_path = os.path.expanduser(SSH_KEY_PATH)
    
    # Check if SSH key exists
    if not os.path.exists(ssh_key_path):
        print_error(f"SSH key not found at: {ssh_key_path}")
        return False
    
    print_success(f"SSH key found at: {ssh_key_path}")
    
    # Test SSH connection
    try:
        result = subprocess.run([
            "ssh", "-i", ssh_key_path, f"{DROPLET_USER}@{DROPLET_IP}",
            "echo 'SSH connection successful' && whoami && pwd"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print_success("SSH connection successful!")
            print(f"User: {result.stdout.strip()}")
            return True
        else:
            print_error(f"SSH connection failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print_error("SSH connection timed out")
        return False
    except Exception as e:
        print_error(f"SSH connection failed: {e}")
        return False

def test_docker_on_droplet() -> bool:
    """Test if Docker is available on the droplet"""
    print_status("Testing Docker availability on droplet...")
    
    ssh_key_path = os.path.expanduser(SSH_KEY_PATH)
    
    try:
        result = subprocess.run([
            "ssh", "-i", ssh_key_path, f"{DROPLET_USER}@{DROPLET_IP}",
            "docker --version"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print_success(f"Docker is available: {result.stdout.strip()}")
            return True
        else:
            print_warning("Docker is not installed on droplet")
            return False
            
    except Exception as e:
        print_error(f"Failed to check Docker: {e}")
        return False

def test_docker_hub_access() -> bool:
    """Test if droplet can access Docker Hub"""
    print_status("Testing Docker Hub access from droplet...")
    
    ssh_key_path = os.path.expanduser(SSH_KEY_PATH)
    
    try:
        result = subprocess.run([
            "ssh", "-i", ssh_key_path, f"{DROPLET_USER}@{DROPLET_IP}",
            "docker pull hello-world"
        ], capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print_success("Docker Hub access successful!")
            return True
        else:
            print_warning(f"Docker Hub access failed: {result.stderr}")
            return False
            
    except Exception as e:
        print_error(f"Failed to test Docker Hub access: {e}")
        return False

def main() -> int:
    """Main test function"""
    print_status("Starting Droplet Connection Test")
    print_status("="*40)
    
    # Test SSH connection
    if not test_ssh_connection():
        print_error("SSH connection test failed")
        return 1
    
    # Test Docker availability
    docker_available = test_docker_on_droplet()
    
    # Test Docker Hub access
    if docker_available:
        docker_hub_ok = test_docker_hub_access()
        if not docker_hub_ok:
            print_warning("Docker Hub access failed - this may cause deployment issues")
    
    print_success("Droplet connection test completed!")
    print(f"Droplet IP: {Colors.GREEN}{DROPLET_IP}{Colors.END}")
    print(f"SSH Key: {Colors.GREEN}{SSH_KEY_PATH}{Colors.END}")
    
    if docker_available:
        print_success("Docker is available on droplet")
    else:
        print_warning("Docker needs to be installed on droplet")
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print_error("\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)
