#!/bin/bash

# Building API Server Setup Script
# This script prepares the server for Building API deployment

set -e

echo "🚀 =============================================="
echo "🚀 BUILDING API SERVER SETUP"
echo "🚀 =============================================="

# Update system packages
echo "📦 Updating system packages..."
apt-get update
apt-get upgrade -y

# Install required packages
echo "📦 Installing required packages..."
apt-get install -y \
    curl \
    wget \
    git \
    nginx \
    certbot \
    python3-certbot-nginx \
    ufw \
    htop \
    nano \
    unzip

# Install Docker
echo "🐳 Installing Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    
    # Add current user to docker group
    usermod -aG docker $USER
    
    echo "✅ Docker installed successfully"
else
    echo "✅ Docker already installed"
fi

# Install Docker Compose
echo "🐳 Installing Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    
    echo "✅ Docker Compose installed successfully"
else
    echo "✅ Docker Compose already installed"
fi

# Create deployment directory
echo "📁 Creating deployment directory..."
mkdir -p /var/www/building-api
mkdir -p /var/www/backups/building-api
mkdir -p /var/log/building-api

# Set proper permissions
chown -R www-data:www-data /var/www/building-api
chown -R www-data:www-data /var/www/backups/building-api
chown -R www-data:www-data /var/log/building-api

# Configure firewall
echo "🔥 Configuring firewall..."
ufw --force enable
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 5001/tcp  # Building API port
ufw allow 5443/tcp  # Building API HTTPS port

# Configure Nginx for api.uzswlu.uz
echo "🌐 Configuring Nginx for api.uzswlu.uz..."
cat > /etc/nginx/sites-available/api.uzswlu.uz << 'EOF'
# HTTP -> HTTPS redirect
server {
    listen 80;
    server_name api.uzswlu.uz;
    
    # Let's Encrypt validation
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }
    
    # Redirect all other requests to HTTPS
    location / {
        return 301 https://$server_name$request_uri;
    }
}

