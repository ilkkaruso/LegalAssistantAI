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

# Test 6: Backend API Docs
echo -e "\n✓ Testing API Documentation..."
curl -s http://localhost:8000/docs | grep swagger > /dev/null
if [ $? -eq 0 ]; then echo "✅ API docs accessible at http://localhost:8000/docs"; else echo "❌ API docs issue"; fi

# Test 7: Frontend
echo -e "\n✓ Testing Frontend..."
curl -s http://localhost:3000 > /dev/null 2>&1
if [ $? -eq 0 ]; then echo "✅ Frontend accessible at http://localhost:3000"; else echo "⚠️  Frontend not running (start with: cd apps/web && npm run dev)"; fi

# Test 8: Configuration
echo -e "\n✓ Testing Backend Configuration..."
cd apps/api
source venv/bin/activate 2>/dev/null
python -c "from src.config import settings; print('✅ Configuration loads successfully')" 2>/dev/null
if [ $? -eq 0 ]; then echo "✅ Backend config OK"; else echo "❌ Backend config issue"; fi
cd ../..

echo -e "\n=== Phase 1 Test Complete ===\n"
echo "📊 Summary:"
echo "  - Docker Infrastructure: PostgreSQL, Redis, MinIO"
echo "  - Backend API: FastAPI with health endpoints"
echo "  - Frontend: Next.js (start if needed)"
echo "  - Config: Environment variables loaded"
echo ""
echo "🎯 Next: Start Phase 2 (Authentication System)"
