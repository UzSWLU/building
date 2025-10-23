# 🚀 Building API - GitHub CI/CD Setup Guide

## 📋 Prerequisites

- GitHub account
- Server access (172.22.0.19)
- Git installed locally

## 🔧 Step 1: Create GitHub Repository

1. **Go to GitHub** and create a new repository:
   - Repository name: `building-api`
   - Description: `Django REST API for Building Management`
   - Visibility: Private (recommended)
   - Initialize with README: No

2. **Copy the repository URL** (you'll need it later)

## 📤 Step 2: Upload Code to GitHub

### Option A: Using Git Commands

```bash
# Navigate to building directory
cd building

# Initialize git repository
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: Building API with CI/CD"

# Add remote origin
git remote add origin https://github.com/YOUR_USERNAME/building-api.git

# Push to GitHub
git push -u origin main
```

### Option B: Using GitHub Desktop

1. Open GitHub Desktop
2. File → Add Local Repository
3. Choose the `building` folder
4. Publish repository to GitHub

## ⚙️ Step 3: Configure GitHub Actions

The following workflow files are already created:

- `.github/workflows/ci.yml` - Continuous Integration
- `.github/workflows/deploy.yml` - Continuous Deployment
- `.github/workflows/check-errors.yml` - Error Monitoring
- `.github/workflows/full-reset.yml` - Full Reset

## 🖥️ Step 4: Setup Self-Hosted Runner

### On Your Server (172.22.0.19):

```bash
# SSH to server
ssh root@172.22.0.19

# Run server setup script
curl -fsSL https://raw.githubusercontent.com/YOUR_USERNAME/building-api/main/scripts/server-setup.sh | bash

# Or download and run manually
wget https://raw.githubusercontent.com/YOUR_USERNAME/building-api/main/scripts/server-setup.sh
chmod +x server-setup.sh
./server-setup.sh
```

### Configure GitHub Actions Runner:

1. **Go to GitHub Repository Settings**
   - Settings → Actions → Runners
   - Click "New self-hosted runner"

2. **Copy the setup commands** and run on server:

```bash
# Create actions-runner directory
mkdir -p /opt/actions-runner
cd /opt/actions-runner

# Download runner
curl -o actions-runner-linux-x64-2.311.0.tar.gz -L https://github.com/actions/runner/releases/download/v2.311.0/actions-runner-linux-x64-2.311.0.tar.gz
tar xzf ./actions-runner-linux-x64-2.311.0.tar.gz

# Configure runner (replace YOUR_TOKEN with actual token)
./config.sh --url https://github.com/YOUR_USERNAME/building-api --token YOUR_TOKEN

# Install as service
sudo ./svc.sh install
sudo ./svc.sh start
```

## 🚀 Step 5: Deploy to Production

### Automatic Deployment (Recommended):

```bash
# Push to main branch triggers automatic deployment
git push origin main
```

### Manual Deployment:

1. **Go to GitHub Actions**
   - Actions → "Deploy to Production"
   - Click "Run workflow"
   - Select environment: production
   - Click "Run workflow"

### Server Deployment:

```bash
# SSH to server
ssh root@172.22.0.19

# Navigate to deployment directory
cd /var/www/building-api

# Clone repository
git clone https://github.com/YOUR_USERNAME/building-api.git .

# Run deployment script
chmod +x deploy.sh
./deploy.sh production latest
```

## 🔐 Step 6: Configure Domain and SSL

### DNS Configuration:

Add A record in your DNS:
```
Type: A
Name: building.swagger
Domain: uzswlu.uz
Value: 172.22.0.19
TTL: 3600
```

### SSL Certificate (Let's Encrypt):

```bash
# On server
certbot --nginx -d building.swagger.uzswlu.uz
```

## 📊 Step 7: Verify Deployment

### Check Services:

```bash
# Container status
docker-compose -f /var/www/building-api/docker-compose.prod.yml ps

# Application logs
docker-compose -f /var/www/building-api/docker-compose.prod.yml logs -f web

# Health check
curl https://building.swagger.uzswlu.uz/health/
```

### Access Points:

- **API**: https://building.swagger.uzswlu.uz/
- **Swagger UI**: https://building.swagger.uzswlu.uz/
- **Health Check**: https://building.swagger.uzswlu.uz/health/
- **Admin**: https://building.swagger.uzswlu.uz/admin/

### Default Credentials:

- **Username**: admin
- **Password**: admin123
- **Email**: admin@uzswlu.uz

## 🔄 Step 8: CI/CD Workflow

### Automatic Triggers:

1. **Push to main** → Automatic deployment
2. **Every 6 hours** → Error monitoring
3. **Manual trigger** → Full reset (with confirmation)

### Manual Actions:

1. **Check Errors**: Actions → "Check Building API Errors" → Run workflow
2. **Full Reset**: Actions → "Full Building API Reset" → Run workflow (type "RESET")
3. **Deploy**: Actions → "Deploy to Production" → Run workflow

## 📝 Step 9: Monitoring and Maintenance

### Logs:

```bash
# Application logs
docker-compose -f /var/www/building-api/docker-compose.prod.yml logs -f web

# System logs
tail -f /var/log/building-api/monitor.log

# Nginx logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

### Backups:

```bash
# Manual backup
/usr/local/bin/building-api-backup.sh

# List backups
ls -la /var/www/backups/building-api/
```

### Updates:

```bash
# Pull latest changes
cd /var/www/building-api
git pull origin main

# Redeploy
./deploy.sh production latest
```

## 🛠️ Troubleshooting

### Common Issues:

1. **Container not starting**:
   ```bash
   docker-compose -f /var/www/building-api/docker-compose.prod.yml logs web
   ```

2. **Database connection failed**:
   ```bash
   docker-compose -f /var/www/building-api/docker-compose.prod.yml exec db psql -U building -d building
   ```

3. **Nginx not serving**:
   ```bash
   systemctl status nginx
   nginx -t
   ```

4. **SSL certificate issues**:
   ```bash
   certbot certificates
   certbot renew --dry-run
   ```

### Reset Everything:

```bash
# Full reset via GitHub Actions
# Go to Actions → "Full Building API Reset" → Run workflow → Type "RESET"

# Or manual reset
cd /var/www/building-api
docker-compose -f docker-compose.prod.yml down -v
docker system prune -af
./deploy.sh production latest
```

## ✅ Success Checklist

- [ ] GitHub repository created
- [ ] Code uploaded to GitHub
- [ ] Server setup script run
- [ ] GitHub Actions runner configured
- [ ] First deployment successful
- [ ] Domain configured (building.swagger.uzswlu.uz)
- [ ] SSL certificate installed
- [ ] Health check passing
- [ ] Swagger UI accessible
- [ ] Admin panel accessible
- [ ] CI/CD pipeline working
- [ ] Monitoring configured
- [ ] Backups working

## 🎉 Congratulations!

Your Building API is now:
- ✅ Deployed to production
- ✅ Automated CI/CD pipeline
- ✅ Monitored and backed up
- ✅ SSL secured
- ✅ Domain configured

**Ready for production use!** 🚀

---

## 📞 Support

For issues or questions:
- GitHub Issues: https://github.com/YOUR_USERNAME/building-api/issues
- Server Logs: `/var/log/building-api/`
- Health Check: https://building.swagger.uzswlu.uz/health/
