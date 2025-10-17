#!/bin/bash

# Production Deployment Script for RTTM Django Project
# Usage: ./deploy.sh [environment]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default environment
ENVIRONMENT=${1:-production}

echo -e "${GREEN}🚀 Starting deployment for environment: $ENVIRONMENT${NC}"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed. Please install Docker Compose first.${NC}"
    exit 1
fi

# Check if .env.prod exists
if [ ! -f ".env.prod" ]; then
    echo -e "${YELLOW}⚠️  .env.prod file not found. Creating from example...${NC}"
    if [ -f "env.prod.example" ]; then
        cp env.prod.example .env.prod
        echo -e "${YELLOW}📝 Please edit .env.prod with your production values before continuing.${NC}"
        echo -e "${YELLOW}   Press Enter when ready to continue...${NC}"
        read
    else
        echo -e "${RED}❌ env.prod.example file not found. Please create .env.prod manually.${NC}"
        exit 1
    fi
fi

# Create necessary directories
echo -e "${GREEN}📁 Creating necessary directories...${NC}"
mkdir -p logs
mkdir -p ssl
mkdir -p staticfiles
mkdir -p media

# Stop existing containers
echo -e "${GREEN}🛑 Stopping existing containers...${NC}"
docker-compose -f docker-compose.prod.yml down

# Remove old images (optional)
echo -e "${GREEN}🧹 Cleaning up old images...${NC}"
docker system prune -f

# Build and start services
echo -e "${GREEN}🔨 Building and starting services...${NC}"
docker-compose -f docker-compose.prod.yml up --build -d

# Wait for database to be ready
echo -e "${GREEN}⏳ Waiting for database to be ready...${NC}"
sleep 10

# Run migrations
echo -e "${GREEN}🗄️  Running database migrations...${NC}"
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate

# Create superuser (optional)
echo -e "${YELLOW}👤 Do you want to create a superuser? (y/n)${NC}"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
fi

# Collect static files
echo -e "${GREEN}📦 Collecting static files...${NC}"
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput

# Check if services are running
echo -e "${GREEN}🔍 Checking service status...${NC}"
docker-compose -f docker-compose.prod.yml ps

# Show logs
echo -e "${GREEN}📋 Recent logs:${NC}"
docker-compose -f docker-compose.prod.yml logs --tail=20

echo -e "${GREEN}✅ Deployment completed successfully!${NC}"
echo -e "${GREEN}🌐 Your application should be available at: http://localhost${NC}"
echo -e "${GREEN}📊 To view logs: docker-compose -f docker-compose.prod.yml logs -f${NC}"
echo -e "${GREEN}🛑 To stop: docker-compose -f docker-compose.prod.yml down${NC}"
