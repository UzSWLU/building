# 🖥️ Server Setup Guide - Building API

## 📋 Server Ma'lumotlari

- **Server IP**: 172.22.0.19
- **Username**: root
- **Password**: Rm09HVd_XhXHa
- **OS**: Ubuntu Linux

## 🔧 Step 1: Serverga Ulanish

### Windows da SSH Client O'rnatish

**Option A: Windows Terminal + OpenSSH**

1. **Windows Terminal** o'rnating (Microsoft Store dan)
2. **OpenSSH Client** o'rnating:
   ```powershell
   # PowerShell da (Admin sifatida)
   Add-WindowsCapability -Online -Name OpenSSH.Client~~~~0.0.1.0
   ```

**Option B: PuTTY**

1. PuTTY yuklab oling: https://www.putty.org/
2. O'rnating va ishga tushiring
3. Host: `172.22.0.19`
4. Port: `22`
5. Username: `root`
6. Password: `Rm09HVd_XhXHa`

**Option C: WSL (Windows Subsystem for Linux)**

1. WSL o'rnating:
   ```powershell
   wsl --install
   ```
2. Ubuntu terminal oching
3. SSH orqali ulaning:
   ```bash
   ssh root@172.22.0.19
   ```

## 🚀 Step 2: Server Setup

### 2.1 Serverga Ulanish

```bash
ssh root@172.22.0.19
# Password: Rm09HVd_XhXHa
```

### 2.2 Mavjud Runnerlarni Tekshirish

```bash
# Mavjud runnerlarni ko'rish
ls -la /var/www/

# Auth-api runner (mavjud)
ls -la /var/www/auth-api/

# Building-api runner (yaratish kerak)
ls -la /var/www/building-api/
```

### 2.3 Building API Runner Yaratish

```bash
# Runner katalogini yaratish
mkdir -p /var/www/building-api/runner
cd /var/www/building-api/runner

# Runner fayllarini yuklab olish
RUNNER_VERSION="2.311.0"
curl -o actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz -L https://github.com/actions/runner/releases/download/v${RUNNER_VERSION}/actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz

# Arxivni ochish
tar xzf ./actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz
rm ./actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz

# Ruxsatlarni sozlash
chown -R root:root /var/www/building-api/runner
chmod +x /var/www/building-api/runner/config.sh
chmod +x /var/www/building-api/runner/run.sh
chmod +x /var/www/building-api/runner/svc.sh

echo "✅ Runner fayllari yuklab olindi!"
```

## ⚙️ Step 3: GitHub da Runner Sozlash

### 3.1 GitHub Repository ga Kirish

1. **GitHub ga kiring**: https://github.com/a-d-sh/building
2. **Settings** → **Actions** → **Runners**
3. **"New self-hosted runner"** tugmasini bosing

### 3.2 Runner Konfiguratsiyasi

GitHub dan quyidagi komandalarni ko'rsatadi:

```bash
# Serverda runner katalogiga o'tish
cd /var/www/building-api/runner

# GitHub dan berilgan komandani ishga tushirish
./config.sh --url https://github.com/a-d-sh/building --token YOUR_TOKEN

# Service sifatida o'rnatish
./svc.sh install

# Serviceni ishga tushirish
./svc.sh start
```

## 🏗️ Step 4: Building API Deployment

### 4.1 Kodni Serverga Yuklash

```bash
# Deployment katalogini yaratish
mkdir -p /var/www/building-api
cd /var/www/building-api

# Repository ni klonlash
git clone https://github.com/a-d-sh/building.git .

# Environment faylini sozlash
cp env.prod.example .env.production

# Environment faylini tahrirlash
nano .env.production
```

### 4.2 Environment Faylini Sozlash

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

### 4.3 Deployment Scriptini Ishga Tushirish

```bash
# Deployment scriptini ruxsat berish
chmod +x deploy.sh

# Deployment ni ishga tushirish
./deploy.sh production latest
```

## 🔧 Step 5: Docker va Nginx Sozlash

