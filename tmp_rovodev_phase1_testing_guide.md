# Phase 1 Testing Guide - Legal Assistant AI

## 📊 Phase 1 Status: ✅ COMPLETE

All Phase 1 infrastructure components are successfully implemented and running!

---

## ✅ What's Implemented

### 1. **Monorepo Setup** ✅
- Turborepo configured with workspaces
- Root package.json with scripts for all services
- Proper workspace structure (`apps/*`, `packages/*`)

### 2. **Docker Infrastructure** ✅
- PostgreSQL 15 with pgvector extension (port 5434)
- Redis 7 (port 6379)
- MinIO S3-compatible storage (ports 9000, 9001)
- All services with health checks
- Docker Compose configuration for local development

### 3. **Backend (FastAPI)** ✅
- FastAPI application with async support
- Configuration management with Pydantic Settings
- Database session management (SQLAlchemy async)
- CORS middleware configured
- Health check endpoints
- API documentation (Swagger UI)
- Logging setup
- Alembic for migrations (ready to use)

### 4. **Frontend (Next.js)** ✅
- Next.js 14 with App Router
- TypeScript configured
- Tailwind CSS setup
- Basic landing page
- Development server ready

### 5. **Configuration** ✅
- Comprehensive `.env` file
- Environment variables for all services
- Proper defaults for development

---

## 🧪 How to Test Phase 1

### Test 1: Infrastructure Services (Docker)

#### Check All Services are Running
```bash
docker ps --filter "name=legal-assistant"
```
**Expected Output:** 3 services running with "(healthy)" status:
- legal-assistant-postgres
- legal-assistant-redis
- legal-assistant-minio

#### Test PostgreSQL Database
```bash
# Connect to database
docker exec -it legal-assistant-postgres psql -U postgres -d legal_assistant

# Inside psql, run:
\l                          # List databases
\dt                         # List tables (empty for now)
SELECT version();           # Check PostgreSQL version
\q                          # Quit
```
**Expected:** PostgreSQL 15+ with pgvector extension available

#### Test Redis
```bash
docker exec -it legal-assistant-redis redis-cli ping
```
**Expected Output:** `PONG`

#### Test Redis Connection with Data
```bash
docker exec -it legal-assistant-redis redis-cli SET test "Phase1Works"
docker exec -it legal-assistant-redis redis-cli GET test
```
**Expected Output:** `Phase1Works`

#### Test MinIO (S3 Storage)
```bash
# Check health endpoint
curl http://localhost:9000/minio/health/live

# OR visit web console
# URL: http://localhost:9001
# Login: minioadmin / minioadmin
```
**Expected:** Empty 200 OK response for curl, or working web UI

---

### Test 2: Backend API (FastAPI)

#### Check if API is Running
```bash
curl http://localhost:8000/health
```
**Expected Output:** 
```json
{"status":"healthy","version":"0.1.0"}
```

#### Test Readiness Check
```bash
curl http://localhost:8000/health/ready
```
**Expected Output:**
```json
{"status":"ready"}
```

#### Test API Documentation
Open in browser: http://localhost:8000/docs

**Expected:** Swagger UI interface showing:
- Health check endpoints
- API documentation
- Interactive API testing interface

#### Test Configuration Loading
```bash
cd apps/api
source venv/bin/activate
python -c "from src.config import settings; print(f'✅ App: {settings.APP_NAME}'); print(f'✅ CORS: {settings.CORS_ORIGINS}')"
```
**Expected Output:**
```
✅ App: Legal Assistant AI
✅ CORS: ['http://localhost:3000', 'http://localhost:3001']
```

#### Test Database Connection
```bash
cd apps/api
source venv/bin/activate
python -c "from src.db.session import engine; import asyncio; asyncio.run(engine.connect().aclose()); print('✅ Database connection successful')"
```
**Expected:** No errors, connection successful message

---

### Test 3: Frontend (Next.js)

#### Start Frontend (if not running)
```bash
cd apps/web
npm run dev
```

#### Test Frontend in Browser
Open: http://localhost:3000

**Expected:** Landing page showing:
- "Legal Assistant AI" heading
- "AI-powered legal document assistant" subtitle
- Clean, centered layout

#### Test Frontend Build
```bash
cd apps/web
npm run build
```
**Expected:** Successful build with no errors

---

### Test 4: Database Migrations (Alembic)

#### Check Alembic Configuration
```bash
cd apps/api
source venv/bin/activate
alembic current
```
**Expected:** Shows current migration state (likely empty/base for now)

#### Test Migration Creation (Dry Run)
```bash
alembic history
```
**Expected:** Empty list or shows existing migrations

#### Verify Migration Path
```bash
ls -la alembic/versions/
```
**Expected:** Empty directory (no migrations yet - normal for Phase 1)

