---
name: docker-manager
description: Manage Docker containers, images, and networks via the `docker` CLI. List, start, stop, inspect containers and view logs.
metadata:
  openclaw:
    emoji: 🐳
    requires:
      bins:
        - docker
    install:
      - id: homebrew
        kind: brew
        formula: docker
        bins:
          - docker
        label: "Install Docker Desktop (brew)"
      - id: linux
        kind: apt
        package: docker.io
        bins:
          - docker
        label: "Install Docker (apt)"
---

## Purpose

Manage Docker containers and images directly from OpenClaw. Start, stop, inspect, and debug containerized applications without leaving your workflow.

## When to Use

- Start/stop containers for local development
- View container logs and debug runtime issues
- Execute commands inside running containers
- List and inspect container/image details
- Monitor container resource usage
- Manage container networking and volumes

## When Not to Use

- Production workload orchestration (use Kubernetes instead)
- Complex container builds (prefer Docker Compose for multi-container setups)
- Without understanding the impact of stopping containers

## Setup

### Prerequisites

- Docker installed and running
- User has Docker permissions (in docker group on Linux)

### Installation

**macOS (Homebrew):**
```bash
brew install docker docker-compose
# Start Docker Desktop app
```

**Linux (apt):**
```bash
sudo apt-get install docker.io docker-compose
sudo usermod -aG docker $USER
# Log out and back in
```

**Windows:**
Download Docker Desktop from https://www.docker.com/products/docker-desktop

### Verify Installation

```bash
docker --version
docker run hello-world
```

## Commands

### List Containers

Show all or running containers:

```bash
docker-manager list                    # All containers (running and stopped)
docker-manager list --running          # Only running
docker-manager list --all --format json  # JSON output
```

**Use case**: Find container IDs, see status, uptime

### Inspect Container

Get detailed information about a container:

```bash
docker-manager inspect <container-id-or-name>
docker-manager inspect <container-name> --env     # Show environment variables
docker-manager inspect <container-name> --mounts  # Show volume mounts
docker-manager inspect <container-name> --network # Show network config
```

**Use case**: Debug container configuration, find exposed ports

### Start/Stop Container

Control container state:

```bash
docker-manager start <container-name>
docker-manager stop <container-name>
docker-manager restart <container-name>
docker-manager kill <container-name>   # Force stop (SIGKILL)
```

**Use case**: Manage services during development

### View Logs

Stream or retrieve container logs:

```bash
docker-manager logs <container-name>
docker-manager logs <container-name> --tail 50        # Last 50 lines
docker-manager logs <container-name> --follow         # Stream live logs
docker-manager logs <container-name> --since "5m"     # Last 5 minutes
docker-manager logs <container-name> --timestamps     # With timestamps
```

**Use case**: Debug errors, monitor application output

### Execute Command

Run a command in a running container:

```bash
docker-manager exec <container-name> ls -la /app
docker-manager exec <container-name> curl http://localhost:3000
docker-manager exec <container-name> bash  # Interactive shell
docker-manager exec --user postgres <container-name> psql --version
```

**Use case**: Inspect container internals, run one-off commands

### Container Stats

Monitor resource usage:

```bash
docker-manager stats <container-name>
docker-manager stats --no-stream  # Single snapshot
```

**Use case**: Check CPU, memory, network usage

### Remove Container/Image

Clean up unused containers or images:

```bash
docker-manager remove <container-name>
docker-manager remove --image <image-name>
docker-manager prune              # Remove all stopped containers
docker-manager prune --images      # Remove unused images
```

**Use case**: Reclaim disk space, clean development environment

## Examples

### Example 1: Debug a Failing Web Service

```bash
# Find the container
docker-manager list --running | grep web

# Check its status
docker-manager inspect my-app-web

# View recent logs
docker-manager logs my-app-web --tail 100 --follow

# Check if a port is open
docker-manager exec my-app-web curl http://localhost:8000/health
```

### Example 2: Restart Services After Code Change

```bash
# Update code, rebuild container, restart
docker-manager restart api-service
docker-manager restart db-service

# Verify they're running
docker-manager list --running
sleep 2
docker-manager exec api-service curl http://localhost:3000/api/status
```

### Example 3: Monitor Resource Usage During Load Testing

```bash
# Start monitoring
docker-manager stats api-server

# In another terminal, run load test
ab -n 1000 -c 10 http://localhost:8080/api/endpoint

# Watch CPU/memory spike in stats output
```

### Example 4: Inspect Database Container Configuration

```bash
# Find postgres container
docker-manager list | grep postgres

# View all details
docker-manager inspect postgres-db

# View just environment variables (includes DB name, user)
docker-manager inspect postgres-db --env

# View mounted volumes
docker-manager inspect postgres-db --mounts

# Connect to it
docker-manager exec -it postgres-db psql -U postgres -d mydb
```

### Example 5: Mass Stop All Containers

```bash
# Gracefully stop all running containers
docker-manager list --running | xargs -I {} docker-manager stop {}

# Or force kill if needed
docker-manager list --running | xargs -I {} docker-manager kill {}

# Verify all stopped
docker-manager list
```

### Example 6: Check Application Logs for Errors

```bash
# Get last 500 lines with errors highlighted
docker-manager logs my-app --tail 500 | grep -i error

# Stream logs and filter
docker-manager logs my-app --follow | grep -i "WARN\|ERROR"

# Get logs from last hour
docker-manager logs my-app --since 1h --timestamps
```

## Common Workflows

### Local Development

```bash
# Start all services (from docker-compose.yml)
docker-compose up -d

# View logs of a specific service
docker-manager logs web-service --follow

# Execute database migration
docker-manager exec app-db ./migrate.sh

# Stop everything
docker-compose down
```

### Debugging

```bash
# Get container ID
ID=$(docker-manager list | grep app | awk '{print $1}')

# Interactive shell into container
docker-manager exec -it $ID /bin/bash

# Inside container: explore filesystem, check env vars, test connectivity
# exit
```

### Health Checks

```bash
# Check if service responds
docker-manager exec api-server curl -f http://localhost:8000/health

# View memory usage
docker-manager stats api-server --no-stream

# Check logs for errors
docker-manager logs api-server | tail -20
```

## Environment Variables in Containers

View environment variables passed to a container:

```bash
docker-manager exec <container> env
docker-manager inspect <container> --env | grep "MY_VAR"
```

## Docker CLI Reference

The `docker-manager` skill is a wrapper around the Docker CLI:

```bash
docker ps -a                    # All containers
docker logs <id>               # View logs
docker exec -it <id> bash      # Interactive shell
docker stats                   # Resource usage
docker inspect <id>            # Full details
docker start/stop/restart <id> # Control
```

## Notes

- Container names and IDs are interchangeable in most commands
- Logs are retained after container stops (unless you remove the container)
- Stopping a container doesn't delete it; use `remove` to delete
- Exec commands run with the container's user by default (often root)
- Use `--interactive --tty` flags for interactive commands like bash
- Consider using `docker-compose` for multi-container environments with networking/volumes
