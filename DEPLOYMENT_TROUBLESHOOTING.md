# Building API Deployment Troubleshooting Guide

## Muammo: https://building.api.uzswlu.uz ishlamayapti

### 1. GitHub Actions Deploy Jarayonini Tekshirish

#### GitHub Actions Loglarini Ko'rish:

1. GitHub repositoryga o'ting
2. "Actions" tabiga o'ting
3. Oxirgi workflow runni tanlang
4. Har bir job uchun loglarni tekshiring

#### Asosiy Tekshirish Qadamlar:

```bash
# Serverga SSH orqali ulaning
ssh root@172.22.0.19

# Project papkasiga o'ting
cd /var/www/building-api

# Debug scriptni ishga tushiring
./debug-deployment.sh
```

### 2. Docker Containerlarni Tekshirish

```bash
# Barcha containerlarni ko'rish
docker ps -a

# Faqat ishlayotgan containerlarni ko'rish
docker ps

# Container statusini tekshirish
docker-compose -f docker-compose.prod.yml ps
```

### 3. Loglarni Tekshirish

```bash
# Barcha servislar uchun loglar
docker-compose -f docker-compose.prod.yml logs

# Faqat web servisi loglari
docker-compose -f docker-compose.prod.yml logs web

# Faqat nginx servisi loglari
docker-compose -f docker-compose.prod.yml logs nginx

# Faqat database servisi loglari
docker-compose -f docker-compose.prod.yml logs db

# Real-time loglarni kuzatish
docker-compose -f docker-compose.prod.yml logs -f
```

### 4. Umumiy Muammolar va Yechimlar

#### Muammo: Containerlar ishlamayapti

```bash
# Containerlarni qayta ishga tushirish
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d --build
```

#### Muammo: Database ulanishi yo'q

```bash
# Database containerini tekshirish
docker-compose -f docker-compose.prod.yml logs db

# Database containerini qayta ishga tushirish
docker-compose -f docker-compose.prod.yml restart db
```

#### Muammo: Environment fayli yo'q

```bash
# Environment faylini yaratish
cp env.prod.example .env.prod

# Environment faylini tekshirish
cat .env.prod
```

#### Muammo: Portlar band

```bash
# Portlarni tekshirish
netstat -tulpn | grep :5001
netstat -tulpn | grep :5443

# Portlarni band qilgan jarayonlarni topish
lsof -i :5001
lsof -i :5443
```

### 5. GitHub Actions Workflow Muammolari

#### Muammo: Workflow ishlamayapti

1. GitHub repositoryda "Actions" tabiga o'ting
2. Oxirgi workflow runni tekshiring
3. Qaysi stepda xatolik borligini aniqlang

#### Muammo: Self-hosted runner ishlamayapti

```bash
# Runner servisini tekshirish
systemctl status actions.runner.*

# Runner servisini qayta ishga tushirish
systemctl restart actions.runner.*
```

### 6. Nginx Konfiguratsiyasi

```bash
# Nginx konfiguratsiyasini tekshirish
docker-compose -f docker-compose.prod.yml exec nginx nginx -t

# Nginx loglarini tekshirish
docker-compose -f docker-compose.prod.yml logs nginx
```

### 7. SSL Sertifikat Muammolari

```bash
# SSL sertifikatlarini tekshirish
ls -la /var/www/sertifikat/

# SSL sertifikatlarini tekshirish
openssl x509 -in /var/www/sertifikat/cert.pem -text -noout
```

### 8. Disk Space Muammolari

```bash
# Disk space tekshirish
df -h

# Docker image va containerlarni tozalash
docker system prune -a
docker volume prune
```

### 9. Network Connectivity

```bash
# Local portlarni tekshirish
curl -I http://localhost:5001
curl -I http://localhost:5443

# External domainni tekshirish
curl -I https://building.api.uzswlu.uz

# DNS tekshirish
nslookup building.api.uzswlu.uz
```

### 10. Database Muammolari

```bash
# Database ulanishini tekshirish
docker-compose -f docker-compose.prod.yml exec db psql -U building -d building -c "SELECT version();"

# Database migrationlarni ishga tushirish
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate

# Superuser yaratish
docker-compose -f docker-compose.prod.yml exec web python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@uzswlu.uz', 'admin123')
    print('Superuser created')
else:
    print('Superuser already exists')
"
```

### 11. To'liq Qayta Deploy

```bash
# To'liq qayta deploy
cd /var/www/building-api

# Oxirgi kodni olish
git fetch origin main
git reset --hard origin/main

# Containerlarni to'xtatish
docker-compose -f docker-compose.prod.yml down -v

# Yangi containerlarni yaratish
docker-compose -f docker-compose.prod.yml up -d --build

# Migrationlarni ishga tushirish
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate

# Static fayllarni yig'ish
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput

# Statusni tekshirish
docker-compose -f docker-compose.prod.yml ps
```

### 12. Monitoring va Alerting

#### Loglarni real-time kuzatish:

```bash
# Barcha servislar uchun
docker-compose -f docker-compose.prod.yml logs -f

# Faqat web servisi uchun
docker-compose -f docker-compose.prod.yml logs -f web
```

#### Health check:

```bash
# API health check
curl https://building.api.uzswlu.uz/api/health/

# Swagger UI
curl https://building.api.uzswlu.uz/

# Admin panel
curl https://building.api.uzswlu.uz/admin/
```

### 13. Emergency Commands

```bash
# Barcha containerlarni to'xtatish
docker-compose -f docker-compose.prod.yml down

# Faqat web servisini qayta ishga tushirish
docker-compose -f docker-compose.prod.yml restart web

# Database backup olish
docker-compose -f docker-compose.prod.yml exec db pg_dump -U building building > backup_$(date +%Y%m%d_%H%M%S).sql

# Container ichiga kirish
docker-compose -f docker-compose.prod.yml exec web bash
docker-compose -f docker-compose.prod.yml exec db bash
```

### 14. Contact va Support

Agar yuqoridagi qadamlar yordam bermasa:

1. GitHub Actions loglarini to'liq ko'ring
2. Server loglarini to'liq tekshiring
3. Debug script natijalarini saqlang
4. Muammoni batafsil tasvirlab, support guruhiga yuboring

### 15. Preventive Measures

1. **Regular Monitoring**: Har kuni container statusini tekshiring
2. **Log Rotation**: Loglarni muntazam tozalang
3. **Backup**: Database backuplarini muntazam oling
4. **Updates**: Docker image va dependencylarni yangilang
5. **Security**: Environment fayllarini himoyalang
