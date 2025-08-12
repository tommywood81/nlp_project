#!/usr/bin/env python3
"""
NLP Dashboard Digital Ocean Droplet Deployment Script

This script deploys the NLP Dashboard to a Digital Ocean droplet.
It assumes the Docker image is already built and pushed to Docker Hub.

Usage:
    python deploy_droplet.py
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
DOCKER_HUB_USERNAME = "tommyboy777"
IMAGE_NAME = f"{DOCKER_HUB_USERNAME}/nlp-dashboard"
CONTAINER_NAME = "nlp-dashboard-container"
PORT_HOST = 8001  # Using port 8001 to avoid conflict with fraud dashboard on port 80
PORT_CONTAINER = 8000

# Digital Ocean Droplet Configuration
DROPLET_IP = "209.38.89.159"  # Your Digital Ocean droplet IP
DROPLET_USER = "root"  # Usually 'root' for Digital Ocean
SSH_KEY_PATH = "C:/Users/tommy/.ssh/id_rsa"  # Path to your SSH private key
DOMAIN = "YOUR_DOMAIN.com"  # Optional: your domain name

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

def check_prerequisites() -> bool:
    """Check if all prerequisites are met"""
    print_status("Checking prerequisites...")
    
    # Check if droplet IP is configured
    if DROPLET_IP == "YOUR_DROPLET_IP":
        print_error("Please set DROPLET_IP in the script configuration")
        return False
    
    # Check if SSH key exists
    ssh_key_path = os.path.expanduser(SSH_KEY_PATH)
    if not os.path.exists(ssh_key_path):
        print_error(f"SSH key not found at: {ssh_key_path}")
        return False
    
    # Check if we can connect to the droplet
    try:
        result = run_command([
            "ssh", "-i", ssh_key_path, f"{DROPLET_USER}@{DROPLET_IP}",
            "echo 'SSH connection successful'"
        ], check=False)
        
        if result.returncode == 0:
            print_success("SSH connection to droplet successful")
        else:
            print_error("Cannot connect to droplet via SSH")
            return False
            
    except Exception as e:
        print_error(f"SSH connection failed: {e}")
        return False
    
    return True

def setup_droplet() -> bool:
    """Set up the droplet with Docker and required software"""
    print_status("Setting up droplet...")
    start_time = time.time()
    
    ssh_key_path = os.path.expanduser(SSH_KEY_PATH)
    
    try:
        # Update system
        print_status("Step 1/3: Updating system packages...")
        step_start = time.time()
        run_command([
            "ssh", "-i", ssh_key_path, f"{DROPLET_USER}@{DROPLET_IP}",
            "apt-get update && apt-get upgrade -y"
        ])
        step_time = time.time() - step_start
        print_success(f"System update completed in {step_time:.2f}s")
        
        # Install Docker
        print_status("Step 2/3: Installing Docker...")
        step_start = time.time()
        run_command([
            "ssh", "-i", ssh_key_path, f"{DROPLET_USER}@{DROPLET_IP}",
            "curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh"
        ])
        step_time = time.time() - step_start
        print_success(f"Docker installation completed in {step_time:.2f}s")
        
        # Install Docker Compose
        print_status("Step 3/3: Installing Docker Compose...")
        step_start = time.time()
        run_command([
            "ssh", "-i", ssh_key_path, f"{DROPLET_USER}@{DROPLET_IP}",
            "curl -L \"https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)\" -o /usr/local/bin/docker-compose && chmod +x /usr/local/bin/docker-compose"
        ])
        step_time = time.time() - step_start
        print_success(f"Docker Compose installation completed in {step_time:.2f}s")
        
        total_time = time.time() - start_time
        print_success(f"Droplet setup completed in {total_time:.2f}s")
        return True
        
    except subprocess.CalledProcessError:
        total_time = time.time() - start_time
        print_error(f"Failed to set up droplet after {total_time:.2f}s")
        return False

def deploy_to_droplet() -> bool:
    """Deploy the application to the droplet"""
    print_status("Deploying to droplet...")
    start_time = time.time()
    
    ssh_key_path = os.path.expanduser(SSH_KEY_PATH)
    
    try:
        # Stop and remove existing container
        print_status("Step 1/4: Stopping existing container...")
        step_start = time.time()
        run_command([
            "ssh", "-i", ssh_key_path, f"{DROPLET_USER}@{DROPLET_IP}",
            f"docker stop {CONTAINER_NAME} || true"
        ], check=False)
        
        run_command([
            "ssh", "-i", ssh_key_path, f"{DROPLET_USER}@{DROPLET_IP}",
            f"docker rm {CONTAINER_NAME} || true"
        ], check=False)
        step_time = time.time() - step_start
        print_success(f"Container cleanup completed in {step_time:.2f}s")
        
        # Pull the latest image
        print_status("Step 2/4: Pulling latest Docker image...")
        step_start = time.time()
        run_command([
            "ssh", "-i", ssh_key_path, f"{DROPLET_USER}@{DROPLET_IP}",
            f"docker pull {IMAGE_NAME}"
        ])
        step_time = time.time() - step_start
        print_success(f"Image pull completed in {step_time:.2f}s")
        
        # Run the container
        print_status("Step 3/4: Starting container...")
        step_start = time.time()
        run_command([
            "ssh", "-i", ssh_key_path, f"{DROPLET_USER}@{DROPLET_IP}",
            f"docker run -d --name {CONTAINER_NAME} -p {PORT_HOST}:{PORT_CONTAINER} --restart unless-stopped {IMAGE_NAME}"
        ])
        step_time = time.time() - step_start
        print_success(f"Container started in {step_time:.2f}s")
        
        # Verify container is running
        print_status("Step 4/4: Verifying container status...")
        step_start = time.time()
        run_command([
            "ssh", "-i", ssh_key_path, f"{DROPLET_USER}@{DROPLET_IP}",
            f"docker ps | grep {CONTAINER_NAME}"
        ])
        step_time = time.time() - step_start
        print_success(f"Container verification completed in {step_time:.2f}s")
        
        total_time = time.time() - start_time
        print_success(f"Deployment to droplet completed in {total_time:.2f}s")
        return True
        
    except subprocess.CalledProcessError:
        total_time = time.time() - start_time
        print_error(f"Failed to deploy to droplet after {total_time:.2f}s")
        return False

def setup_nginx_proxy() -> bool:
    """Set up Nginx as a reverse proxy (optional)"""
    print_status("Setting up Nginx reverse proxy...")
    
    ssh_key_path = os.path.expanduser(SSH_KEY_PATH)
    
    try:
        # Install Nginx
        run_command([
            "ssh", "-i", ssh_key_path, f"{DROPLET_USER}@{DROPLET_IP}",
            "apt-get install -y nginx"
        ])
        
        # Create Nginx configuration
        nginx_config = f"""
