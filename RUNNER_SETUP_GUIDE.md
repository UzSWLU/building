# 🤖 GitHub Actions Runner Setup Guide

## 📋 Building API uchun Runner Sozlash

Serverda allaqachon auth-api uchun runner bor, lekin building-api uchun alohida runner kerak.

## 🔧 Step 1: Serverga Ulanish

```bash
# SSH orqali serverga ulanish
ssh root@172.22.0.19

# Yoki Windows PowerShell da (agar SSH client bor bo'lsa)
ssh root@172.22.0.19
```

## 📁 Step 2: Runner Katalogini Tekshirish

```bash
# Mavjud runnerlarni ko'rish
ls -la /var/www/

# Auth-api runner (mavjud)
ls -la /var/www/auth-api/

# Building-api runner (yaratish kerak)
ls -la /var/www/building-api/
```

## 🚀 Step 3: Building API Runner Yaratish

### Option A: Avtomatik (Server Setup Script)

```bash
# Server setup scriptini ishga tushirish
cd /var/www/building-api
curl -fsSL https://raw.githubusercontent.com/a-d-sh/building/main/scripts/server-setup.sh | bash
```

### Option B: Manual

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
```

## ⚙️ Step 4: GitHub da Runner Sozlash

### 4.1 GitHub Repository ga Kirish

1. **GitHub ga kiring**: https://github.com/a-d-sh/building
2. **Settings** → **Actions** → **Runners**
3. **"New self-hosted runner"** tugmasini bosing

### 4.2 Runner Konfiguratsiyasi

GitHub dan quyidagi komandalarni ko'rsatadi:

```bash
# Download and configure
cd /opt/building-actions-runner
./config.sh --url https://github.com/a-d-sh/building --token YOUR_TOKEN

# Install as service
./svc.sh install

# Start service
./svc.sh start
```

### 4.3 Token Olish

GitHub da runner yaratishda token avtomatik beriladi. Ushbu token:

- 1 soat amal qiladi
- Faqat bir marta ishlatiladi
- Runner konfiguratsiyasi uchun kerak

## 🔧 Step 5: Runner Konfiguratsiyasi

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

## ✅ Step 6: Tekshirish

### 6.1 Runner Status

```bash
# Runner serviceni tekshirish
systemctl status actions.runner.building-api

# Runner loglarini ko'rish
journalctl -u actions.runner.building-api -f
```

### 6.2 GitHub da Tekshirish

1. **GitHub** → **Settings** → **Actions** → **Runners**
2. **"building-api"** runner ko'rinishi kerak
3. Status: **"Online"** bo'lishi kerak

## 🚀 Step 7: Test Deployment

```bash
# Building API kodini serverga yuklash
cd /var/www/building-api
git clone https://github.com/a-d-sh/building.git .

# Environment faylini sozlash
cp env.prod.example .env.production

# Deployment scriptini ishga tushirish
chmod +x deploy.sh
./deploy.sh production latest
```

## 🔄 Step 8: GitHub Actions Test

### 8.1 Manual Trigger

1. **GitHub** → **Actions** → **"Deploy to Production"**
2. **"Run workflow"** tugmasini bosing
3. Runner ishlayotganini tekshirish

### 8.2 Push Trigger

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

### Issue: Permission Denied

```bash
# Ruxsatlarni to'g'rilash
chmod +x /opt/building-actions-runner/config.sh
chmod +x /opt/building-actions-runner/run.sh
chmod +x /opt/building-actions-runner/svc.sh
```

### Issue: Token Expired

```bash
# Runner ni qayta konfiguratsiya qilish
cd /var/www/building-api/runner
./config.sh remove
./config.sh --url https://github.com/a-d-sh/building --token NEW_TOKEN
```

## 📊 Monitoring

### Runner Status

```bash
# Service status
systemctl status actions.runner.building-api

# Logs
journalctl -u actions.runner.building-api -f

# Runner directory
ls -la /var/www/building-api/runner/
```

### GitHub Actions

- **Repository**: https://github.com/a-d-sh/building/actions
- **Runners**: https://github.com/a-d-sh/building/settings/actions/runners

## 🎯 Success Checklist

- [ ] Serverga SSH orqali ulanish
- [ ] Building API runner katalogi yaratilgan
- [ ] Runner fayllari yuklab olingan
- [ ] GitHub da runner yaratilgan
- [ ] Runner konfiguratsiya qilingan
- [ ] Service ishga tushirilgan
- [ ] GitHub da runner "Online" ko'rinadi
- [ ] Test deployment muvaffaqiyatli
- [ ] GitHub Actions ishlaydi

## 🆘 Support

Agar muammolar bo'lsa:

1. **Server Logs**: `journalctl -u actions.runner.building-api -f`
2. **GitHub Actions Logs**: Repository → Actions → Workflow logs
3. **Runner Status**: GitHub → Settings → Actions → Runners

---

**Building API uchun GitHub Actions Runner endi tayyor!** 🚀
