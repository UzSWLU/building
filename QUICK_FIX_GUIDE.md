# Building API Deploy Muammosi - Tezkor Yechim

## Muammo

`https://building.api.uzswlu.uz` ishlamayapti va loglar yo'q.

## Tezkor Tekshirish Qadamlar

### 1. GitHub Actions Loglarini Ko'rish

```bash
# GitHub repositoryga o'ting
# Actions tab → Oxirgi workflow runni tanlang
# Har bir job uchun loglarni tekshiring
```

### 2. Serverga Ulanish va Tekshirish

```bash
# Serverga SSH orqali ulaning
ssh root@172.22.0.19

# Project papkasiga o'ting
cd /var/www/building-api

# Debug scriptni ishga tushiring
./debug-deployment.sh
```

### 3. Container Statusini Tekshirish

```bash
# Barcha containerlarni ko'rish
docker ps -a

# Container statusini tekshirish
docker-compose -f docker-compose.prod.yml ps
```

### 4. Loglarni Tekshirish

```bash
# Barcha servislar uchun loglar
docker-compose -f docker-compose.prod.yml logs

# Faqat web servisi loglari
docker-compose -f docker-compose.prod.yml logs web

# Real-time loglarni kuzatish
docker-compose -f docker-compose.prod.yml logs -f
```

### 5. Qayta Deploy

```bash
# Oxirgi kodni olish
git fetch origin main
git reset --hard origin/main

# Containerlarni qayta ishga tushirish
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d --build

# Migrationlarni ishga tushirish
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate

# Static fayllarni yig'ish
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
```

## Asosiy Muammolar va Yechimlar

### Containerlar ishlamayapti

```bash
docker-compose -f docker-compose.prod.yml up -d --build
```

### Environment fayli yo'q

```bash
cp env.prod.example .env.prod
```

### Portlar band

```bash
netstat -tulpn | grep :5001
```

### Database ulanishi yo'q

```bash
docker-compose -f docker-compose.prod.yml restart db
```

## Monitoring

### Health Check

```bash
curl https://building.api.uzswlu.uz/api/health/
```

### API Test

```bash
curl https://building.api.uzswlu.uz/
```

## Emergency Commands

```bash
# Barcha containerlarni to'xtatish
docker-compose -f docker-compose.prod.yml down

# Faqat web servisini qayta ishga tushirish
docker-compose -f docker-compose.prod.yml restart web

# Container ichiga kirish
docker-compose -f docker-compose.prod.yml exec web bash
```

## Foydali Fayllar

- `debug-deployment.sh` - To'liq debug script
- `DEPLOYMENT_TROUBLESHOOTING.md` - Batafsil qo'llanma
- `deploy.sh` - To'liq deploy script
- `manual-deploy.sh` - Qo'lda deploy script

## Contact

Agar muammo hal bo'lmasa, debug script natijalarini va GitHub Actions loglarini support guruhiga yuboring.