# HTTPS server
server {
    listen 443 ssl http2;
    server_name api.uzswlu.uz;
    
    # SSL Configuration (using existing certificates)
    ssl_certificate /etc/nginx/ssl/STAR25_uzswlu_uz.crt;
    ssl_certificate_key /etc/nginx/ssl/STAR25_uzswlu_uz.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384';
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    ssl_session_tickets off;
    
    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # Client max body size
    client_max_body_size 20M;
    
    # Proxy to building API
    location / {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        
        # Timeouts
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }
    
    # Health check endpoint
    location /health/ {
        proxy_pass http://127.0.0.1:5001;
        access_log off;
    }
    
    # Static files
    location /static/ {
        alias /var/www/building-api/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Media files
    location /media/ {
        alias /var/www/building-api/media/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF

# Enable the site
ln -sf /etc/nginx/sites-available/api.uzswlu.uz /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Create webroot for Let's Encrypt
mkdir -p /var/www/html

echo "✅ Nginx configuration created for api.uzswlu.uz"

# Use existing SSL certificates from /var/www/sertifikat
echo "🔒 Using existing SSL certificates..."
if [ -d "/var/www/sertifikat" ]; then
  echo "✅ SSL certificates directory found: /var/www/sertifikat"
  ls -la /var/www/sertifikat/
else
  echo "⚠️ SSL certificates directory not found: /var/www/sertifikat"
  echo "Please ensure SSL certificates are available in /var/www/sertifikat/"
fi

# Start and enable services
echo "🚀 Starting services..."
systemctl start nginx
systemctl enable nginx
systemctl start docker
systemctl enable docker

# Create systemd service for Building API
echo "⚙️ Creating systemd service..."
cat > /etc/systemd/system/building-api.service << 'EOF'
[Unit]
Description=Building API Docker Compose
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/var/www/building-api
ExecStart=/usr/local/bin/docker-compose -f docker-compose.prod.yml up -d
ExecStop=/usr/local/bin/docker-compose -f docker-compose.prod.yml down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable building-api.service

# Create log rotation configuration
echo "📝 Configuring log rotation..."
cat > /etc/logrotate.d/building-api << 'EOF'
/var/log/building-api/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
    postrotate
        systemctl reload nginx
    endscript
}
EOF

# Create monitoring script
echo "📊 Creating monitoring script..."
cat > /usr/local/bin/building-api-monitor.sh << 'EOF'
#!/bin/bash

# Building API Monitoring Script

LOG_FILE="/var/log/building-api/monitor.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

echo "[$DATE] Starting Building API monitoring..." >> $LOG_FILE

# Check if containers are running
if ! docker-compose -f /var/www/building-api/docker-compose.prod.yml ps | grep -q "Up"; then
    echo "[$DATE] ERROR: Building API containers are not running!" >> $LOG_FILE
    systemctl restart building-api.service
    echo "[$DATE] Restarted Building API service" >> $LOG_FILE
fi

# Check API health
if ! curl -f -s https://building.swagger.uzswlu.uz/health/ > /dev/null; then
    echo "[$DATE] WARNING: Building API health check failed" >> $LOG_FILE
fi

# Check disk space
DISK_USAGE=$(df /var/www/building-api | tail -1 | awk '{print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
    echo "[$DATE] WARNING: Disk usage is ${DISK_USAGE}%" >> $LOG_FILE
fi

echo "[$DATE] Monitoring completed" >> $LOG_FILE
EOF

chmod +x /usr/local/bin/building-api-monitor.sh

# Add monitoring to crontab
echo "⏰ Setting up monitoring cron job..."
(crontab -l 2>/dev/null; echo "*/5 * * * * /usr/local/bin/building-api-monitor.sh") | crontab -

# Create backup script
echo "💾 Creating backup script..."
cat > /usr/local/bin/building-api-backup.sh << 'EOF'
#!/bin/bash

# Building API Backup Script

BACKUP_DIR="/var/www/backups/building-api"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/backup_$DATE.sql"

echo "Creating backup: $BACKUP_FILE"

# Create database backup
cd /var/www/building-api
docker-compose -f docker-compose.prod.yml exec -T db pg_dump -U building building > "$BACKUP_FILE"

# Compress backup
gzip "$BACKUP_FILE"

# Remove backups older than 7 days
find "$BACKUP_DIR" -name "backup_*.sql.gz" -mtime +7 -delete

echo "Backup completed: $BACKUP_FILE.gz"
EOF

chmod +x /usr/local/bin/building-api-backup.sh

# Add backup to crontab (daily at 2 AM)
echo "⏰ Setting up backup cron job..."
(crontab -l 2>/dev/null; echo "0 2 * * * /usr/local/bin/building-api-backup.sh") | crontab -

# Set up GitHub Actions runner for building-api
echo "🤖 Setting up GitHub Actions runner for building-api..."
if [ ! -d "/var/www/building-api/runner" ]; then
    mkdir -p /var/www/building-api/runner
    cd /var/www/building-api/runner
    
    # Download latest runner
    RUNNER_VERSION="2.311.0"
    curl -o actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz -L https://github.com/actions/runner/releases/download/v${RUNNER_VERSION}/actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz
    tar xzf ./actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz
    rm ./actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz
    
    # Set proper permissions
    chown -R root:root /var/www/building-api/runner
    chmod +x /var/www/building-api/runner/config.sh
    chmod +x /var/www/building-api/runner/run.sh
    chmod +x /var/www/building-api/runner/svc.sh
    
    echo "✅ GitHub Actions runner downloaded for building-api"
    echo "⚠️  Manual configuration required:"
    echo "   1. Go to GitHub → Settings → Actions → Runners"
    echo "   2. Click 'New self-hosted runner'"
    echo "   3. Copy the setup commands and run on server:"
    echo "      cd /var/www/building-api/runner"
    echo "      ./config.sh --url https://github.com/a-d-sh/building --token YOUR_TOKEN"
    echo "      ./svc.sh install"
    echo "      ./svc.sh start"
else
    echo "✅ GitHub Actions runner already exists for building-api"
fi

echo ""
echo "✅ =============================================="
echo "✅ SERVER SETUP COMPLETED SUCCESSFULLY!"
echo "✅ =============================================="
echo ""
echo "📋 Next Steps:"
echo "1. Clone your Building API repository to /var/www/building-api"
echo "2. Configure GitHub Actions runner (if using self-hosted)"
echo "3. Run the deployment script: ./deploy.sh"
echo ""
echo "🔗 Services:"
echo "   - Nginx: systemctl status nginx"
echo "   - Docker: systemctl status docker"
echo "   - Building API: systemctl status building-api"
echo ""
echo "📊 Monitoring:"
echo "   - Logs: tail -f /var/log/building-api/monitor.log"
echo "   - Backups: ls -la /var/www/backups/building-api/"
echo ""
echo "🔐 SSL Certificate:"
echo "   - Self-signed certificate generated"
echo "   - For production, use Let's Encrypt:"
echo "     certbot --nginx -d building.swagger.uzswlu.uz"
echo ""
echo "🌐 Domain Configuration:"
echo "   - Add A record: building.swagger.uzswlu.uz -> $(curl -s ifconfig.me)"
echo ""
echo "🎉 Server is ready for Building API deployment!"
