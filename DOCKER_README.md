# BudgetWise Docker Setup

## Quick Start

### 1. Ensure .env file exists
Make sure you have a `.env` file in the project root with:
```env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
OPENAI_API_KEY=your_openai_key
```

### 2. Build and run all services
```bash
docker-compose up --build
```

This starts all 4 backend services:
- **Auth Service**: http://localhost:8001
- **Ranking System**: http://localhost:8002
- **Budget Engine**: http://localhost:8003
- **AI Pipeline**: http://localhost:8004

### 3. View logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f ai-pipeline
```

### 4. Stop all services
```bash
docker-compose down
```

---

## Service Configuration

### Fail-Fast Behavior
- **No health checks**: Services don't waste resources on health polling
- **`restart: "no"`**: If a service crashes, it stays down (fail fast)
- **Exit on error**: Python errors will kill the container immediately

### Hot Reload
- Code changes in `src/backend/` automatically reload services
- Mounted as read-only volume for safety

### Inter-Service Communication
- Services communicate via Docker network: `budgetwise-network`
- Use service names as hostnames (e.g., `http://budget-engine:8003`)

---

## Troubleshooting

### Service won't start
Check logs:
```bash
docker-compose logs [service-name]
```

### Database connection issues
Verify `.env` has correct Supabase credentials

### Port conflicts
Stop services using ports 8001-8004:
```bash
# Windows
netstat -ano | findstr ":8001"
taskkill /PID <pid> /F

# Linux/Mac
lsof -ti:8001 | xargs kill -9
```

### Clean rebuild
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up
```

---

## Development Workflow

1. **Start services**: `docker-compose up`
2. **Make code changes** in `src/backend/`
3. **Services auto-reload** (watch logs)
4. **If error occurs**, service dies → check logs → fix → restart

---

## Why Docker?

✅ **Clean imports** - No Python cache issues
✅ **Isolated environment** - Each service has own container
✅ **Consistent setup** - Works same on all machines
✅ **Easy debugging** - Clear separation of services
✅ **Fail fast** - Errors kill process immediately

---

## API Documentation

Once running, access Swagger docs:
- Auth: http://localhost:8001/docs
- Ranking: http://localhost:8002/docs
- Budget: http://localhost:8003/docs
- AI: http://localhost:8004/docs
