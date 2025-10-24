#!/bin/bash

echo "🚀 Manual Deploy Script for Building Project"
echo "=============================================="

# Check if directory exists
if [ ! -d "/var/www/building-api" ]; then
    echo "❌ Directory /var/www/building-api not found"
    echo "📁 Creating directory..."
    sudo mkdir -p /var/www/building-api
    sudo chown -R deploy:deploy /var/www/building-api
fi

cd /var/www/building-api
echo "📁 Changed to /var/www/building-api"

# Check if git repository exists
if [ ! -d ".git" ]; then
    echo "📥 Cloning repository..."
    git clone https://github.com/UzSWLU/building.git .
    sudo chown -R deploy:deploy .
else
    echo "📥 Pulling latest code..."
    git fetch origin main
    git reset --hard origin/main
fi

echo "✅ Code updated successfully!"

# Stop existing containers
echo "🛑 Stopping existing containers..."
docker-compose -f docker-compose.prod.yml down || echo "No containers to stop"

# Build and start containers locally
echo "🔨 Building and starting containers..."
docker-compose -f docker-compose.prod.yml up -d --build

echo "✅ Containers started successfully!"

# Wait for containers to be ready
echo "⏳ Waiting for containers to be ready..."
sleep 15

# Check container status
echo "🔍 Checking container status..."
docker-compose -f docker-compose.prod.yml ps

# Check if containers are running
echo "📊 Monitoring deployment status..."

if docker ps | grep -q "building-api-web-1"; then
    echo "✅ Building API container is running"
else
    echo "❌ Building API container is not running"
    exit 1
fi

if docker ps | grep -q "building-api-nginx-1"; then
    echo "✅ Building Nginx container is running"
else
    echo "❌ Building Nginx container is not running"
    exit 1
fi

# Check if ports are accessible
if curl -s -o /dev/null -w "%{http_code}" http://localhost:5001 | grep -q "200"; then
    echo "✅ Building API is accessible on port 5001"
else
    echo "❌ Building API is not accessible on port 5001"
    exit 1
fi

echo "✅ =============================================="
echo "✅ BUILDING API DEPLOYED SUCCESSFULLY!"
echo "✅ =============================================="
echo ""
echo "🌐 Domain: https://building.api.uzswlu.uz"
echo "🔧 Port: 5001 (HTTP), 5443 (HTTPS)"
echo "📊 Status: Running"
echo ""
echo "🚀 Next steps:"
echo "1. Test the domain: curl -I https://building.api.uzswlu.uz"
echo "2. Check logs: docker-compose -f docker-compose.prod.yml logs"
