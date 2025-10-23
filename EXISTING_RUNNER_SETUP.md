# 🔄 Serverda Mavjud Runner Holati

## 📋 Mavjud Runner Ma'lumotlari

Serverda allaqachon **auth-api** uchun actions-runner ishlayapti:

- **Auth API Runner**: `/var/www/auth-api/` da ishlaydi
- **Building API**: Yangi runner kerak yoki mavjud runner ni ishlatish

## 🔧 Variant 1: Alohida Runner (Tavsiya etiladi)

### Building API uchun yangi runner yaratish:

```bash
# Serverga ulanish
ssh root@172.22.0.19
# Password: Rm09HVd_XhXHa

# Building API uchun alohida runner katalogi
mkdir -p /var/www/building-api/runner
cd /var/www/building-api/runner

# Runner fayllarini yuklab olish
curl -o actions-runner-linux-x64-2.329.0.tar.gz -L https://github.com/actions/runner/releases/download/v2.329.0/actions-runner-linux-x64-2.329.0.tar.gz

# Arxivni ochish
tar xzf ./actions-runner-linux-x64-2.329.0.tar.gz
rm ./actions-runner-linux-x64-2.329.0.tar.gz

# Ruxsatlar
chown -R root:root /var/www/building-api/runner
chmod +x /var/www/building-api/runner/config.sh
chmod +x /var/www/building-api/runner/run.sh
chmod +x /var/www/building-api/runner/svc.sh

# Konfiguratsiya
./config.sh --url https://github.com/a-d-sh/building --token ALLG4AJAAKJ2VNZ2QQISMX3I7HJEC

# Service sifatida o'rnatish
./svc.sh install
./svc.sh start
```

## 🔧 Variant 2: Mavjud Runner ni Ishlatish

### Auth API runner ni building-api uchun ham ishlatish:

```bash
# Mavjud runner holatini tekshirish
systemctl status actions.runner.auth-api

# Mavjud runner katalogini ko'rish
ls -la /var/www/auth-api/

# Building API uchun kodni yuklash
mkdir -p /var/www/building-api
cd /var/www/building-api
git clone https://github.com/a-d-sh/building.git .

# Environment sozlash
cp env.prod.example .env.production
nano .env.production

# Deployment
chmod +x deploy.sh
./deploy.sh production latest
```

## 🔧 Variant 3: Mavjud Runner ni Yangilash

### Auth API runner ni yangilab, ikkala loyiha uchun ishlatish:

```bash
# Mavjud runner ni to'xtatish
systemctl stop actions.runner.auth-api

# Runner ni qayta konfiguratsiya qilish
cd /var/www/auth-api
./config.sh remove

# Yangi konfiguratsiya (ikkala repository uchun)
./config.sh --url https://github.com/a-d-sh/auth-api --token AUTH_TOKEN
./config.sh --url https://github.com/a-d-sh/building --token ALLG4AJAAKJ2VNZ2QQISMX3I7HJEC

# Serviceni qayta ishga tushirish
./svc.sh start
```

## 📊 Mavjud Runnerlarni Tekshirish

```bash
# Barcha runner servicelarni ko'rish
systemctl list-units --type=service | grep actions.runner

# Auth API runner status
systemctl status actions.runner.auth-api

# Auth API runner loglar
journalctl -u actions.runner.auth-api -f

# Auth API runner katalogi
ls -la /var/www/auth-api/
```

## 🚀 Tavsiya: Alohida Runner

**Tavsiya etiladi**: Building API uchun alohida runner yaratish, chunki:

1. **Xavfsizlik**: Har bir loyiha alohida runner ishlatadi
2. **Monitoring**: Har bir loyiha uchun alohida monitoring
3. **Performance**: Bir loyiha boshqasiga ta'sir qilmaydi
4. **Maintenance**: Har bir loyihani mustaqil boshqarish

## 🔧 To'liq Setup (Alohida Runner)

### Step 1: Serverga Ulanish

```bash
ssh root@172.22.0.19
# Password: Rm09HVd_XhXHa
```

### Step 2: Mavjud Runnerlarni Tekshirish

```bash
# Mavjud runnerlarni ko'rish
ls -la /var/www/

# Auth API runner
ls -la /var/www/auth-api/

# Building API uchun yangi katalog
mkdir -p /var/www/building-api/runner
```

### Step 3: Building API Runner O'rnatish

```bash
cd /var/www/building-api/runner

# Runner fayllarini yuklab olish
curl -o actions-runner-linux-x64-2.329.0.tar.gz -L https://github.com/actions/runner/releases/download/v2.329.0/actions-runner-linux-x64-2.329.0.tar.gz

# Arxivni ochish
tar xzf ./actions-runner-linux-x64-2.329.0.tar.gz
rm ./actions-runner-linux-x64-2.329.0.tar.gz

# Ruxsatlar
chown -R root:root /var/www/building-api/runner
chmod +x /var/www/building-api/runner/config.sh
chmod +x /var/www/building-api/runner/run.sh
chmod +x /var/www/building-api/runner/svc.sh
```

### Step 4: Runner Konfiguratsiyasi

```bash
# Runner ni konfiguratsiya qilish
./config.sh --url https://github.com/a-d-sh/building --token ALLG4AJAAKJ2VNZ2QQISMX3I7HJEC

# Service sifatida o'rnatish
./svc.sh install

# Serviceni ishga tushirish
./svc.sh start
```

### Step 5: Building API Deployment

```bash
# Kodni yuklash
mkdir -p /var/www/building-api
cd /var/www/building-api
git clone https://github.com/a-d-sh/building.git .

# Environment sozlash
cp env.prod.example .env.production
nano .env.production

# Deployment
chmod +x deploy.sh
./deploy.sh production latest
```

## ✅ Tekshirish

### Ikkala Runner Status

```bash
# Auth API runner
systemctl status actions.runner.auth-api

# Building API runner
systemctl status actions.runner.building-api

# Barcha runner servicelar
systemctl list-units --type=service | grep actions.runner
```

### GitHub da Tekshirish

1. **Auth API**: https://github.com/a-d-sh/auth-api/settings/actions/runners
2. **Building API**: https://github.com/a-d-sh/building/settings/actions/runners

## 🎯 Success Checklist

- [ ] Serverga SSH orqali ulanish
- [ ] Mavjud auth-api runner tekshirilgan
- [ ] Building API uchun alohida runner katalogi yaratilgan
- [ ] Building API runner fayllari yuklab olingan
- [ ] Building API runner konfiguratsiya qilingan
- [ ] Building API runner service ishga tushirilgan
- [ ] GitHub da ikkala runner "Online" ko'rinadi
- [ ] Building API kod yuklangan
- [ ] Building API environment sozlangan
- [ ] Building API Docker containerlar ishlaydi
- [ ] Building API endpoints ishlaydi

---

**Building API uchun alohida runner setup endi tayyor!** 🚀

**Server**: 172.22.0.19  
**Username**: root  
**Password**: Rm09HVd_XhXHa  
**Auth API Runner**: `/var/www/auth-api/`  
**Building API Runner**: `/var/www/building-api/runner/`