### 5.1 Docker O'rnatish (agar yo'q bo'lsa)

```bash
# Docker o'rnatish
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
rm get-docker.sh

# Docker Compose o'rnatish
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
```

### 5.2 Nginx Sozlash

```bash
# Nginx o'rnatish
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
    }
}
EOF

# Site ni faollashtirish
ln -sf /etc/nginx/sites-available/building.swagger.uzswlu.uz /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Nginx ni qayta ishga tushirish
systemctl restart nginx
systemctl enable nginx
```

## ✅ Step 6: Tekshirish

### 6.1 Runner Status

```bash
# Runner serviceni tekshirish
systemctl status actions.runner.building-api

# Runner loglarini ko'rish
journalctl -u actions.runner.building-api -f
```

### 6.2 Application Status

```bash
# Docker containerlarni tekshirish
docker-compose -f /var/www/building-api/docker-compose.prod.yml ps

# Application loglarini ko'rish
docker-compose -f /var/www/building-api/docker-compose.prod.yml logs -f web
```

### 6.3 API Test

```bash
# Health check
curl http://localhost:5001/health/

# Swagger UI
curl http://localhost:5001/

# Nginx orqali test
curl http://building.swagger.uzswlu.uz/health/
```

## 🚀 Step 7: GitHub Actions Test

### 7.1 Manual Trigger

1. **GitHub** → **Actions** → **"Deploy to Production"**
2. **"Run workflow"** tugmasini bosing
3. Runner ishlayotganini tekshirish

### 7.2 Push Trigger

```bash
# Kodni o'zgartirish va push qilish
echo "# Test" >> README.md
git add README.md
git commit -m "test: Test GitHub Actions runner"
git push origin main
```

## 🛠️ Troubleshooting

### Issue: "sudo ishlatilmaydi" Xatoligi

```bash
# Root user sifatida ishlatish
sudo su -

# Yoki runner fayllarini root ga tegishli qilish
chown -R root:root /var/www/building-api/runner
```

### Issue: Runner Offline

```bash
# Runner serviceni qayta ishga tushirish
systemctl restart actions.runner.building-api

# Yoki manual ishga tushirish
cd /var/www/building-api/runner
./run.sh
```

### Issue: Docker Permission Denied

```bash
# Root user ga Docker ruxsati berish
usermod -aG docker root
```

### Issue: Nginx Not Serving

```bash
# Nginx status tekshirish
systemctl status nginx

# Nginx konfiguratsiyasini tekshirish
nginx -t

# Nginx ni qayta ishga tushirish
systemctl restart nginx
```

## 📊 Monitoring Commands

```bash
# Runner status
systemctl status actions.runner.building-api

# Application logs
docker-compose -f /var/www/building-api/docker-compose.prod.yml logs -f web

# System resources
htop
df -h
free -h

# Network connections
netstat -tlnp | grep :5001
```

## 🎯 Success Checklist

- [ ] Serverga SSH orqali ulanish
- [ ] Building API runner katalogi yaratilgan
- [ ] Runner fayllari yuklab olingan
- [ ] GitHub da runner yaratilgan
- [ ] Runner konfiguratsiya qilingan
- [ ] Service ishga tushirilgan
- [ ] GitHub da runner "Online" ko'rinadi
- [ ] Building API kod yuklangan
- [ ] Environment sozlangan
- [ ] Docker containerlar ishlaydi
- [ ] Nginx sozlangan
- [ ] API endpoints ishlaydi
- [ ] Test deployment muvaffaqiyatli

## 🆘 Support

Agar muammolar bo'lsa:

1. **Server Logs**: `journalctl -u actions.runner.building-api -f`
2. **Application Logs**: `docker-compose logs -f web`
3. **GitHub Actions Logs**: Repository → Actions → Workflow logs
4. **Runner Status**: GitHub → Settings → Actions → Runners

---

**Building API uchun server setup endi tayyor!** 🚀

**Server**: 172.22.0.19  
**Username**: root  
**Password**: Rm09HVd_XhXHa
