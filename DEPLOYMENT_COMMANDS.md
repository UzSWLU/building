# 🚀 Building API Deployment - Server Commands

## 📋 Environment Fayl Tayyor

Environment fayl quyidagi sozlamalar bilan tayyor:

```env
DJANGO_SECRET_KEY=django-insecure-production-secret-key-change-this-in-production
DJANGO_DEBUG=0
DJANGO_ALLOWED_HOSTS=building.swagger.uzswlu.uz
POSTGRES_DB=building
POSTGRES_USER=building
POSTGRES_PASSWORD=building_production_password_2024
POSTGRES_HOST=db
POSTGRES_PORT=5432
AUTH_BASE_URL=https://auth.uzswlu.uz
AUTH_TIMEOUT=10
AUTH_CACHE_TIMEOUT=300
SERVER_HOST=172.22.0.19
SERVER_USER=root
SERVER_PORT=22
```

## 🔧 Step 1: Building API Kodini Yuklash

```bash
# Building API katalogini yaratish
mkdir -p /var/www/building-api
cd /var/www/building-api

# Repository ni klonlash
git clone https://github.com/a-d-sh/building.git .

# Environment faylini yaratish
cat > .env.production << 'EOF'
# Production Environment Variables for Building API

# Django Settings
DJANGO_SECRET_KEY=django-insecure-production-secret-key-change-this-in-production
DJANGO_DEBUG=0
DJANGO_ALLOWED_HOSTS=building.swagger.uzswlu.uz

# Database Settings
POSTGRES_DB=building
POSTGRES_USER=building
POSTGRES_PASSWORD=building_production_password_2024
POSTGRES_HOST=db
POSTGRES_PORT=5432

# Auth Service
AUTH_BASE_URL=https://auth.uzswlu.uz
AUTH_TIMEOUT=10
AUTH_CACHE_TIMEOUT=300

# Server Settings
SERVER_HOST=172.22.0.19
SERVER_USER=root
SERVER_PORT=22
EOF

# Environment faylini tekshirish
cat .env.production
```

## 🐳 Step 2: Docker va Docker Compose Tekshirish

```bash
# Docker holatini tekshirish
docker --version
docker-compose --version

# Docker serviceni tekshirish
systemctl status docker

# Agar Docker yo'q bo'lsa, o'rnatish
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
rm get-docker.sh

# Docker Compose o'rnatish
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
```

## 🚀 Step 3: Deployment Scriptini Ishga Tushirish

```bash
# Deployment scriptini ruxsat berish
chmod +x deploy.sh

# Deployment ni ishga tushirish
./deploy.sh production latest
```

## 🔧 Step 4: Manual Deployment (Agar Script Ishlamasa)

```bash
# Docker Compose faylini tekshirish
ls -la docker-compose.prod.yml

# Docker containerlarni yaratish va ishga tushirish
docker-compose -f docker-compose.prod.yml up -d --build

# Containerlarni tekshirish
docker-compose -f docker-compose.prod.yml ps

# Loglarni ko'rish
docker-compose -f docker-compose.prod.yml logs -f web
```

## 🗄️ Step 5: Database Migration

```bash
# Database migration
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate

# Superuser yaratish
docker-compose -f docker-compose.prod.yml exec web python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@uzswlu.uz', 'admin123')
    print('Superuser created: admin/admin123')
else:
    print('Superuser already exists')
"

# Static fayllarni yig'ish
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
```

## 🌐 Step 6: Nginx Sozlash

```bash
# Nginx o'rnatish (agar yo'q bo'lsa)
apt-get update
apt-get install -y nginx

# Building API uchun Nginx konfiguratsiyasi
cat > /etc/nginx/sites-available/building.swagger.uzswlu.uz << 'EOF'
server {
    listen 80;
    server_name building.swagger.uzswlu.uz;

    location / {
        proxy_pass http://localhost:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }

    # Static files
    location /static/ {
        alias /var/www/building-api/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Media files
    location /media/ {
        alias /var/www/building-api/media/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF

# Site ni faollashtirish
ln -sf /etc/nginx/sites-available/building.swagger.uzswlu.uz /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Nginx konfiguratsiyasini tekshirish
nginx -t

# Nginx ni qayta ishga tushirish
systemctl restart nginx
systemctl enable nginx
```

## ✅ Step 7: Tekshirish

### Application Status

```bash
# Docker containerlarni tekshirish
docker-compose -f docker-compose.prod.yml ps

# Application loglarini ko'rish
docker-compose -f docker-compose.prod.yml logs -f web

# Database loglarini ko'rish
docker-compose -f docker-compose.prod.yml logs -f db

# Nginx loglarini ko'rish
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

### API Test

```bash
# Health check
curl http://localhost:5001/health/

# Swagger UI
curl http://localhost:5001/

# API schema
curl http://localhost:5001/api/schema/

# Nginx orqali test
curl http://building.swagger.uzswlu.uz/health/
curl http://building.swagger.uzswlu.uz/
```

### GitHub Actions Test

```bash
# GitHub Actions ni tekshirish
# https://github.com/a-d-sh/building/actions

# Yoki manual trigger
echo "# Test" >> README.md
git add README.md
git commit -m "test: Test deployment"
git push origin main
```

## 🛠️ Troubleshooting

### Issue: Docker Build Failed

```bash
# Docker loglarini ko'rish
docker-compose -f docker-compose.prod.yml logs web

# Docker image ni qayta build qilish
docker-compose -f docker-compose.prod.yml build --no-cache web
```

### Issue: Database Connection Failed

```bash
# Database containerini tekshirish
docker-compose -f docker-compose.prod.yml ps db

# Database loglarini ko'rish
docker-compose -f docker-compose.prod.yml logs db

# Database ga ulanishni tekshirish
docker-compose -f docker-compose.prod.yml exec web python manage.py dbshell
```

### Issue: Nginx Not Serving

```bash
# Nginx status
systemctl status nginx

# Nginx konfiguratsiyasini tekshirish
nginx -t

# Nginx ni qayta ishga tushirish
systemctl restart nginx
```

### Issue: Port Already in Use

```bash
# Port 5001 ni ishlatayotgan processni topish
lsof -i :5001

# Process ni o'chirish
kill -9 PID

# Yoki port ni o'zgartirish
# docker-compose.prod.yml da port ni o'zgartirish
```

## 📊 Monitoring

```bash
# System resources
htop
df -h
free -h

# Docker resources
docker stats

# Application logs
docker-compose -f docker-compose.prod.yml logs -f web

# Runner logs
journalctl -u building-api-runner.service -f
```

## 🎯 Success Checklist

- [x] ✅ Runner konfiguratsiya qilindi
- [x] ✅ Runner ishga tushdi
- [x] ✅ Systemd service yaratildi
- [x] ✅ GitHub Actions ishlaydi
- [ ] ⏳ Building API kod yuklanishi
- [ ] ⏳ Environment sozlash
- [ ] ⏳ Docker deployment
- [ ] ⏳ Database migration
- [ ] ⏳ Nginx sozlash
- [ ] ⏳ API endpoints test
- [ ] ⏳ GitHub Actions deployment test

---

**Building API deployment davom etmoqda!** 🚀

**Hozirgi holat**: Runner ishlayapti, kod yuklash va deployment qilish kerak
