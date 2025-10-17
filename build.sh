#!/bin/bash

# Build Script for RTTM Django Project
# Usage: ./build.sh [environment]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default environment
ENVIRONMENT=${1:-production}

echo -e "${GREEN}🔨 Building RTTM Django Project for environment: $ENVIRONMENT${NC}"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed. Please install Docker Compose first.${NC}"
    exit 1
fi

# Create necessary directories
echo -e "${GREEN}📁 Creating necessary directories...${NC}"
mkdir -p logs
mkdir -p ssl
mkdir -p staticfiles
mkdir -p media

# Build the Docker image
echo -e "${GREEN}🏗️  Building Docker image...${NC}"
docker-compose -f docker-compose.prod.yml build --no-cache

# Build without cache for fresh build
echo -e "${GREEN}🧹 Cleaning up old images...${NC}"
docker system prune -f

echo -e "${GREEN}✅ Build completed successfully!${NC}"
echo -e "${GREEN}🚀 Run './deploy.sh' to deploy the application${NC}"
echo -e "${GREEN}📊 To view build logs: docker-compose -f docker-compose.prod.yml logs${NC}"
