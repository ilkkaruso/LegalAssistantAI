-- Initialize PostgreSQL database with pgvector extension

-- Create pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create uuid extension for UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Verify installations
SELECT extname, extversion FROM pg_extension WHERE extname IN ('vector', 'uuid-ossp');
