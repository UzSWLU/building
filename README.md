# Building API

Building Management Django REST API for managing buildings, rooms, devices, and maintenance requests.

## 🚀 Features

- 🏢 Building and Room Management
- 📱 Device Inventory Management
- 📸 Multi-image Upload Support
- 🔧 Repair Request System
- 📊 Service Logs and History
- 🔐 Secure API with Authentication
- 📚 Auto-generated API Documentation (Swagger UI)
- 🐳 Docker Support
- 🔄 CI/CD Pipeline with GitHub Actions

## 🛠️ Tech Stack

- **Backend**: Django 5.2.7 + Django REST Framework
- **Database**: PostgreSQL 16
- **Web Server**: Nginx
- **Containerization**: Docker & Docker Compose
- **CI/CD**: GitHub Actions
- **Documentation**: Swagger UI (drf-spectacular)

## 📋 API Endpoints

### Buildings

- `GET /api/buildings/` - List all buildings
- `POST /api/buildings/` - Create building
- `GET /api/building-images/` - List building images
- `POST /api/building-images/` - Upload building images

### Rooms

- `GET /api/rooms/` - List all rooms
- `POST /api/rooms/` - Create room
- `GET /api/room-images/` - List room images
- `POST /api/room-images/` - Upload room images

### Devices

- `GET /api/devices/` - List all devices
- `POST /api/devices/` - Create device
- `POST /api/devices/{id}/move/` - Move device to new room
- `POST /api/devices/{id}/change_condition/` - Change device condition

### Repairs & Service Logs

- `GET /api/repair-requests/` - List repair requests
- `POST /api/repair-requests/` - Create repair request
- `GET /api/service-logs/` - List service logs
- `POST /api/service-logs/` - Create service log

## 🚀 Quick Start

### Development Setup

1. **Clone the repository**

   ```bash
   git clone https://github.com/a-d-sh/building.git
   cd building
   ```

2. **Create environment file**

   ```bash
   cp env.prod.example .env.prod
   # Edit .env.prod with your settings
   ```

3. **Run with Docker**

   ```bash
   docker-compose up --build -d
   ```

4. **Access the application**
   - API: http://localhost:5001/
   - Swagger UI: http://localhost:5001/
   - Admin: http://localhost:5001/admin/
   - Health Check: http://localhost:5001/health/

### Production Deployment

1. **Server Setup** (172.22.0.19)

   ```bash
   # Upload deploy.sh to server
   chmod +x deploy.sh
   ./deploy.sh
   ```

2. **Domain Configuration**
   - Domain: `building.swagger.uzswlu.uz`
   - SSL: Auto-generated self-signed certificate
   - Production URL: `https://building.swagger.uzswlu.uz`

## 🔐 Authentication

The API uses Bearer token authentication with external auth service integration:

- **Auth Service**: `https://auth.uzswlu.uz`
- **Token Format**: Bearer token in Authorization header
- **Roles**: Admin, Creator, User

## 🐳 Docker Commands

```bash
# Development
docker-compose up --build -d

# Production
docker-compose -f docker-compose.prod.yml up --build -d

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# View logs
docker-compose logs -f web
```

## 🔄 CI/CD Pipeline

GitHub Actions automatically:

- ✅ Runs tests on every push/PR
- 🚀 Deploys to production on main branch
- 🔧 Builds Docker images
- 📊 Runs database migrations
- 🔍 Performs health checks

## 📊 Monitoring

- **Health Check**: `/health/`
- **Container Logs**: `docker-compose logs -f`
- **System Service**: `systemctl status building-api`

## 🔧 Configuration

### Environment Variables

| Variable               | Description       | Default                    |
| ---------------------- | ----------------- | -------------------------- |
| `DJANGO_SECRET_KEY`    | Django secret key | Required                   |
| `DJANGO_DEBUG`         | Debug mode        | 0                          |
| `DJANGO_ALLOWED_HOSTS` | Allowed hosts     | building.swagger.uzswlu.uz |
| `POSTGRES_DB`          | Database name     | rttm                       |
| `POSTGRES_USER`        | Database user     | rttm                       |
| `POSTGRES_PASSWORD`    | Database password | Required                   |
| `AUTH_BASE_URL`        | Auth service URL  | https://auth.uzswlu.uz     |

## 📝 Default Credentials

- **Admin Username**: `admin`
- **Admin Password**: `admin123`
- **Admin Email**: `admin@uzswlu.uz`

⚠️ **Important**: Change default password in production!

## 🛡️ Security Features

- ✅ CSRF protection
- ✅ Rate limiting
- ✅ Security headers
- ✅ File upload size limits
- ✅ Input validation
- ✅ SQL injection protection
- ✅ SSL/TLS encryption

## 📚 Documentation

- **Swagger UI**: Available at root URL (`/`)
- **API Schema**: `/api/schema/`
- **ReDoc**: `/api/schema/redoc/`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:

- **Issues**: GitHub Issues
- **Documentation**: Swagger UI
- **Health Check**: `/health/` endpoint

---

**Building API** - Professional Django REST API for building management 🚀
