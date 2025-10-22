# Auth Integration Guide

Bu qo'llanma Django RTTM loyihasini Node.js auth tizimi bilan integratsiya qilish uchun yozilgan.

## Qo'shilgan Fayllar

### 1. `app_rttm/auth_service.py`
External auth API bilan ishlash uchun service class.

**Asosiy funksiyalar:**
- `get_current_user_role(access_token)` - User role olish
- `verify_token(access_token)` - Token tekshirish
- `get_user_info(access_token)` - User ma'lumotlari olish
- `has_permission(access_token, required_roles)` - Role tekshirish

### 2. `app_rttm/auth_middleware.py`
Access token ni tekshirish va user ma'lumotlarini request ga qo'shish uchun middleware.

**Asosiy class lar:**
- `AuthMiddleware` - Access token tekshirish
- `RolePermissionMiddleware` - Role asosida permission tekshirish

### 3. `app_rttm/permissions.py`
Custom permission class lar va decorator lar.

**Permission class lar:**
- `AuthPermission` - Asosiy auth permission
- `AdminOnlyPermission` - Faqat admin/creator uchun
- `ReadOnlyPermission` - Faqat o'qish ruxsati

**Decorator lar:**
- `@require_auth_token` - Access token tekshirish
- `@require_admin_role` - Admin/creator role tekshirish

## Sozlamalar

### Settings.py da qo'shilgan sozlamalar:

```python
# Auth settings
AUTH_BASE_URL = 'https://auth.uzswlu.uz'
AUTH_TIMEOUT = 10
AUTH_CACHE_TIMEOUT = 300  # 5 minut

# Cache settings
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# Middleware
MIDDLEWARE = [
    # ... boshqa middleware lar
    'app_rttm.auth_middleware.AuthMiddleware',
    'app_rttm.auth_middleware.RolePermissionMiddleware',
    'app_rttm.middleware.CurrentUserMiddleware',
]
```

## Foydalanish

### 1. Access Token Yuborish

**Header orqali:**
```bash
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
     http://localhost:8000/api/buildings/
```

**Query parameter orqali:**
```bash
curl "http://localhost:8000/api/buildings/?access_token=YOUR_ACCESS_TOKEN"
```

**POST data orqali:**
```json
{
    "access_token": "YOUR_ACCESS_TOKEN",
    "name": "Yangi bino"
}
```

### 2. Role Tizimi

**Admin/Creator role:**
- Barcha endpoint larga to'liq ruxsat
- CRUD operatsiyalar (Create, Read, Update, Delete)

**User role:**
- Faqat o'qish ruxsati (GET, HEAD, OPTIONS)
- POST, PUT, DELETE operatsiyalar uchun 403 Forbidden

### 3. Endpoint Lar

**Barcha endpoint lar auth talab qiladi:**
- `/api/buildings/` - Binolar
- `/api/rooms/` - Xonalar
- `/api/devices/` - Qurilmalar
- `/api/categories/` - Kategoriyalar
- `/api/device-types/` - Qurilma turlari
- `/api/repair-requests/` - Ta'mir so'rovlari
- `/api/service-logs/` - Xizmat loglari

**Health check (auth talab qilmaydi):**
- `/api/health/` - Tizim holati

### 4. Xatolik Kodlari

**401 Unauthorized:**
```json
{
    "error": "Access token required",
    "message": "Authorization header yoki access_token parameter kerak"
}
```

**403 Forbidden:**
```json
{
    "error": "Permission denied",
    "message": "Sizda admin yoki creator ruxsati kerak"
}
```

## Test Qilish

### 1. Health Check
```bash
curl http://localhost:8000/api/health/
```

### 2. Auth Token Bilan Test
```bash
# Token bilan so'rov
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://localhost:8000/api/buildings/

# Token siz so'rov (401 xatolik)
curl http://localhost:8000/api/buildings/
```

### 3. Role Test
```bash
# Admin/Creator token bilan (muvaffaqiyatli)
curl -H "Authorization: Bearer ADMIN_TOKEN" \
     -X POST \
     -H "Content-Type: application/json" \
     -d '{"name": "Test bino"}' \
     http://localhost:8000/api/buildings/

# User token bilan (403 xatolik)
curl -H "Authorization: Bearer USER_TOKEN" \
     -X POST \
     -H "Content-Type: application/json" \
     -d '{"name": "Test bino"}' \
     http://localhost:8000/api/buildings/
```

## Muhim Eslatmalar

1. **Cache:** Auth ma'lumotlari 5 minut cache da saqlanadi
2. **Timeout:** Auth API ga so'rov 10 soniyada timeout bo'ladi
3. **Role:** `creator` va `creater` ikkalasini ham qo'llab-quvvatlaydi
4. **Middleware:** Auth middleware barcha API endpoint larini tekshiradi
5. **Health Check:** `/api/health/` endpoint auth talab qilmaydi

## Troubleshooting

### 1. Auth API ga Ulanish Muammosi
```python
# settings.py da timeout oshirish
AUTH_TIMEOUT = 30
```

### 2. Cache Muammosi
```python
# settings.py da cache timeout oshirish
AUTH_CACHE_TIMEOUT = 600  # 10 minut
```

### 3. Role Tekshirish Muammosi
```python
# permissions.py da role lar ro'yxatini tekshirish
allowed_roles = ['admin', 'creator', 'creater']
```

## Production Sozlamalari

### 1. Environment Variables
```bash
export AUTH_BASE_URL="https://auth.uzswlu.uz"
export AUTH_TIMEOUT="10"
export AUTH_CACHE_TIMEOUT="300"
```

### 2. Redis Cache (Production uchun)
```python
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}
```

### 3. Logging
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'auth.log',
        },
    },
    'loggers': {
        'app_rttm.auth_service': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```
