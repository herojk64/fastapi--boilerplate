# Docker Deployment Guide

## Quick Start

### Production Deployment

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

Access the application:
- API: http://localhost:8080 (via Nginx)
- Direct API: http://localhost:3000
- Docs: http://localhost:8080/docs
- Public files: http://localhost:8080/storage/
- PostgreSQL: localhost:5433

### Development Mode

```bash
# Start with hot-reload
docker-compose -f docker-compose.dev.yml up

# Run migrations manually
docker-compose exec app alembic upgrade head

# Access shell
docker-compose exec app bash
```

## Services

### 1. PostgreSQL (postgres)
- **Port**: 5432
- **Database**: fastapi_boilerplate
- **Credentials**: Set via .env file

### 2. FastAPI App (app)
- **Port**: 3000 (internal), 80 (via Nginx)
- **Workers**: 4 (production)
- **Health Check**: http://localhost/health

### 3. Nginx (nginx)
- **Port**: 80 (HTTP), 443 (HTTPS)
- **Static Files**: /storage/ served directly
- **API Proxy**: All /api/* routes proxied to FastAPI

## Configuration

### Environment Variables

Copy `.env.docker` to `.env` and update:

```bash
cp .env.docker .env
```

Key variables:
- `DB_USER`, `DB_PASSWORD`, `DB_NAME` - Database credentials
- `SECRET_KEY` - JWT secret (generate with `openssl rand -hex 32`)
- `ADMIN_EMAIL`, `ADMIN_PASSWORD` - Initial admin user
- `ACCEPTED_ORIGINS` - CORS allowed origins

### Supervisord

The app container uses Supervisord to manage processes:
1. **migrations** - Runs `alembic upgrade head` on startup (priority 1)
2. **fastapi** - Starts Uvicorn with 4 workers (priority 2)

Logs are stored in `/app/logs/`:
- `supervisord.log` - Supervisor main log
- `migrations.log` - Alembic migration logs
- `fastapi.log` - Application logs

## Nginx Configuration

### Static Files
Public files in `storage/public/` are served directly by Nginx at `/storage/`

### API Proxy
All API requests are proxied to the FastAPI app with:
- Connection pooling
- WebSocket support
- 60s timeouts
- Gzip compression

### SSL/HTTPS Setup

1. Add SSL certificates to `nginx/ssl/`
2. Uncomment HTTPS server block in `nginx/nginx.conf`
3. Update `server_name` with your domain
4. Restart Nginx:

```bash
docker-compose restart nginx
```

## Database Management

### Backup

```bash
docker-compose exec postgres pg_dump -U postgres fastapi_boilerplate > backup.sql
```

### Restore

```bash
docker-compose exec -T postgres psql -U postgres fastapi_boilerplate < backup.sql
```

### Migrations

```bash
# Create new migration
docker-compose exec app alembic revision --autogenerate -m "description"

# Apply migrations
docker-compose exec app alembic upgrade head

# Rollback
docker-compose exec app alembic downgrade -1
```

## Scaling

### Horizontal Scaling (Multiple Workers)

Update `docker-compose.yml`:

```yaml
app:
  deploy:
    replicas: 3
```

### Load Balancing

Nginx automatically load balances to multiple app replicas.

## Monitoring

### Health Check

```bash
curl http://localhost/health
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f app

# Supervisord logs
docker-compose exec app tail -f /app/logs/fastapi.log
```

### Resource Usage

```bash
docker stats
```

## Troubleshooting

### App won't start
```bash
# Check logs
docker-compose logs app

# Check migrations
docker-compose exec app alembic current

# Restart services
docker-compose restart
```

### Database connection issues
```bash
# Check postgres health
docker-compose exec postgres pg_isready -U postgres

# Test connection
docker-compose exec app psql -h postgres -U postgres -d fastapi_boilerplate
```

### Permission issues
```bash
# Fix storage permissions
docker-compose exec app chmod -R 755 /app/storage
```

## Production Checklist

- [ ] Change `SECRET_KEY` to secure random value
- [ ] Update `ADMIN_PASSWORD` to strong password
- [ ] Configure proper `ACCEPTED_ORIGINS`
- [ ] Set up SSL certificates for HTTPS
- [ ] Configure backup strategy for database
- [ ] Set up log rotation
- [ ] Configure monitoring (Sentry, Prometheus, etc.)
- [ ] Use Docker secrets for sensitive data
- [ ] Set resource limits in docker-compose.yml
- [ ] Review and harden Nginx configuration

## Cloud Deployment

### AWS ECS
Use the provided `Dockerfile` with ECS task definitions

### Google Cloud Run
Works out of the box, set environment variables in Cloud Run console

### DigitalOcean App Platform
Use `Dockerfile` deployment method

### Traditional VPS
```bash
# Install Docker & Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Clone and deploy
git clone <your-repo>
cd <your-repo>
cp .env.docker .env
# Edit .env with production values
docker-compose up -d
```
