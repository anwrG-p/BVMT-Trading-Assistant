# Deployment Guide

## Docker Deployment (Recommended)

### 1. Build Image

This will build the complete application image including dependencies.

```bash
docker build -t bvmt-forecaster:latest .
```

### 2. Run Container

```bash
docker run -d \
  -p 8000:8000 \
  -p 8501:8501 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/models:/app/models \
  --name bvmt-app \
  bvmt-forecaster:latest
```

### 3. Using Docker Compose

For simpler orchestration of services (if separating frontend/backend in future):

```yaml
version: "3.8"

services:
  app:
    build: .
    ports:
      - "8000:8000"
      - "8501:8501"
    volumes:
      - ./data:/app/data
      - ./models:/app/models
    environment:
      - API_HOST=0.0.0.0
      - API_PORT=8000
    restart: unless-stopped
```

Run with: `docker-compose up -d`

## Environment Variables

| Variable    | Description                     | Default       | Required |
| ----------- | ------------------------------- | ------------- | -------- |
| `API_HOST`  | Host to bind API service        | `0.0.0.0`     | No       |
| `API_PORT`  | Port for API service            | `8000`        | No       |
| `DATA_DIR`  | Path to data directory          | `/app/data`   | No       |
| `MODEL_DIR` | Path to models directory        | `/app/models` | No       |
| `LOG_LEVEL` | Logging verbosity (DEBUG, INFO) | `INFO`        | No       |

## Scaling

- **Horizontal Scaling**: Deploy multiple instances behind a load balancer (Nginx, AWS ALB).
- **Stateless**: The API is stateless, but model files must be present on each instance. Using a shared volume (EFS) or S3 object storage for model artifacts is recommended for scaled deployments.

## Monitoring

- **Health Check**: `GET /health` endpoint returns 200 OK if services are up.
- **Logs**: Application logs are written to stdout/stderr (captured by Docker) and `logs/app.log`.
- **Metrics**: `GET /metrics` provides internal model performance stats.

## Production Checklist

- [ ] SSL/TLS certificate configured (e.g., Let's Encrypt with Nginx).
- [ ] Environment variables set securely.
- [ ] Database backups (if using external DB).
- [ ] Monitoring alerts set up for 5xx errors.
- [ ] Rate limiting enabled at gateway level.
