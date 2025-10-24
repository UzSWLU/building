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
echo '#!/bin/bash' > server-deploy.sh
echo '' >> server-deploy.sh
echo 'echo "🔧 Server-side deployment script"' >> server-deploy.sh
echo 'echo "================================="' >> server-deploy.sh
echo '' >> server-deploy.sh
echo 'cd /var/www/building-api || exit 1' >> server-deploy.sh
echo '' >> server-deploy.sh
echo 'echo "📥 Pulling latest code..."' >> server-deploy.sh
echo 'git fetch origin main' >> server-deploy.sh
echo 'git reset --hard origin/main' >> server-deploy.sh
echo '' >> server-deploy.sh
echo 'echo "🛑 Stopping existing containers..."' >> server-deploy.sh
echo 'docker-compose -f docker-compose.prod.yml down || echo "No containers to stop"' >> server-deploy.sh
echo '' >> server-deploy.sh
echo 'echo "🔨 Building and starting containers..."' >> server-deploy.sh
echo 'docker-compose -f docker-compose.prod.yml up -d --build' >> server-deploy.sh
echo '' >> server-deploy.sh
echo 'echo "⏳ Waiting for services to start..."' >> server-deploy.sh
echo 'sleep 30' >> server-deploy.sh
echo '' >> server-deploy.sh
echo 'echo "🗄️ Running database migrations..."' >> server-deploy.sh
echo 'docker-compose -f docker-compose.prod.yml exec -T web python manage.py migrate' >> server-deploy.sh
echo '' >> server-deploy.sh
echo 'echo "👤 Creating superuser..."' >> server-deploy.sh
echo 'docker-compose -f docker-compose.prod.yml exec -T web python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser(\"admin\", \"admin@uzswlu.uz\", \"admin123\") if not User.objects.filter(username=\"admin\").exists() else print(\"Superuser already exists\")"' >> server-deploy.sh
echo '' >> server-deploy.sh
echo 'echo "📊 Collecting static files..."' >> server-deploy.sh
echo 'docker-compose -f docker-compose.prod.yml exec -T web python manage.py collectstatic --noinput' >> server-deploy.sh
echo '' >> server-deploy.sh
echo 'echo "🏥 Health check..."' >> server-deploy.sh
echo 'sleep 10' >> server-deploy.sh
echo '' >> server-deploy.sh
echo 'echo "📊 Container Status:"' >> server-deploy.sh
echo 'docker-compose -f docker-compose.prod.yml ps' >> server-deploy.sh
echo '' >> server-deploy.sh
echo 'echo "🔍 Testing API..."' >> server-deploy.sh
echo 'if curl -f -s http://localhost:5001/api/health/ > /dev/null; then' >> server-deploy.sh
echo '    echo "✅ API health check passed"' >> server-deploy.sh
echo 'else' >> server-deploy.sh
echo '    echo "❌ API health check failed"' >> server-deploy.sh
echo 'fi' >> server-deploy.sh
echo '' >> server-deploy.sh
echo 'echo ""' >> server-deploy.sh
echo 'echo "✅ =============================================="' >> server-deploy.sh
echo 'echo "✅ BUILDING API DEPLOYED SUCCESSFULLY!"' >> server-deploy.sh
echo 'echo "✅ =============================================="' >> server-deploy.sh
echo 'echo ""' >> server-deploy.sh
echo 'echo "🔗 API: https://building.api.uzswlu.uz/"' >> server-deploy.sh
echo 'echo "🔗 Health Check: https://building.api.uzswlu.uz/api/health/"' >> server-deploy.sh
echo 'echo "🔗 Admin: https://building.api.uzswlu.uz/admin/"' >> server-deploy.sh
echo 'echo ""' >> server-deploy.sh
echo 'echo "👤 Default Admin Credentials:"' >> server-deploy.sh
echo 'echo "   Username: admin"' >> server-deploy.sh
echo 'echo "   Password: admin123"' >> server-deploy.sh

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
