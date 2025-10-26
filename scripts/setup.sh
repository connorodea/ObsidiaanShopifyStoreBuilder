#!/bin/bash

# StoreForge AI Setup Script
echo "🚀 Setting up StoreForge AI..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create .env file from example if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from example..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your API keys before running the application."
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p backend/app/{api,core,db,models,services,utils,ai,scraper}
mkdir -p frontend/src/{app,components,lib,hooks,types}
mkdir -p docs
mkdir -p scripts

# Set permissions for scripts
chmod +x scripts/*.sh

# Build and start services
echo "🐳 Building Docker containers..."
docker-compose build

echo "🗄️  Starting database services..."
docker-compose up -d postgres redis

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
sleep 10

# Run database migrations (when implemented)
echo "🔄 Running database migrations..."
# docker-compose exec backend alembic upgrade head

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your API keys"
echo "2. Run 'docker-compose up -d' to start all services"
echo "3. Visit http://localhost:3000 for the frontend"
echo "4. Visit http://localhost:8000/docs for API documentation"
echo ""
echo "API Keys needed:"
echo "- OPENAI_API_KEY (for AI content generation)"
echo "- LEONARDO_API_KEY (for image enhancement)"
echo "- SHOPIFY_API_SECRET (for Shopify integration)"
echo "- AWS credentials (for S3 storage)"