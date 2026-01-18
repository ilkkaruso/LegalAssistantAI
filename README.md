# Legal Assistant AI

AI-powered legal document assistant with conversational AI, legal research capabilities, and workflow automation.

## Features

### Core AI Capabilities (MVP)
- **AI Assistant**: Conversational AI that answers questions about internal/external documents with source citations across any language
- **Document Q&A**: Upload legal documents and ask questions in natural language
- **Source Citations**: All AI responses include verifiable citations to source documents
- **Multi-language Support**: Query documents in any language

### Planned Features (Post-MVP)
- **Legal Research**: Agentic AI searching across document management systems and legal databases
- **Workflows**: Automated multi-step legal task completion
- **Tabular Review**: Transform document folders into interactive grids for analysis
- **Word Add-in**: Microsoft Word integration for in-document AI assistance

## Tech Stack

### Frontend
- **Next.js 14** with App Router
- **TypeScript** & **React 18**
- **Tailwind CSS** with shadcn/ui components
- **Zustand** for state management
- **React Query** for server state
- **Axios** for API client

### Backend
- **FastAPI** (Python 3.11+)
- **PostgreSQL 15+** with **pgvector** extension
- **Redis** for caching and job queues
- **SQLAlchemy 2.0** (async ORM)
- **Alembic** for database migrations

### AI/ML
- **Anthropic Claude API** (Claude 3.5 Sonnet)
- **LangChain** & **LangGraph** for AI orchestration
- **sentence-transformers** for embeddings
- **Unstructured.io** for document processing

### Infrastructure
- **Docker** & **Docker Compose** for local development
- **MinIO** (S3-compatible) for document storage
- **Celery** for background task processing
- **Turborepo** for monorepo management

## Prerequisites

