# 🚀 Building API Runner Setup - Server Commands

## 📋 GitHub dan Berilgan Komandalar

GitHub dan quyidagi komandalar berildi:

### 1. Runner Katalogini Yaratish va Yuklab Olish

```bash
# Serverga ulanish
ssh root@172.22.0.19
# Password: Rm09HVd_XhXHa

# Runner katalogini yaratish
mkdir -p /var/www/building-api/runner
cd /var/www/building-api/runner

# Runner fayllarini yuklab olish (GitHub dan berilgan)
curl -o actions-runner-linux-x64-2.329.0.tar.gz -L https://github.com/actions/runner/releases/download/v2.329.0/actions-runner-linux-x64-2.329.0.tar.gz

# Hash tekshirish (ixtiyoriy)
echo "194f1e1e4bd02f80b7e9633fc546084d8d4e19f3928a324d512ea53430102e1d  actions-runner-linux-x64-2.329.0.tar.gz" | shasum -a 256 -c

# Arxivni ochish
tar xzf ./actions-runner-linux-x64-2.329.0.tar.gz
```

### 2. Runner Konfiguratsiyasi

```bash
# Runner ni konfiguratsiya qilish (GitHub dan berilgan token bilan)
./config.sh --url https://github.com/a-d-sh/building --token ALLG4AJAAKJ2VNZ2QQISMX3I7HJEC
```

### 3. Runner ni Ishga Tushirish

```bash
# Service sifatida o'rnatish
./svc.sh install

# Serviceni ishga tushirish
./svc.sh start

# Yoki manual ishga tushirish (test uchun)
./run.sh
```

## 🔧 To'liq Server Setup

### Step 1: Serverga Ulanish

```bash
ssh root@172.22.0.19
# Password: Rm09HVd_XhXHa
```

### Step 2: Runner O'rnatish

```bash
# Runner katalogini yaratish
mkdir -p /var/www/building-api/runner
cd /var/www/building-api/runner

# Runner fayllarini yuklab olish
curl -o actions-runner-linux-x64-2.329.0.tar.gz -L https://github.com/actions/runner/releases/download/v2.329.0/actions-runner-linux-x64-2.329.0.tar.gz

# Arxivni ochish
tar xzf ./actions-runner-linux-x64-2.329.0.tar.gz
rm ./actions-runner-linux-x64-2.329.0.tar.gz

# Ruxsatlarni sozlash
chown -R root:root /var/www/building-api/runner
chmod +x /var/www/building-api/runner/config.sh
chmod +x /var/www/building-api/runner/run.sh
chmod +x /var/www/building-api/runner/svc.sh
```

### Step 3: Runner Konfiguratsiyasi

```bash
# Runner ni konfiguratsiya qilish
./config.sh --url https://github.com/a-d-sh/building --token ALLG4AJAAKJ2VNZ2QQISMX3I7HJEC

# Service sifatida o'rnatish
./svc.sh install

# Serviceni ishga tushirish
./svc.sh start
```

### Step 4: Building API Deployment

```bash
# Kodni yuklash
mkdir -p /var/www/building-api
cd /var/www/building-api
git clone https://github.com/a-d-sh/building.git .

# Environment faylini sozlash
cp env.prod.example .env.production

# Environment faylini tahrirlash
nano .env.production
```

### Step 5: Environment Faylini Sozlash

```bash
# .env.production faylida quyidagilarni sozlang:
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=0
DJANGO_ALLOWED_HOSTS=building.swagger.uzswlu.uz
POSTGRES_DB=building
POSTGRES_USER=building
POSTGRES_PASSWORD=your-secure-password
AUTH_BASE_URL=https://auth.uzswlu.uz
BACKEND_URL=https://auth.uzswlu.uz
FRONTEND_CALLBACK_URL=https://building.swagger.uzswlu.uz/callback
```

### Step 6: Deployment

```bash
# Deployment scriptini ruxsat berish
chmod +x deploy.sh

# Deployment ni ishga tushirish
./deploy.sh production latest
```

## ✅ Tekshirish

### Runner Status

```bash
# Runner serviceni tekshirish
systemctl status actions.runner.building-api

# Runner loglarini ko'rish
journalctl -u actions.runner.building-api -f

# Runner katalogini tekshirish
ls -la /var/www/building-api/runner/
```

### Application Status

```bash
# Docker containerlarni tekshirish
docker-compose -f /var/www/building-api/docker-compose.prod.yml ps

# Application loglarini ko'rish
docker-compose -f /var/www/building-api/docker-compose.prod.yml logs -f web
```

### API Test

```bash
# Health check
curl http://localhost:5001/health/

# Swagger UI
curl http://localhost:5001/
```

## 🚀 GitHub Actions Test

### Manual Trigger

1. **GitHub** → https://github.com/a-d-sh/building/actions
2. **"Deploy to Production"** workflow ni tanlang
3. **"Run workflow"** tugmasini bosing
4. Runner ishlayotganini tekshirish

### Push Trigger

```bash
# Kodni o'zgartirish va push qilish
echo "# Test" >> README.md
git add README.md
git commit -m "test: Test GitHub Actions runner"
git push origin main
```

## 🛠️ Troubleshooting

### Issue: Runner Offline

```bash
# Runner serviceni qayta ishga tushirish
systemctl restart actions.runner.building-api

# Yoki manual ishga tushirish
cd /var/www/building-api/runner
./run.sh
```

### Issue: Permission Denied

```bash
# Ruxsatlarni to'g'rilash
chown -R root:root /var/www/building-api/runner
chmod +x /var/www/building-api/runner/config.sh
chmod +x /var/www/building-api/runner/run.sh
chmod +x /var/www/building-api/runner/svc.sh
```

### Issue: Token Expired

```bash
# Runner ni qayta konfiguratsiya qilish
cd /var/www/building-api/runner
./config.sh remove
./config.sh --url https://github.com/a-d-sh/building --token NEW_TOKEN
```

## 📊 Monitoring

```bash
# Runner status
systemctl status actions.runner.building-api

# Application logs
docker-compose -f /var/www/building-api/docker-compose.prod.yml logs -f web

# System resources
htop
df -h
free -h
```

## 🎯 Success Checklist

- [ ] Serverga SSH orqali ulanish
- [ ] Runner katalogi yaratilgan (`/var/www/building-api/runner`)
- [ ] Runner fayllari yuklab olingan
- [ ] Runner konfiguratsiya qilingan
- [ ] Service ishga tushirilgan
- [ ] GitHub da runner "Online" ko'rinadi
- [ ] Building API kod yuklangan
- [ ] Environment sozlangan
- [ ] Docker containerlar ishlaydi
- [ ] API endpoints ishlaydi
- [ ] GitHub Actions ishlaydi

---

**Building API uchun runner setup endi tayyor!** 🚀

**Server**: 172.22.0.19  
**Username**: root  
**Password**: Rm09HVd_XhXHa  
**Token**: ALLG4AJAAKJ2VNZ2QQISMX3I7HJEC
