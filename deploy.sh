#!/bin/bash

# Building API Deployment Script
# For server: 172.22.0.19
# Domain: building.swagger.uzswlu.uz

set -e

echo "🚀 Starting Building API deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_DIR="/opt/building"
DOMAIN="building.swagger.uzswlu.uz"
BACKUP_DIR="/opt/backups/building"

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    print_error "Please run as root"
    exit 1
fi

# Create project directory if it doesn't exist
if [ ! -d "$PROJECT_DIR" ]; then
    print_status "Creating project directory: $PROJECT_DIR"
    mkdir -p "$PROJECT_DIR"
fi

# Create backup directory
if [ ! -d "$BACKUP_DIR" ]; then
    print_status "Creating backup directory: $BACKUP_DIR"
    mkdir -p "$BACKUP_DIR"
fi

# Backup current deployment
if [ -d "$PROJECT_DIR" ] && [ "$(ls -A $PROJECT_DIR)" ]; then
    print_status "Creating backup of current deployment..."
    BACKUP_NAME="building-backup-$(date +%Y%m%d-%H%M%S)"
    cp -r "$PROJECT_DIR" "$BACKUP_DIR/$BACKUP_NAME"
    print_status "Backup created: $BACKUP_DIR/$BACKUP_NAME"
fi

# Install Docker if not installed
if ! command -v docker &> /dev/null; then
    print_status "Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    systemctl start docker
    systemctl enable docker
    rm get-docker.sh
fi

# Install Docker Compose if not installed
if ! command -v docker-compose &> /dev/null; then
    print_status "Installing Docker Compose..."
    curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
fi

# Install Git if not installed
if ! command -v git &> /dev/null; then
    print_status "Installing Git..."
    yum install -y git || apt-get update && apt-get install -y git
fi

# Clone or update repository
if [ ! -d "$PROJECT_DIR/.git" ]; then
    print_status "Cloning repository..."
    git clone https://github.com/a-d-sh/building.git "$PROJECT_DIR"
else
    print_status "Updating repository..."
    cd "$PROJECT_DIR"
    git pull origin main
fi

cd "$PROJECT_DIR"

# Create environment file if it doesn't exist
if [ ! -f ".env.prod" ]; then
    print_warning "Creating .env.prod from example..."
    cp env.prod.example .env.prod
    print_warning "Please edit .env.prod with your production values!"
fi

# Create SSL directory
mkdir -p ssl

# Generate self-signed certificate if no SSL certificate exists
if [ ! -f "ssl/cert.pem" ] || [ ! -f "ssl/key.pem" ]; then
    print_warning "Generating self-signed SSL certificate..."
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout ssl/key.pem \
        -out ssl/cert.pem \
        -subj "/C=UZ/ST=Tashkent/L=Tashkent/O=UZSWLU/OU=IT/CN=$DOMAIN"
fi

# Stop existing containers
print_status "Stopping existing containers..."
docker-compose -f docker-compose.prod.yml down || true

# Build and start containers
print_status "Building and starting containers..."
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d

# Wait for database to be ready
print_status "Waiting for database to be ready..."
sleep 10

# Run migrations
print_status "Running database migrations..."
docker-compose -f docker-compose.prod.yml exec -T web python manage.py migrate

# Collect static files
print_status "Collecting static files..."
docker-compose -f docker-compose.prod.yml exec -T web python manage.py collectstatic --noinput

# Create superuser if it doesn't exist
print_status "Creating superuser..."
docker-compose -f docker-compose.prod.yml exec -T web python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@uzswlu.uz', 'admin123')
    print('Superuser created: admin/admin123')
else:
    print('Superuser already exists')
"

# Setup firewall rules
print_status "Configuring firewall..."
if command -v ufw &> /dev/null; then
    ufw allow 80
    ufw allow 443
    ufw allow 22
elif command -v firewall-cmd &> /dev/null; then
    firewall-cmd --permanent --add-port=80/tcp
    firewall-cmd --permanent --add-port=443/tcp
    firewall-cmd --permanent --add-port=22/tcp
    firewall-cmd --reload
fi

# Setup systemd service for auto-start
print_status "Setting up systemd service..."
cat > /etc/systemd/system/building-api.service << EOF
[Unit]
Description=Building API
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=$PROJECT_DIR
ExecStart=/usr/local/bin/docker-compose -f docker-compose.prod.yml up -d
ExecStop=/usr/local/bin/docker-compose -f docker-compose.prod.yml down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable building-api.service

# Health check
print_status "Performing health check..."
sleep 5

if curl -f http://localhost/health/ > /dev/null 2>&1; then
    print_status "✅ Health check passed!"
else
    print_error "❌ Health check failed!"
    print_status "Container logs:"
    docker-compose -f docker-compose.prod.yml logs web
    exit 1
fi

# Final status
print_status "🎉 Deployment completed successfully!"
print_status "🌐 Application URL: https://$DOMAIN"
print_status "📚 Swagger UI: https://$DOMAIN"
print_status "🔧 Admin Panel: https://$DOMAIN/admin"
print_status "💚 Health Check: https://$DOMAIN/health/"

# Show container status
print_status "📊 Container Status:"
docker-compose -f docker-compose.prod.yml ps

echo ""
print_status "🔑 Default Admin Credentials:"
print_status "   Username: admin"
print_status "   Password: admin123"
print_warning "   Please change the default password!"