- **Node.js** 18+ and npm 9+
- **Python** 3.11+
- **Docker** and Docker Compose
- **Anthropic API Key** ([Get one here](https://console.anthropic.com/))

## Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd LegalAssistantAI
```

### 2. Run Setup Script

```bash
./scripts/setup-dev.sh
```

This script will:
- Check prerequisites
- Install dependencies
- Start infrastructure services (PostgreSQL, Redis, MinIO)
- Run database migrations
- Set up environment variables

### 3. Configure Environment Variables

Update `.env` with your credentials:

```env
# Required
ANTHROPIC_API_KEY=your-anthropic-api-key-here
JWT_SECRET_KEY=generate-a-secure-random-string-min-32-chars

# Optional (defaults are provided)
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/legal_assistant
REDIS_URL=redis://localhost:6379/0
S3_ENDPOINT=http://localhost:9000
```

### 4. Start Development Servers

**Terminal 1 - Backend API:**
```bash
cd apps/api
source venv/bin/activate
uvicorn src.main:app --reload
```

**Terminal 2 - Frontend:**
```bash
cd apps/web
npm run dev
```

**Terminal 3 - Celery Worker (optional):**
```bash
cd apps/api
source venv/bin/activate
celery -A src.tasks.celery_app worker --loglevel=info
```

### 5. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **MinIO Console**: http://localhost:9001 (minioadmin/minioadmin)

## Project Structure

```
LegalAssistantAI/
├── apps/
│   ├── web/                  # Next.js frontend
│   │   ├── src/
│   │   │   ├── app/         # App router pages
│   │   │   ├── components/  # React components
│   │   │   ├── lib/         # Utilities, API clients, stores
│   │   │   └── types/       # TypeScript types
│   │   └── package.json
│   │
│   └── api/                 # FastAPI backend
│       ├── src/
│       │   ├── api/         # API routes
│       │   ├── core/        # Core utilities (auth, logging)
│       │   ├── models/      # SQLAlchemy models
│       │   ├── schemas/     # Pydantic schemas
│       │   ├── services/    # Business logic
│       │   ├── ai/          # AI agents, chains, tools
│       │   ├── db/          # Database session, repositories
│       │   ├── tasks/       # Celery tasks
│       │   └── utils/       # Utility functions
│       ├── alembic/         # Database migrations
│       ├── tests/           # Tests
│       └── requirements/    # Python dependencies
│
├── infrastructure/
│   └── docker/             # Docker Compose configs
│
├── scripts/                # Setup and utility scripts
├── docs/                   # Documentation
├── package.json            # Root workspace config
└── turbo.json             # Turborepo config
```

## Development Commands

### Root Workspace

```bash
npm run dev        # Run all apps in development mode
npm run build      # Build all apps
npm run test       # Run all tests
npm run lint       # Lint all apps
npm run clean      # Clean all build artifacts and node_modules
```

### Backend (FastAPI)

```bash
# From apps/api directory
source venv/bin/activate

# Run server
uvicorn src.main:app --reload

# Create migration
alembic revision --autogenerate -m "description"

# Run migrations
alembic upgrade head

# Run tests
pytest

# Format code
black src/
ruff check src/
```

### Frontend (Next.js)

```bash
# From apps/web directory
npm run dev        # Development server
npm run build      # Production build
npm run start      # Start production server
npm run lint       # Lint code
npm test           # Run tests
```

### Infrastructure

```bash
# Start services
docker-compose -f infrastructure/docker/docker-compose.dev.yml up -d

# Stop services
docker-compose -f infrastructure/docker/docker-compose.dev.yml down

# View logs
docker-compose -f infrastructure/docker/docker-compose.dev.yml logs -f

# Reset all data (destructive!)
docker-compose -f infrastructure/docker/docker-compose.dev.yml down -v
```

## Database Migrations

### Creating a New Migration

```bash
cd apps/api
source venv/bin/activate

# Make changes to models in src/models/
# Then create a migration
alembic revision --autogenerate -m "Add user and document models"
```

### Applying Migrations

```bash
# Upgrade to latest version
alembic upgrade head

# Downgrade one version
alembic downgrade -1

# View migration history
alembic history
```

## Testing

### Backend Tests

```bash
cd apps/api
source venv/bin/activate
pytest                          # Run all tests
pytest tests/unit              # Run unit tests only
pytest tests/integration       # Run integration tests only
pytest --cov=src               # Run with coverage
```

### Frontend Tests

```bash
cd apps/web
npm test                       # Run Jest tests
npm run test:watch             # Run tests in watch mode
npx playwright test            # Run E2E tests
```

## Implementation Roadmap

### ✅ Phase 1: Foundation & Infrastructure (Completed)
- Monorepo setup with Turborepo
- Next.js 14 frontend
- FastAPI backend
- Docker Compose for local services
- Database setup with Alembic

### 🚧 Phase 2: Authentication System (Next)
- User registration and login
- JWT authentication
- Role-based access control
- Protected routes

### 📋 Phase 3: Document Management
- Document upload/download
- S3/MinIO storage integration
- Document metadata
- File type support (PDF, DOCX, TXT)

### 📋 Phase 4: Vector Storage & Embeddings
- Document chunking
- Embedding generation
- pgvector integration
- Semantic search

### 📋 Phase 5: AI Assistant Core
- Conversational AI with Claude
- RAG (Retrieval Augmented Generation)
- Source citation extraction
- Chat UI

### 📋 Phase 6: UI Polish & UX
- Conversation history
- Document context selector
- Settings page
- Mobile responsive design

### 📋 Phase 7: Testing & Documentation
- Unit tests
- Integration tests
- E2E tests
- API documentation
- User guides

## Environment Variables

See `.env.example` for a full list of configuration options.

### Required Variables

- `DATABASE_URL`: PostgreSQL connection string
- `ANTHROPIC_API_KEY`: Anthropic API key for Claude
- `JWT_SECRET_KEY`: Secret key for JWT token generation (min 32 chars)

### Optional Variables

- `DEBUG`: Enable debug mode (default: false)
- `LOG_LEVEL`: Logging level (default: INFO)
- `CORS_ORIGINS`: Allowed CORS origins (default: http://localhost:3000)
- `MAX_UPLOAD_SIZE`: Maximum file upload size in bytes (default: 100MB)

## Troubleshooting

### Database Connection Issues

```bash
# Check if PostgreSQL is running
docker-compose -f infrastructure/docker/docker-compose.dev.yml ps

# View PostgreSQL logs
docker logs legal-assistant-postgres

# Connect to PostgreSQL
docker exec -it legal-assistant-postgres psql -U postgres -d legal_assistant
```

### Redis Connection Issues

```bash
# Check if Redis is running
docker-compose -f infrastructure/docker/docker-compose.dev.yml ps

# Test Redis connection
docker exec -it legal-assistant-redis redis-cli ping
```

### MinIO Connection Issues

```bash
# Access MinIO console at http://localhost:9001
# Default credentials: minioadmin / minioadmin

# Check MinIO logs
docker logs legal-assistant-minio
```

### Python Dependencies

```bash
# Recreate virtual environment
cd apps/api
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements/dev.txt
```

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) for development guidelines.

## License

[License Type] - See [LICENSE](./LICENSE) for details.

## Support

For issues and questions:
- Open an issue on GitHub
- Check the [documentation](./docs/)
- Review the implementation plan at `.claude/plans/floating-sleeping-star.md`
