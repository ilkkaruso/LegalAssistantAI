#!/bin/bash
set -e

echo "🚀 Setting up Legal Assistant AI development environment..."
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Check prerequisites
echo -e "${BLUE}Checking prerequisites...${NC}"
command -v docker >/dev/null 2>&1 || { echo "❌ Docker required but not installed. Please install Docker."; exit 1; }
command -v node >/dev/null 2>&1 || { echo "❌ Node.js required but not installed. Please install Node.js 18+."; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "❌ Python 3 required but not installed. Please install Python 3.11+."; exit 1; }
echo -e "${GREEN}✓ All prerequisites found${NC}"
echo ""

# 2. Copy environment variables
echo -e "${BLUE}Setting up environment variables...${NC}"
if [ ! -f .env ]; then
    cp .env.example .env
    echo -e "${GREEN}✓ Created .env file${NC}"
    echo -e "${YELLOW}⚠️  Please update .env with your actual credentials, especially:${NC}"
    echo "   - ANTHROPIC_API_KEY"
    echo "   - JWT_SECRET_KEY (generate a secure random string)"
    echo ""
    read -p "Press Enter to continue after updating .env file..."
else
    echo -e "${GREEN}✓ .env file already exists${NC}"
fi
echo ""

# 3. Install root dependencies
echo -e "${BLUE}Installing root workspace dependencies...${NC}"
npm install
echo -e "${GREEN}✓ Root dependencies installed${NC}"
echo ""

# 4. Install frontend dependencies
echo -e "${BLUE}Installing frontend dependencies...${NC}"
cd apps/web
npm install
cd ../..
echo -e "${GREEN}✓ Frontend dependencies installed${NC}"
echo ""

# 5. Setup Python backend
echo -e "${BLUE}Setting up Python backend...${NC}"
cd apps/api

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✓ Created Python virtual environment${NC}"
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements/dev.txt
echo -e "${GREEN}✓ Python dependencies installed${NC}"

cd ../..
echo ""

# 6. Start infrastructure services
echo -e "${BLUE}Starting infrastructure services (PostgreSQL, Redis, MinIO)...${NC}"
docker-compose -f infrastructure/docker/docker-compose.dev.yml up -d

echo -e "${YELLOW}Waiting for services to be ready...${NC}"
sleep 15

# Check if services are healthy
docker-compose -f infrastructure/docker/docker-compose.dev.yml ps
echo -e "${GREEN}✓ Infrastructure services started${NC}"
echo ""

# 7. Run database migrations
echo -e "${BLUE}Running database migrations...${NC}"
cd apps/api
source venv/bin/activate
alembic upgrade head
cd ../..
echo -e "${GREEN}✓ Database migrations complete${NC}"
echo ""

# 8. Create logs directory
mkdir -p logs
echo -e "${GREEN}✓ Created logs directory${NC}"
echo ""

echo "════════════════════════════════════════════════════════"
echo -e "${GREEN}✅ Setup complete!${NC}"
echo "════════════════════════════════════════════════════════"
echo ""
echo "To start development:"
echo ""
echo -e "${BLUE}Terminal 1 - Backend API:${NC}"
echo "  cd apps/api"
echo "  source venv/bin/activate"
echo "  uvicorn src.main:app --reload"
echo ""
echo -e "${BLUE}Terminal 2 - Frontend:${NC}"
echo "  cd apps/web"
echo "  npm run dev"
echo ""
echo -e "${BLUE}Terminal 3 - Celery Worker (optional, for background tasks):${NC}"
echo "  cd apps/api"
echo "  source venv/bin/activate"
echo "  celery -A src.tasks.celery_app worker --loglevel=info"
echo ""
echo "Services:"
echo "  Frontend:        http://localhost:3000"
echo "  Backend API:     http://localhost:8000"
echo "  API Docs:        http://localhost:8000/docs"
echo "  MinIO Console:   http://localhost:9001 (minioadmin/minioadmin)"
echo "  PostgreSQL:      localhost:5432 (postgres/postgres)"
echo "  Redis:           localhost:6379"
echo ""
echo "To stop infrastructure services:"
echo "  docker-compose -f infrastructure/docker/docker-compose.dev.yml down"
echo ""
