#!/bin/bash
# Docker Build Validation Script for HelpLink

echo "=================================="
echo "HelpLink Docker Build Validation"
echo "=================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker."
    exit 1
fi

echo "✓ Docker found"

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose is not installed."
    exit 1
fi

echo "✓ docker-compose found"
echo ""

# Build backend image
echo "📦 Building backend Docker image..."
docker build -f backend/Dockerfile -t helplink-backend:latest ./backend
if [ $? -ne 0 ]; then
    echo "❌ Backend build failed"
    exit 1
fi
echo "✓ Backend image built successfully"
echo ""

# Build frontend image
echo "📦 Building frontend Docker image..."
docker build -f frontend/Dockerfile -t helplink-frontend:latest ./frontend
if [ $? -ne 0 ]; then
    echo "❌ Frontend build failed"
    exit 1
fi
echo "✓ Frontend image built successfully"
echo ""

# Check image sizes
echo "📊 Docker image sizes:"
docker images | grep helplink
echo ""

echo "✅ All Docker images built successfully!"
echo ""
echo "Next steps:"
echo "1. Create .env file with API credentials"
echo "2. Run: docker-compose up -d"
echo "3. Visit: http://localhost (frontend on port 80)"
echo "4. Visit: http://localhost:8000/docs (API documentation)"
