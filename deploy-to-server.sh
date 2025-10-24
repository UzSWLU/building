#!/bin/bash

echo "🚀 Deploying Building API to Server"
echo "====================================="

# Server configuration
SERVER_HOST="172.22.0.19"
SERVER_USER="root"
SERVER_PORT="22"
DEPLOY_DIR="/var/www/building-api"

echo "📁 Deploy directory: $DEPLOY_DIR"

# Create deployment script for server
cat > server-deploy.sh << 'EOF'
#!/bin/bash

echo "🔧 Server-side deployment script"
echo "================================="

cd /var/www/building-api || exit 1

echo "📥 Pulling latest code..."
git fetch origin main
git reset --hard origin/main

echo "🛑 Stopping existing containers..."
docker-compose -f docker-compose.prod.yml down || echo "No containers to stop"

echo "🔨 Building and starting containers..."
docker-compose -f docker-compose.prod.yml up -d --build

echo "⏳ Waiting for services to start..."
sleep 30

echo "🗄️ Running database migrations..."
docker-compose -f docker-compose.prod.yml exec -T web python manage.py migrate

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

echo "📊 Collecting static files..."
docker-compose -f docker-compose.prod.yml exec -T web python manage.py collectstatic --noinput

echo "🏥 Health check..."
sleep 10

echo "📊 Container Status:"
docker-compose -f docker-compose.prod.yml ps

echo "🔍 Testing API..."
if curl -f -s http://localhost:5001/api/health/ > /dev/null; then
    echo "✅ API health check passed"
else
    echo "❌ API health check failed"
fi

echo ""
echo "✅ =============================================="
echo "✅ BUILDING API DEPLOYED SUCCESSFULLY!"
echo "✅ =============================================="
echo ""
echo "🔗 API: https://building.api.uzswlu.uz/"
echo "🔗 Health Check: https://building.api.uzswlu.uz/api/health/"
echo "🔗 Admin: https://building.api.uzswlu.uz/admin/"
echo ""
echo "👤 Default Admin Credentials:"
echo "   Username: admin"
echo "   Password: admin123"
EOF

echo "📤 Uploading deployment script to server..."
echo "Run this command on the server:"
echo "bash server-deploy.sh"

echo ""
echo "📋 Manual deployment steps:"
echo "1. SSH to server: ssh root@172.22.0.19"
echo "2. Go to directory: cd /var/www/building-api"
echo "3. Pull latest code: git pull origin main"
echo "4. Restart containers: docker-compose -f docker-compose.prod.yml down && docker-compose -f docker-compose.prod.yml up -d --build"
echo "5. Run migrations: docker-compose -f docker-compose.prod.yml exec web python manage.py migrate"
echo "6. Test API: curl http://localhost:5001/api/health/"
