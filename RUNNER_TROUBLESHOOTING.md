# 🔧 Building API Runner Setup - Muammolar va Yechimlar

## 📋 Hozirgi Muammolar

❌ **Muammo 1**: `svc.sh` fayli yo'q  
❌ **Muammo 2**: `config.sh` sudo bilan ishlamaydi ("Must not run with sudo")

## 🔧 Yechim 1: svc.sh Faylini Topish

`svc.sh` fayli ba'zi versiyalarda boshqa nomda bo'lishi mumkin. Keling, tekshiramiz:

```bash
# Barcha fayllarni ko'rish
ls -la

# svc.sh ni qidirish
find . -name "*svc*" -type f

# Yoki barcha .sh fayllarni ko'rish
ls -la *.sh

# Yoki bin katalogida qidirish
ls -la bin/
```

## 🔧 Yechim 2: Deploy User Yaratish

`config.sh` sudo bilan ishlamaydi. Deploy user yaratamiz:

```bash
# Deploy user yaratish
useradd -m -s /bin/bash deploy

# Deploy user ga sudo ruxsati berish
usermod -aG sudo deploy

# Deploy user ga Docker ruxsati berish
usermod -aG docker deploy

# Deploy user ga runner katalogiga ruxsat berish
chown -R deploy:deploy /var/www/building-api/runner

# Deploy user ga o'tish
su - deploy
```

## 🔧 Yechim 3: Manual Runner Ishga Tushirish

Agar `svc.sh` yo'q bo'lsa, manual ishga tushirish:

```bash
# Deploy user sifatida
cd /var/www/building-api/runner

# Runner ni konfiguratsiya qilish
./config.sh --url https://github.com/a-d-sh/building --token ALLG4AJAAKJ2VNZ2QQISMX3I7HJEC

# Runner ni manual ishga tushirish
./run.sh
```

## 🔧 Yechim 4: Systemd Service Yaratish

Manual systemd service yaratish:

```bash
# Root user sifatida qaytish
exit

# Systemd service faylini yaratish
cat > /etc/systemd/system/building-api-runner.service << 'EOF'
[Unit]
Description=Building API GitHub Actions Runner
After=network.target

[Service]
Type=simple
User=deploy
WorkingDirectory=/var/www/building-api/runner
ExecStart=/var/www/building-api/runner/run.sh
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Service ni faollashtirish
systemctl daemon-reload
systemctl enable building-api-runner.service
systemctl start building-api-runner.service
```

## 🚀 To'liq Yechim (Tavsiya)

### Step 1: Deploy User Yaratish

```bash
# Root user sifatida
useradd -m -s /bin/bash deploy
usermod -aG sudo deploy
usermod -aG docker deploy

# Runner katalogiga ruxsat berish
chown -R deploy:deploy /var/www/building-api/runner
```

### Step 2: Deploy User ga O'tish

```bash
# Deploy user ga o'tish
su - deploy

# Runner katalogiga o'tish
cd /var/www/building-api/runner

# Runner ni konfiguratsiya qilish
./config.sh --url https://github.com/a-d-sh/building --token ALLG4AJAAKJ2VNZ2QQISMX3I7HJEC
```

### Step 3: Runner ni Ishga Tushirish

```bash
# Manual ishga tushirish (test uchun)
./run.sh

# Yoki background da ishga tushirish
nohup ./run.sh > runner.log 2>&1 &
```

### Step 4: Systemd Service (Ixtiyoriy)

```bash
# Root user ga qaytish
exit

# Systemd service yaratish
cat > /etc/systemd/system/building-api-runner.service << 'EOF'
[Unit]
Description=Building API GitHub Actions Runner
After=network.target

[Service]
Type=simple
User=deploy
WorkingDirectory=/var/www/building-api/runner
ExecStart=/var/www/building-api/runner/run.sh
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Service ni faollashtirish
systemctl daemon-reload
systemctl enable building-api-runner.service
systemctl start building-api-runner.service
```

## ✅ Tekshirish

### Runner Status

```bash
# Manual runner
ps aux | grep run.sh

# Systemd service
systemctl status building-api-runner.service

# Runner loglar
tail -f /var/www/building-api/runner/runner.log
```

### GitHub da Tekshirish

1. **GitHub** → https://github.com/a-d-sh/building/settings/actions/runners
2. **"building-api"** runner ko'rinishi kerak
3. Status: **"Online"** bo'lishi kerak

## 🛠️ Troubleshooting

### Issue: "Must not run with sudo"

```bash
# Deploy user yaratish
useradd -m -s /bin/bash deploy
usermod -aG sudo deploy
usermod -aG docker deploy

# Runner katalogiga ruxsat berish
chown -R deploy:deploy /var/www/building-api/runner

# Deploy user ga o'tish
su - deploy
cd /var/www/building-api/runner
./config.sh --url https://github.com/a-d-sh/building --token ALLG4AJAAKJ2VNZ2QQISMX3I7HJEC
```

### Issue: svc.sh fayli yo'q

```bash
# Manual ishga tushirish
./run.sh

# Yoki systemd service yaratish
# (yuqoridagi systemd service qadamlarini bajaring)
```

### Issue: Permission Denied

```bash
# Ruxsatlarni to'g'rilash
chown -R deploy:deploy /var/www/building-api/runner
chmod +x /var/www/building-api/runner/config.sh
chmod +x /var/www/building-api/runner/run.sh
```

## 🎯 Keyingi Qadamlar

Runner muvaffaqiyatli ishga tushgandan keyin:

1. **GitHub da runner "Online" ko'rinishi**
2. **Building API kodini yuklash**
3. **Environment sozlash**
4. **Docker deployment**
5. **GitHub Actions test**

---

**Building API runner setup davom etmoqda!** 🚀

**Hozirgi holat**: Runner fayllari tayyor, deploy user yaratish va konfiguratsiya qilish kerak
