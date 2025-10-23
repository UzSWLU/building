# 🔧 Building API Runner Setup - Server Commands

## 📋 Serverda Qilingan Ishlar

✅ **Muvaffaqiyatli:**

- Runner katalogi yaratildi: `/var/www/building-api/runner`
- Runner fayllari yuklab olindi (179MB)
- Arxiv ochildi
- Ruxsatlar sozlandi

❌ **Muammo:**

- `svc.sh` fayli topilmadi

## 🔧 Muammoni Hal Qilish

### Step 1: Fayllarni Tekshirish

```bash
# Hozirgi katalogda nima borligini ko'rish
ls -la /var/www/building-api/runner/

# Fayllar ro'yxatini ko'rish
ls -la
```

### Step 2: To'g'ri Versiyani Yuklab Olish

GitHub dan berilgan versiya `2.329.0` edi, lekin siz `2.311.0` yuklab oldingiz. Keling, to'g'ri versiyani yuklab olamiz:

```bash
# Eski fayllarni o'chirish
rm -rf *

# To'g'ri versiyani yuklab olish (GitHub dan berilgan)
curl -o actions-runner-linux-x64-2.329.0.tar.gz -L https://github.com/actions/runner/releases/download/v2.329.0/actions-runner-linux-x64-2.329.0.tar.gz

# Arxivni ochish
tar xzf ./actions-runner-linux-x64-2.329.0.tar.gz

# Arxivni o'chirish
rm ./actions-runner-linux-x64-2.329.0.tar.gz

# Fayllarni tekshirish
ls -la
```

### Step 3: Ruxsatlarni Sozlash

```bash
# Ruxsatlarni sozlash
chown -R root:root /var/www/building-api/runner
chmod +x /var/www/building-api/runner/config.sh
chmod +x /var/www/building-api/runner/run.sh
chmod +x /var/www/building-api/runner/svc.sh

# Fayllarni tekshirish
ls -la
```

### Step 4: Runner Konfiguratsiyasi

```bash
# Runner ni konfiguratsiya qilish
./config.sh --url https://github.com/a-d-sh/building --token ALLG4AJAAKJ2VNZ2QQISMX3I7HJEC
```

### Step 5: Service O'rnatish

```bash
# Service sifatida o'rnatish
./svc.sh install

# Serviceni ishga tushirish
./svc.sh start
```

## 🚀 To'liq Setup (Qayta)

Agar yuqoridagi qadamlar ishlamasa, to'liq qayta setup:

```bash
# Katalogga o'tish
cd /var/www/building-api/runner

# Barcha fayllarni o'chirish
rm -rf *

# GitHub dan berilgan to'g'ri versiyani yuklab olish
curl -o actions-runner-linux-x64-2.329.0.tar.gz -L https://github.com/actions/runner/releases/download/v2.329.0/actions-runner-linux-x64-2.329.0.tar.gz

# Hash tekshirish (ixtiyoriy)
echo "194f1e1e4bd02f80b7e9633fc546084d8d4e19f3928a324d512ea53430102e1d  actions-runner-linux-x64-2.329.0.tar.gz" | shasum -a 256 -c

# Arxivni ochish
tar xzf ./actions-runner-linux-x64-2.329.0.tar.gz

# Arxivni o'chirish
rm ./actions-runner-linux-x64-2.329.0.tar.gz

# Fayllarni tekshirish
ls -la

# Ruxsatlarni sozlash
chown -R root:root /var/www/building-api/runner
chmod +x /var/www/building-api/runner/config.sh
chmod +x /var/www/building-api/runner/run.sh
chmod +x /var/www/building-api/runner/svc.sh

# Konfiguratsiya
./config.sh --url https://github.com/a-d-sh/building --token ALLG4AJAAKJ2VNZ2QQISMX3I7HJEC

# Service o'rnatish
./svc.sh install

# Service ishga tushirish
./svc.sh start
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

### GitHub da Tekshirish

1. **GitHub** → https://github.com/a-d-sh/building/settings/actions/runners
2. **"building-api"** runner ko'rinishi kerak
3. Status: **"Online"** bo'lishi kerak

## 🛠️ Troubleshooting

### Issue: svc.sh fayli yo'q

```bash
# Fayllarni tekshirish
ls -la

# Agar svc.sh yo'q bo'lsa, qayta yuklab olish
rm -rf *
curl -o actions-runner-linux-x64-2.329.0.tar.gz -L https://github.com/actions/runner/releases/download/v2.329.0/actions-runner-linux-x64-2.329.0.tar.gz
tar xzf ./actions-runner-linux-x64-2.329.0.tar.gz
rm ./actions-runner-linux-x64-2.329.0.tar.gz
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
./config.sh remove
./config.sh --url https://github.com/a-d-sh/building --token NEW_TOKEN
```

## 🎯 Keyingi Qadamlar

Runner muvaffaqiyatli sozlangandan keyin:

1. **Building API kodini yuklash**
2. **Environment sozlash**
3. **Docker deployment**
4. **GitHub Actions test**

---

**Building API runner setup davom etmoqda!** 🚀

**Hozirgi holat**: Runner fayllari yuklab olindi, konfiguratsiya qilish kerak