---

### Test 5: Turborepo Workspace Commands

#### Test Lint (from root)
```bash
npm run lint
```
**Expected:** Linting runs for all apps

#### Test Docker Commands (from root)
```bash
# View logs
npm run docker:logs

# Check status
docker-compose -f infrastructure/docker/docker-compose.dev.yml ps
```
**Expected:** All services running and healthy

---

## 🎯 Quick Integration Test

Run this comprehensive test script:

```bash
#!/bin/bash
echo "=== Phase 1 Integration Test ==="

# Test 1: Docker Services
echo -e "\n✓ Testing Docker services..."
docker ps --filter "name=legal-assistant" --format "{{.Names}}: {{.Status}}" | grep healthy
if [ $? -eq 0 ]; then echo "✅ Docker services healthy"; else echo "❌ Docker services issue"; fi

# Test 2: Database
echo -e "\n✓ Testing PostgreSQL..."
docker exec legal-assistant-postgres psql -U postgres -d legal_assistant -c "SELECT 1" > /dev/null 2>&1
if [ $? -eq 0 ]; then echo "✅ PostgreSQL connection OK"; else echo "❌ PostgreSQL connection failed"; fi

# Test 3: Redis
echo -e "\n✓ Testing Redis..."
docker exec legal-assistant-redis redis-cli ping | grep PONG > /dev/null
if [ $? -eq 0 ]; then echo "✅ Redis connection OK"; else echo "❌ Redis connection failed"; fi

# Test 4: MinIO
echo -e "\n✓ Testing MinIO..."
curl -s http://localhost:9000/minio/health/live > /dev/null
if [ $? -eq 0 ]; then echo "✅ MinIO connection OK"; else echo "❌ MinIO connection failed"; fi

# Test 5: Backend API
echo -e "\n✓ Testing Backend API..."
curl -s http://localhost:8000/health | grep healthy > /dev/null
if [ $? -eq 0 ]; then echo "✅ Backend API healthy"; else echo "❌ Backend API issue"; fi

# Test 6: Frontend
echo -e "\n✓ Testing Frontend..."
curl -s http://localhost:3000 > /dev/null 2>&1
if [ $? -eq 0 ]; then echo "✅ Frontend accessible"; else echo "⚠️  Frontend not running (start with: cd apps/web && npm run dev)"; fi

echo -e "\n=== Phase 1 Test Complete ==="
```

Save this as `test_phase1.sh`, make it executable, and run:
```bash
chmod +x test_phase1.sh
./test_phase1.sh
```

---

## 🐛 Fixed Issues

During testing, I fixed the following issues:

### Issue 1: Missing Pydantic Settings Import
**Problem:** `config.py` had type annotation issues with list fields  
**Fix:** Updated field validators to properly handle comma-separated env vars

### Issue 2: CORS_ORIGINS Type Validation
**Problem:** Pydantic was trying to validate string as list before field validators ran  
**Fix:** Changed type to `Any` and added proper field validators

---

## 📝 Current Service Status

- ✅ **PostgreSQL**: Running on port 5434 (healthy)
- ✅ **Redis**: Running on port 6379 (healthy)
- ✅ **MinIO**: Running on ports 9000/9001 (healthy)
- ✅ **Backend API**: Running on port 8000
- ✅ **Frontend**: Can start on port 3000

---

## 🚀 Next Steps (Phase 2)

Phase 1 is complete! You're ready to move on to **Phase 2: Authentication System**

Phase 2 will include:
- User registration and login endpoints
- JWT token generation and validation
- Password hashing with bcrypt
- Protected route middleware
- User model and database migrations
- Login/Register UI components

---

## 📚 Additional Resources

### Useful URLs
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **MinIO Console**: http://localhost:9001 (minioadmin/minioadmin)

### Quick Reference Commands
```bash
# Start all infrastructure
npm run docker:up

# Stop all infrastructure
npm run docker:down

# Start backend
cd apps/api && source venv/bin/activate && uvicorn src.main:app --reload

# Start frontend
cd apps/web && npm run dev

# View logs
npm run docker:logs

# Create migration
cd apps/api && alembic revision --autogenerate -m "description"

# Run migrations
cd apps/api && alembic upgrade head
```

---

## ✅ Phase 1 Checklist

- [x] Monorepo setup with Turborepo
- [x] Docker Compose with PostgreSQL, Redis, MinIO
- [x] FastAPI backend with health endpoints
- [x] Next.js frontend with basic landing page
- [x] Configuration management (.env)
- [x] Database session management
- [x] Alembic migrations setup
- [x] CORS configuration
- [x] Logging setup
- [x] API documentation (Swagger)
- [x] All services running and healthy

**Phase 1 Status: 100% COMPLETE** 🎉
