# RTTM Django API

Real-Time Technology Management (RTTM) Django REST API for managing buildings, rooms, devices, and maintenance requests.

## Features

- 🏢 Building and Room Management
- 📱 Device Inventory Management
- 📸 Multi-image Upload Support
- 🔧 Repair Request System
- 📊 Service Logs and History
- 🔐 Secure API with Authentication
- 📚 Auto-generated API Documentation

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Git

### Development Setup

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd Jahon_tillari_rttm
   ```

2. **Create environment file**
   ```bash
   cp env.prod.example .env.prod
   # Edit .env.prod with your settings
   ```

3. **Run the application**
   ```bash
   ./deploy.sh
   ```

4. **Access the application**
   - API: http://localhost/api/
   - Admin: http://localhost/admin/
   - API Docs: http://localhost/api/schema/swagger-ui/

### Production Deployment

1. **Configure environment**
   ```bash
   cp env.prod.example .env.prod
   # Update .env.prod with production values
   ```

2. **Deploy**
   ```bash
   ./deploy.sh production
   ```

3. **SSL Setup (Optional)**
   - Place SSL certificates in `ssl/` directory
   - Uncomment HTTPS configuration in `nginx/conf.d/default.conf`
   - Update `CSRF_TRUSTED_ORIGINS` in settings

## API Endpoints

### Buildings
- `GET /api/buildings/` - List all buildings
- `POST /api/buildings/` - Create building
- `GET /api/building-images/` - List building images
- `POST /api/building-images/` - Upload building images (multiple files supported)

### Rooms
- `GET /api/rooms/` - List all rooms
- `POST /api/rooms/` - Create room
- `GET /api/room-images/` - List room images
- `POST /api/room-images/` - Upload room images (multiple files supported)

### Devices
- `GET /api/devices/` - List all devices
- `POST /api/devices/` - Create device
- `GET /api/device-images/` - List device images
- `POST /api/device-images/` - Upload device images (multiple files supported)
- `POST /api/devices/{id}/move/` - Move device to new room
- `POST /api/devices/{id}/change_condition/` - Change device condition

### Repairs
- `GET /api/repair-requests/` - List repair requests
- `POST /api/repair-requests/` - Create repair request

### Service Logs
- `GET /api/service-logs/` - List service logs
- `POST /api/service-logs/` - Create service log

## Image Upload

The API supports multiple image uploads for buildings, rooms, and devices:

### Single Image Upload
```bash
curl -X POST http://localhost/api/building-images/ \
  -H "Authorization: Basic <base64-encoded-credentials>" \
  -F "building=1" \
  -F "image=@image.jpg" \
  -F "is_main=true" \
  -F "title=Main Building Photo"
```

### Multiple Images Upload
```bash
curl -X POST http://localhost/api/building-images/ \
  -H "Authorization: Basic <base64-encoded-credentials>" \
  -F "building=1" \
  -F "images=@image1.jpg" \
  -F "images=@image2.jpg" \
  -F "images=@image3.jpg" \
  -F "is_main=false" \
  -F "title=Building Gallery"
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DJANGO_SECRET_KEY` | Django secret key | Required |
| `DJANGO_DEBUG` | Debug mode | 0 |
| `DJANGO_ALLOWED_HOSTS` | Allowed hosts | localhost,127.0.0.1 |
| `POSTGRES_DB` | Database name | rttm |
| `POSTGRES_USER` | Database user | rttm |
| `POSTGRES_PASSWORD` | Database password | Required |
| `POSTGRES_HOST` | Database host | db |
| `POSTGRES_PORT` | Database port | 5432 |

## Security Features

- ✅ CSRF protection disabled for API (Basic Auth)
- ✅ Rate limiting on API endpoints
- ✅ Security headers (XSS, CSRF, etc.)
- ✅ File upload size limits
- ✅ Input validation and sanitization
- ✅ SQL injection protection
- ✅ Secure session management

## Monitoring

- Health check endpoint: `/health/`
- Application logs: `docker-compose logs -f web`
- Nginx logs: `docker-compose logs -f nginx`
- Database logs: `docker-compose logs -f db`

## Troubleshooting

### Common Issues

1. **Permission denied on deploy.sh**
   ```bash
   chmod +x deploy.sh
   ```

2. **Database connection failed**
   - Check PostgreSQL container is running
   - Verify database credentials in `.env.prod`

3. **Static files not loading**
   - Run: `docker-compose exec web python manage.py collectstatic --noinput`

4. **CSRF token missing**
   - Use Basic Authentication header
   - Check `CSRF_TRUSTED_ORIGINS` in settings

### Useful Commands

```bash
# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Access Django shell
docker-compose -f docker-compose.prod.yml exec web python manage.py shell

# Create superuser
docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser

# Run migrations
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate

# Stop services
docker-compose -f docker-compose.prod.yml down

# Rebuild and restart
docker-compose -f docker-compose.prod.yml up --build -d
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.
