# 🔧 Serverda Deploy User ga Sudo Ruxsati Berish

## 📋 Muammo

Deploy workflow da `sudo` komandasi ishlamaydi:
```
sudo: a terminal is required to read the password; either use the -S option to read from standard input or configure an askpass helper
```

## 🔧 Yechim 1: Deploy User ga Sudo Ruxsati Berish

Serverda quyidagi komandalarni bajaring:

```bash
# Root user sifatida
sudo visudo

# Yoki faylga qo'shish
echo "deploy ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

# Yoki sudoers.d fayl yaratish
echo "deploy ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/deploy
chmod 440 /etc/sudoers.d/deploy
```

## 🔧 Yechim 2: Workflow ni Tuzatish (Tavsiya)

Deploy workflow da sudo o'rniga boshqa yechim:

```yaml
# Fix git ownership and permissions
echo "🔧 Fixing git ownership and permissions..."
git config --global --add safe.directory /var/www/building-api

# Try to fix permissions without sudo
chmod -R 755 .git 2>/dev/null || echo "⚠️ Could not change git permissions, continuing..."

echo "📥 Pulling latest code..."
git fetch origin main
git reset --hard origin/main
```

## 🔧 Yechim 3: Root User da Ishga Tushirish

Deploy workflow ni root user da ishga tushirish:

```yaml
deploy:
  name: 🚀 Deploy to Production
  runs-on: [self-hosted, Linux, X64]
  needs: test
  timeout-minutes: 10
  
  steps:
    - name: 📥 Pull latest code
      run: |
        cd /var/www/building-api
        
        # Fix git ownership and permissions
        echo "🔧 Fixing git ownership and permissions..."
        git config --global --add safe.directory /var/www/building-api
        
        # Fix git directory permissions (root user)
        chown -R deploy:deploy /var/www/building-api/.git
        chmod -R 755 /var/www/building-api/.git

        echo "📥 Pulling latest code..."
        git fetch origin main
        git reset --hard origin/main
```

## 🚀 Tavsiya: Yechim 1

Serverda deploy user ga sudo ruxsati berish:

```bash
# Root user sifatida
echo "deploy ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/deploy
chmod 440 /etc/sudoers.d/deploy

# Tekshirish
sudo -l -U deploy
```

## ✅ Tekshirish

```bash
# Deploy user ga o'tish
su - deploy

# Sudo test
sudo whoami
# Output: root

# Git test
cd /var/www/building-api
sudo chown -R deploy:deploy .git
sudo chmod -R 755 .git
```

---

**Deploy user ga sudo ruxsati berish yoki workflow ni tuzatish kerak!** 🚀
