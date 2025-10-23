#!/bin/bash

# Building API Deployment Script
# Usage: ./deploy.sh [environment] [version]

set -e

ENVIRONMENT=${1:-production}
VERSION=${2:-latest}

echo "🚀 =============================================="
echo "🚀 BUILDING API DEPLOYMENT"
echo "🚀 Environment: $ENVIRONMENT"
echo "🚀 Version: $VERSION"
echo "🚀 =============================================="

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "⚠️  Running as root. This is not recommended for production."
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Deployment cancelled."
        exit 1
    fi
fi

# Set deployment directory
DEPLOY_DIR="/var/www/building-api"
BACKUP_DIR="/var/www/backups/building-api"

echo "📁 Deployment directory: $DEPLOY_DIR"

# Create directories if they don't exist
sudo mkdir -p "$DEPLOY_DIR"
sudo mkdir -p "$BACKUP_DIR"

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

# Navigate to deployment directory
cd "$DEPLOY_DIR"

echo "📥 Pulling latest code..."
git fetch origin main
git reset --hard origin/main

echo "🔧 Setting up environment..."
if [ ! -f .env.production ]; then
    echo "📝 Creating .env.production from template..."
    cp env.prod.example .env.production
    
    # Generate secure passwords
    DJANGO_SECRET_KEY=$(openssl rand -base64 32)
    POSTGRES_PASSWORD=$(openssl rand -base64 24)
    
    # Update environment file
    sed -i "s/DJANGO_SECRET_KEY=.*/DJANGO_SECRET_KEY=$DJANGO_SECRET_KEY/" .env.production
    sed -i "s/POSTGRES_PASSWORD=.*/POSTGRES_PASSWORD=$POSTGRES_PASSWORD/" .env.production
    
    echo "✅ Environment file created with secure passwords"
else
    echo "✅ Environment file already exists"
fi

# Ensure OAuth URLs are configured
echo "🔗 Configuring OAuth URLs..."
sed -i '/^BACKEND_URL=/d' .env.production
sed -i '/^FRONTEND_CALLBACK_URL=/d' .env.production
sed -i '/^# OAuth URLs/d' .env.production

echo "" >> .env.production
echo "# OAuth URLs" >> .env.production
echo "BACKEND_URL=https://auth.uzswlu.uz" >> .env.production
echo "FRONTEND_CALLBACK_URL=https://building.swagger.uzswlu.uz/callback,http://localhost:5001/callback" >> .env.production

echo "✅ OAuth URLs configured"

# Create backup before deployment
echo "💾 Creating backup..."
BACKUP_FILE="$BACKUP_DIR/backup_$(date +%Y%m%d_%H%M%S).sql"
if docker-compose -f docker-compose.prod.yml ps | grep -q "Up"; then
    echo "📊 Creating database backup..."
    docker-compose -f docker-compose.prod.yml exec -T db pg_dump -U building building > "$BACKUP_FILE" || echo "⚠️  Backup failed, continuing..."
    echo "✅ Backup created: $BACKUP_FILE"
else
    echo "ℹ️  No running containers to backup"
fi

# Stop existing containers
echo "🛑 Stopping existing containers..."
docker-compose -f docker-compose.prod.yml down -v

# Build and start new containers
echo "🔨 Building and starting containers..."
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 30

# Run database migrations
echo "🗄️ Running database migrations..."
docker-compose -f docker-compose.prod.yml exec -T web python manage.py migrate

# Create superuser if not exists
echo "👤 Creating superuser..."
docker-compose -f docker-compose.prod.yml exec -T web python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@uzswlu.uz', 'admin123')
    print('Superuser created: admin/admin123')
else:
    print('Superuser already exists')
"

# Collect static files
echo "📊 Collecting static files..."
docker-compose -f docker-compose.prod.yml exec -T web python manage.py collectstatic --noinput

# Health check
echo "🏥 Performing health checks..."
sleep 10

# Check container status
echo "📊 Container Status:"
docker-compose -f docker-compose.prod.yml ps

# Test API endpoints
echo "🔍 Testing API endpoints..."

# Health check
if curl -f -s https://building.swagger.uzswlu.uz/health/ > /dev/null; then
    echo "✅ Health check passed"
else
    echo "❌ Health check failed"
fi

# Swagger UI
if curl -f -s https://building.swagger.uzswlu.uz/ > /dev/null; then
    echo "✅ Swagger UI accessible"
else
    echo "❌ Swagger UI not accessible"
fi

# API schema
if curl -f -s https://building.swagger.uzswlu.uz/api/schema/ > /dev/null; then
    echo "✅ API schema accessible"
else
    echo "❌ API schema not accessible"
fi

# Clean up old images
echo "🧹 Cleaning up old Docker images..."
docker image prune -f

echo ""
echo "✅ =============================================="
echo "✅ DEPLOYMENT COMPLETED SUCCESSFULLY!"
echo "✅ =============================================="
echo ""
echo "🔗 API: https://building.swagger.uzswlu.uz/"
echo "🔗 Swagger UI: https://building.swagger.uzswlu.uz/"
echo "🔗 Health Check: https://building.swagger.uzswlu.uz/health/"
echo "🔗 Admin: https://building.swagger.uzswlu.uz/admin/"
echo ""
echo "👤 Default Admin Credentials:"
echo "   Username: admin"
echo "   Password: admin123"
echo ""
echo "📊 Container Status:"
docker-compose -f docker-compose.prod.yml ps
echo ""
echo "📝 Recent Logs:"
docker-compose -f docker-compose.prod.yml logs --tail=20 web