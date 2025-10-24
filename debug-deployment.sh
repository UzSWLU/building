#!/bin/bash

echo "🔍 Building API Deployment Debug Script"
echo "========================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    local status=$1
    local message=$2
    case $status in
        "SUCCESS")
            echo -e "${GREEN}✅ $message${NC}"
            ;;
        "ERROR")
            echo -e "${RED}❌ $message${NC}"
            ;;
        "WARNING")
            echo -e "${YELLOW}⚠️  $message${NC}"
            ;;
        "INFO")
            echo -e "${BLUE}ℹ️  $message${NC}"
            ;;
    esac
}

# Check if we're in the right directory
if [ ! -f "docker-compose.prod.yml" ]; then
    print_status "ERROR" "docker-compose.prod.yml not found. Please run this script from the project root directory."
    exit 1
fi

print_status "INFO" "Starting deployment debug..."

echo ""
echo "📊 1. SYSTEM INFORMATION"
echo "======================="
echo "Date: $(date)"
echo "User: $(whoami)"
echo "Hostname: $(hostname)"
echo "Uptime: $(uptime)"
echo ""

echo "📊 2. DOCKER STATUS"
echo "=================="
print_status "INFO" "Checking Docker service status..."
systemctl is-active docker || print_status "WARNING" "Docker service not active"

print_status "INFO" "Docker version:"
docker --version || print_status "ERROR" "Docker not installed"

print_status "INFO" "Docker Compose version:"
docker-compose --version || print_status "ERROR" "Docker Compose not installed"

echo ""
print_status "INFO" "Docker system info:"
docker system df

echo ""
print_status "INFO" "Running containers:"
docker ps

echo ""
print_status "INFO" "All containers (including stopped):"
docker ps -a

echo ""
echo "📊 3. PROJECT STATUS"
echo "==================="
print_status "INFO" "Current directory: $(pwd)"
print_status "INFO" "Git status:"
git status --short || print_status "WARNING" "Not a git repository"

print_status "INFO" "Git branch:"
git branch --show-current || print_status "WARNING" "No git branch info"

print_status "INFO" "Last commit:"
git log -1 --oneline || print_status "WARNING" "No git commits"

echo ""
echo "📊 4. ENVIRONMENT FILES"
echo "====================="
if [ -f ".env.prod" ]; then
    print_status "SUCCESS" ".env.prod file exists"
    print_status "INFO" "Environment file size: $(wc -l < .env.prod) lines"
else
    print_status "ERROR" ".env.prod file not found"
fi

if [ -f "env.prod.example" ]; then
    print_status "SUCCESS" "env.prod.example template exists"
else
    print_status "WARNING" "env.prod.example template not found"
fi

echo ""
echo "📊 5. DOCKER COMPOSE STATUS"
echo "=========================="
print_status "INFO" "Checking docker-compose.prod.yml services..."

# Check if containers are defined
if docker-compose -f docker-compose.prod.yml config --services > /dev/null 2>&1; then
    print_status "SUCCESS" "docker-compose.prod.yml is valid"
    
    print_status "INFO" "Defined services:"
    docker-compose -f docker-compose.prod.yml config --services
    
    print_status "INFO" "Container status:"
    docker-compose -f docker-compose.prod.yml ps
    
    echo ""
    print_status "INFO" "Service health checks:"
    
    # Check each service
    for service in $(docker-compose -f docker-compose.prod.yml config --services); do
        echo "Checking $service..."
        if docker-compose -f docker-compose.prod.yml ps $service | grep -q "Up"; then
            print_status "SUCCESS" "$service is running"
        else
            print_status "ERROR" "$service is not running"
            print_status "INFO" "Logs for $service:"
            docker-compose -f docker-compose.prod.yml logs $service --tail=10
        fi
    done
else
    print_status "ERROR" "docker-compose.prod.yml is invalid"
    print_status "INFO" "Configuration errors:"
    docker-compose -f docker-compose.prod.yml config
fi

echo ""
echo "📊 6. NETWORK CONNECTIVITY"
echo "========================="
print_status "INFO" "Testing local connectivity..."

# Test local ports
for port in 5001 5443; do
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:$port > /dev/null 2>&1; then
        print_status "SUCCESS" "Port $port is accessible locally"
    else
        print_status "ERROR" "Port $port is not accessible locally"
    fi
done

# Test external domain
print_status "INFO" "Testing external domain..."
if curl -s -o /dev/null -w "%{http_code}" https://building.api.uzswlu.uz > /dev/null 2>&1; then
    print_status "SUCCESS" "External domain https://building.api.uzswlu.uz is accessible"
else
    print_status "ERROR" "External domain https://building.api.uzswlu.uz is not accessible"
fi

echo ""
echo "📊 7. LOG ANALYSIS"
echo "================="
print_status "INFO" "Recent logs from all services:"

for service in $(docker-compose -f docker-compose.prod.yml config --services); do
    echo ""
    print_status "INFO" "=== $service logs (last 20 lines) ==="
    docker-compose -f docker-compose.prod.yml logs $service --tail=20
done

echo ""
echo "📊 8. DISK SPACE"
echo "==============="
print_status "INFO" "Disk usage:"
df -h

print_status "INFO" "Docker volumes:"
docker volume ls

echo ""
echo "📊 9. RECOMMENDATIONS"
echo "==================="
echo ""

# Check for common issues
if ! docker ps | grep -q "building-api-web-1"; then
    print_status "WARNING" "Web container is not running. Try: docker-compose -f docker-compose.prod.yml up -d web"
fi

if ! docker ps | grep -q "building-api-nginx-1"; then
    print_status "WARNING" "Nginx container is not running. Try: docker-compose -f docker-compose.prod.yml up -d nginx"
fi

if ! docker ps | grep -q "building-api-db-1"; then
    print_status "WARNING" "Database container is not running. Try: docker-compose -f docker-compose.prod.yml up -d db"
fi

if [ ! -f ".env.prod" ]; then
    print_status "WARNING" "Environment file missing. Copy from template: cp env.prod.example .env.prod"
fi

echo ""
print_status "INFO" "Debug completed. Check the output above for any issues."
echo ""
print_status "INFO" "For more detailed logs, run:"
echo "  docker-compose -f docker-compose.prod.yml logs -f"
echo ""
print_status "INFO" "To restart all services:"
echo "  docker-compose -f docker-compose.prod.yml down"
echo "  docker-compose -f docker-compose.prod.yml up -d --build"
