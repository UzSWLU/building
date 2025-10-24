# Building API Server Deployment Guide

## 🚀 Quick Deploy Commands

```bash
# 1. SSH to server
ssh root@172.22.0.19

# 2. Go to project directory
cd /var/www/building-api

# 3. Pull latest code
git pull origin main

# 4. Stop and remove old containers
docker-compose -f docker-compose.prod.yml down -v

# 5. Build and start new containers
docker-compose -f docker-compose.prod.yml up -d --build

# 6. Wait for services to start
sleep 30

# 7. Run database migrations
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate

# 8. Create superuser (if needed)
docker-compose -f docker-compose.prod.yml exec web python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@uzswlu.uz', 'admin123') if not User.objects.filter(username='admin').exists() else print('Superuser already exists')"

# 9. Collect static files
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput

# 10. Test API
curl http://localhost:5001/api/health/

# 11. Check container status
docker-compose -f docker-compose.prod.yml ps
```

## 🔧 What Changed

- **Domain configuration**: Fixed `building.api.uzswlu.uz` in nginx and Django settings
- **Nginx config**: Updated server_name to correct domain
- **Django settings**: Updated ALLOWED_HOSTS for correct domain
- **Deploy script**: Added server deployment instructions

## 🎯 Expected Results

After deployment:

- ✅ API accessible at: `https://building.api.uzswlu.uz/`
- ✅ Health check: `https://building.api.uzswlu.uz/api/health/`
- ✅ Admin panel: `https://building.api.uzswlu.uz/admin/`
- ✅ Default admin: `admin` / `admin123`

## 🚨 Troubleshooting

If API still doesn't work:

1. Check container logs: `docker-compose -f docker-compose.prod.yml logs`
2. Check nginx config: `docker-compose -f docker-compose.prod.yml exec nginx nginx -t`
3. Check Django settings: `docker-compose -f docker-compose.prod.yml exec web python manage.py check`
4. Test local IP: `curl http://172.22.0.19:5001/api/health/`