server {{
    listen 80;
    server_name {DROPLET_IP} {DOMAIN if DOMAIN != "YOUR_DOMAIN.com" else ""};
    
    location / {{
        proxy_pass http://localhost:{PORT_HOST};
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
}}
"""
        
        # Upload Nginx config
        with open("nginx_config", "w") as f:
            f.write(nginx_config)
        
        run_command([
            "scp", "-i", ssh_key_path, "nginx_config", f"{DROPLET_USER}@{DROPLET_IP}:/etc/nginx/sites-available/nlp-dashboard"
        ])
        
        # Enable site and restart Nginx
        run_command([
            "ssh", "-i", ssh_key_path, f"{DROPLET_USER}@{DROPLET_IP}",
            "ln -sf /etc/nginx/sites-available/nlp-dashboard /etc/nginx/sites-enabled/ && nginx -t && systemctl restart nginx"
        ])
        
        # Clean up local file
        os.remove("nginx_config")
        
        print_success("Nginx reverse proxy configured")
        return True
        
    except subprocess.CalledProcessError:
        print_error("Failed to set up Nginx")
        return False

def setup_firewall() -> bool:
    """Set up firewall rules"""
    print_status("Setting up firewall...")
    
    ssh_key_path = os.path.expanduser(SSH_KEY_PATH)
    
    try:
        # Allow SSH, HTTP, HTTPS, and the app port
        run_command([
            "ssh", "-i", ssh_key_path, f"{DROPLET_USER}@{DROPLET_IP}",
            "ufw allow ssh && ufw allow 80 && ufw allow 443 && ufw allow {PORT_HOST} && ufw --force enable"
        ])
        
        print_success("Firewall configured")
        return True
        
    except subprocess.CalledProcessError:
        print_error("Failed to configure firewall")
        return False

def wait_for_service() -> bool:
    """Wait for the service to be ready"""
    print_status("Waiting for service to be ready...")
    
    start_time = time.time()
    max_wait_time = 120  # 2 minutes
    attempts = 0
    
    while time.time() - start_time < max_wait_time:
        attempts += 1
        elapsed = time.time() - start_time
        print_status(f"Health check attempt {attempts} (elapsed: {elapsed:.1f}s)")
        
        try:
            response = requests.get(f"http://{DROPLET_IP}:{PORT_HOST}/home", timeout=10)
            if response.status_code == 200:
                total_time = time.time() - start_time
                print_success(f"Service is ready after {total_time:.1f}s!")
                return True
        except requests.RequestException as e:
            print_warning(f"Health check failed: {e}")
        
        remaining = max_wait_time - elapsed
        if remaining > 5:
            print_status(f"Service not ready yet, waiting 5s... (remaining: {remaining:.1f}s)")
            time.sleep(5)
        else:
            break
    
    total_time = time.time() - start_time
    print_error(f"Service health check failed after {total_time:.1f}s")
    return False

def run_remote_tests() -> bool:
    """Run tests on the remote server"""
    print_status("Running remote tests...")
    
    ssh_key_path = os.path.expanduser(SSH_KEY_PATH)
    
    try:
        # Test basic connectivity
        result = run_command([
            "ssh", "-i", ssh_key_path, f"{DROPLET_USER}@{DROPLET_IP}",
            f"curl -f http://localhost:{PORT_HOST}/home"
        ], check=False)
        
        if result.returncode == 0:
            print_success("Basic connectivity test passed")
            return True
        else:
            print_error("Basic connectivity test failed")
            return False
            
    except Exception as e:
        print_error(f"Remote tests failed: {e}")
        return False

def print_deployment_info() -> None:
    """Print deployment information and URLs"""
    print("\n" + "="*60)
    print_success("DROPLET DEPLOYMENT COMPLETE!")
    print("="*60)
    
    print(f"\n{Colors.BOLD}Access URLs:{Colors.END}")
    print(f"  🏠 Homepage: {Colors.GREEN}http://{DROPLET_IP}:{PORT_HOST}/home{Colors.END}")
    print(f"  📊 Analysis: {Colors.GREEN}http://{DROPLET_IP}:{PORT_HOST}/{Colors.END}")
    print(f"  📰 News: {Colors.GREEN}http://{DROPLET_IP}:{PORT_HOST}/news/browse{Colors.END}")
    
    if DOMAIN != "YOUR_DOMAIN.com":
        print(f"  🌐 Domain: {Colors.GREEN}http://{DOMAIN}{Colors.END}")
    
    print(f"\n{Colors.BOLD}Docker Hub Image:{Colors.END}")
    print(f"  Image: {Colors.GREEN}{IMAGE_NAME}{Colors.END}")
    
    print(f"\n{Colors.BOLD}Useful Commands:{Colors.END}")
    print(f"  View logs: {Colors.YELLOW}ssh -i {SSH_KEY_PATH} {DROPLET_USER}@{DROPLET_IP} 'docker logs {CONTAINER_NAME}'{Colors.END}")
    print(f"  Stop container: {Colors.YELLOW}ssh -i {SSH_KEY_PATH} {DROPLET_USER}@{DROPLET_IP} 'docker stop {CONTAINER_NAME}'{Colors.END}")
    print(f"  Restart container: {Colors.YELLOW}ssh -i {SSH_KEY_PATH} {DROPLET_USER}@{DROPLET_IP} 'docker restart {CONTAINER_NAME}'{Colors.END}")
    print(f"  Shell access: {Colors.YELLOW}ssh -i {SSH_KEY_PATH} {DROPLET_USER}@{DROPLET_IP}{Colors.END}")
    
    print("\n" + "="*60)

def main() -> int:
    """Main deployment function"""
    print_status("Starting NLP Dashboard Droplet Deployment")
    print_status("="*50)
    overall_start = time.time()
    
    # Check prerequisites
    print_status("Phase 1/6: Checking prerequisites...")
    if not check_prerequisites():
        return 1
    
    # Set up droplet
    print_status("Phase 2/6: Setting up droplet...")
    if not setup_droplet():
        return 1
    
    # Deploy application
    print_status("Phase 3/6: Deploying application...")
    if not deploy_to_droplet():
        return 1
    
    # Set up firewall
    print_status("Phase 4/6: Setting up firewall...")
    if not setup_firewall():
        print_warning("Firewall setup failed, but continuing...")
    
    # Set up Nginx (optional)
    print_status("Phase 5/6: Configuring Nginx (optional)...")
    setup_nginx = input("Set up Nginx reverse proxy? (y/n): ").lower().strip()
    if setup_nginx == 'y':
        if not setup_nginx_proxy():
            print_warning("Nginx setup failed, but continuing...")
    
    # Wait for service
    print_status("Phase 6/6: Waiting for service to be ready...")
    if not wait_for_service():
        print_error("Service health check failed")
        return 1
    
    # Run remote tests
    print_status("Running final tests...")
    if not run_remote_tests():
        print_warning("Some remote tests failed")
    
    # Print deployment info
    overall_time = time.time() - overall_start
    print_success(f"Total deployment time: {overall_time:.2f}s")
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
