# BudgetWise Docker Setup

## Quick Start

### Prerequisites
- Docker Desktop installed and running
- `.env` file configured with required credentials

### Start All Services

```bash
# Build and start all services
docker-compose up --build

# Or run in detached mode (background)
docker-compose up -d --build
```

### Stop All Services

```bash
# Stop services (keeps containers)
docker-compose stop

# Stop and remove containers
docker-compose down

# Stop, remove containers, and clean up volumes
docker-compose down -v
```

## Service URLs

Once running, access services at:

- 🔐 **Auth Service**: http://localhost:8001
  - API Docs: http://localhost:8001/docs

- 📊 **Ranking System**: http://localhost:8002
  - API Docs: http://localhost:8002/docs

- 💰 **Budget Engine**: http://localhost:8003
  - API Docs: http://localhost:8003/docs

- 🤖 **AI Pipeline**: http://localhost:8004
  - API Docs: http://localhost:8004/docs

## Useful Commands

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f auth-service
docker-compose logs -f ranking-system
docker-compose logs -f budget-engine
docker-compose logs -f ai-pipeline
```

### Rebuild a Specific Service

```bash
docker-compose up -d --build auth-service
```

### Check Service Status

```bash
docker-compose ps
```

### Execute Commands in Container

```bash
# Open shell in a container
docker-compose exec auth-service /bin/bash

# Run Python in container
docker-compose exec budget-engine python
```

### Health Checks

```bash
# Auth Service
curl http://localhost:8001/health

# Ranking System
curl http://localhost:8002/health

# Budget Engine
curl http://localhost:8003/health

# AI Pipeline
curl http://localhost:8004/health
```

## Architecture

```
┌─────────────────────────────────────────────────┐
│         Docker Network: budgetwise-network      │
│                                                 │
│  ┌─────────────┐  ┌─────────────┐             │
│  │Auth Service │  │  Ranking    │             │
│  │  Port 8001  │  │  System     │             │
│  └─────────────┘  │  Port 8002  │             │
│                   └──────┬──────┘             │
│                          │                     │
│                   ┌──────▼──────┐             │
│                   │   Budget    │             │
│                   │   Engine    │             │
│                   │  Port 8003  │             │
│                   └──────┬──────┘             │
│                          │                     │
│                   ┌──────▼──────┐             │
│                   │AI Pipeline  │             │
│                   │  Port 8004  │             │
│                   └─────────────┘             │
└─────────────────────────────────────────────────┘
```

## Environment Variables

Required in `.env`:
- `SUPABASE_URL` - Your Supabase project URL
- `SUPABASE_KEY` - Your Supabase anon key
- `OPENAI_API_KEY` - OpenAI API key for AI features

Optional:
- `ELEVENLABS_API_KEY` - For text-to-speech features
- `ELEVENLABS_VOICE_ID` - Voice ID (default: Rachel)
- `ENVIRONMENT` - development/production (default: development)

## Troubleshooting

### Port Already in Use

If you get a port conflict error:

```bash
# Stop conflicting services
docker-compose down

# Or change ports in docker-compose.yml
```

### Build Errors

```bash
# Clean rebuild
docker-compose down
docker-compose build --no-cache
docker-compose up
```

### Check Container Logs

```bash
# See what's failing
docker-compose logs auth-service
```

### Network Issues Between Services

Services communicate using Docker's internal network. Use service names as hostnames:
- `http://auth-service:8001`
- `http://ranking-system:8002`
- `http://budget-engine:8003`
- `http://ai-pipeline:8004`

## Development Workflow

1. **Make code changes** in your editor
2. **Rebuild affected service**:
   ```bash
   docker-compose up -d --build <service-name>
   ```
3. **View logs**:
   ```bash
   docker-compose logs -f <service-name>
   ```

## Production Deployment

For production, consider:

1. **Remove `restart: unless-stopped`** and use an orchestrator
2. **Add resource limits**:
   ```yaml
   deploy:
     resources:
       limits:
         cpus: '1'
         memory: 1G
   ```
3. **Use secrets management** instead of `.env` files
4. **Enable HTTPS** with a reverse proxy (nginx/traefik)
5. **Set `ENVIRONMENT=production`** in your `.env`

## Next Steps

- [ ] Set up API Gateway for unified entry point
- [ ] Add Redis for caching
- [ ] Set up monitoring (Prometheus/Grafana)
- [ ] Configure CI/CD pipeline
- [ ] Add database migrations management
