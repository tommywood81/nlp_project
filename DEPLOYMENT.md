# NLP Dashboard Deployment Guide

This guide explains how to deploy the NLP Dashboard using different methods.

## Prerequisites

1. **Docker Desktop** installed and running
2. **Docker Hub account** and logged in (`docker login`)
3. **SSH key** for droplet access (for cloud deployment)
4. **Digital Ocean droplet** (for cloud deployment)

## Deployment Options

### Option 1: Local Deployment (Recommended for Development)

Deploy locally using Docker Desktop and Docker Hub:

```bash
python deploy_local_docker_hub.py
```

This will:
- Build the Docker image locally
- Push it to Docker Hub
- Pull it back and run locally
- Run tests and health checks

### Option 2: Cloud Deployment (Production)

Deploy to Digital Ocean droplet:

```bash
python deploy_droplet.py
```

This will:
- Connect to your droplet via SSH
- Install Docker if needed
- Pull the image from Docker Hub
- Run the container
- Set up firewall and optional Nginx

### Option 3: Complete Workflow

Orchestrate the entire process (local build + cloud deploy):

```bash
python deploy_workflow.py
```

This combines both local and cloud deployment in one script.

### Option 4: Push Only

Just build and push to Docker Hub (useful for CI/CD):

```bash
python push_to_dockerhub.py
```

## Configuration

### Docker Hub Configuration

Update the Docker Hub username in the deployment scripts:

```python
DOCKER_HUB_USERNAME = "your-username"
```

### Droplet Configuration

Update the droplet settings in `deploy_droplet.py`:

```python
DROPLET_IP = "your-droplet-ip"
DROPLET_USER = "root"
SSH_KEY_PATH = "path/to/your/ssh/key"
```

## Step-by-Step Deployment

### 1. Local Development Setup

```bash
# 1. Login to Docker Hub
docker login

# 2. Deploy locally
python deploy_local_docker_hub.py
```

### 2. Production Deployment

```bash
# 1. Push image to Docker Hub
python push_to_dockerhub.py

# 2. Deploy to droplet
python deploy_droplet.py
```

### 3. Complete Workflow

```bash
# Single command for full deployment
python deploy_workflow.py
```

## Access URLs

After deployment, your application will be available at:

- **Local**: `http://localhost:8001`
- **Droplet**: `http://your-droplet-ip:8001`

## Troubleshooting

### Docker Issues

1. **Docker not running**: Start Docker Desktop
2. **Not logged in**: Run `docker login`
3. **Permission issues**: Ensure Docker Desktop is running

### SSH Issues

1. **SSH key not found**: Check the path in `deploy_droplet.py`
2. **Connection refused**: Verify droplet IP and firewall settings
3. **Permission denied**: Ensure SSH key has correct permissions

### Container Issues

1. **Container won't start**: Check logs with `docker logs container-name`
2. **Port conflicts**: Change `PORT_HOST` in configuration
3. **Health check fails**: Wait longer or check application logs

## Useful Commands

### Local Docker Commands

```bash
# View logs
docker logs nlp-dashboard-container

# Stop container
docker stop nlp-dashboard-container

# Remove container
docker rm nlp-dashboard-container

# Shell access
docker exec -it nlp-dashboard-container /bin/bash
```

### Remote Commands

```bash
# SSH to droplet
ssh -i /path/to/key root@your-droplet-ip

# View container logs
docker logs nlp-dashboard-container

# Restart container
docker restart nlp-dashboard-container

# Check container status
docker ps
```

## Security Considerations

1. **SSH Keys**: Use strong SSH keys and keep them secure
2. **Firewall**: The deployment script sets up basic firewall rules
3. **Docker Images**: Only pull from trusted sources (your own Docker Hub)
4. **Ports**: Use non-standard ports to avoid conflicts

## Performance Tips

1. **Image Size**: The light Dockerfile reduces image size
2. **Caching**: Docker layers are cached for faster builds
3. **Health Checks**: Built-in health checks ensure service availability
4. **Restart Policy**: Container automatically restarts on failure

## Monitoring

The deployment includes:
- Health checks during startup
- Integration tests
- Container status monitoring
- Log output for debugging

## Support

If you encounter issues:
1. Check the logs: `docker logs container-name`
2. Verify configuration in the deployment scripts
3. Ensure all prerequisites are met
4. Check network connectivity for cloud deployment
