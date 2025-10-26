#!/bin/bash

# Development environment startup script
echo "🔧 Starting StoreForge AI development environment..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Run ./scripts/setup.sh first."
    exit 1
fi

# Start development services
echo "🐳 Starting development containers..."
docker-compose up -d postgres redis

echo "⏳ Waiting for services to be ready..."
sleep 5

echo "🚀 Starting backend (FastAPI)..."
cd backend
python -m venv venv 2>/dev/null || true
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

echo "🎨 Starting frontend (Next.js)..."
cd ../frontend
npm install
npm run dev &
FRONTEND_PID=$!

echo ""
echo "✅ Development environment started!"
echo ""
echo "Services running:"
echo "🔗 Frontend: http://localhost:3000"
echo "🔗 Backend API: http://localhost:8000"
echo "🔗 API Docs: http://localhost:8000/docs"
echo "🔗 Database: localhost:5432"
echo "🔗 Redis: localhost:6379"
echo ""
echo "Press Ctrl+C to stop all services"

# Trap Ctrl+C and kill background processes
trap "echo 'Stopping services...'; kill $BACKEND_PID $FRONTEND_PID; docker-compose down; exit" INT

# Wait for background processes
wait