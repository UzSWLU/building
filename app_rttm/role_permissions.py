"""
Role va permission tizimi - keyingi qadamlar uchun
"""

# Role lar va ularning ruxsatlari
ROLE_PERMISSIONS = {
    'admin': {
        'description': 'Tizim administratori',
        'permissions': ['read', 'write', 'delete', 'manage_users'],
        'endpoints': ['*']  # Barcha endpoint lar
    },
    'creator': {
        'description': 'Kontent yaratuvchi',
        'permissions': ['read', 'write', 'delete'],
        'endpoints': ['*']  # Barcha endpoint lar
    },
    'manager': {
        'description': 'Menejer',
        'permissions': ['read', 'write'],
        'endpoints': [
            '/api/buildings/',
            '/api/rooms/',
            '/api/devices/',
            '/api/categories/',
            '/api/device-types/'
        ]
    },
    'technician': {
        'description': 'Texnik xodim',
        'permissions': ['read', 'write'],
        'endpoints': [
            '/api/devices/',
            '/api/repair-requests/',
            '/api/service-logs/'
        ]
    },
    'viewer': {
        'description': 'Ko\'ruvchi',
        'permissions': ['read'],
        'endpoints': ['*']  # Barcha endpoint larni o'qish
    },
    'user': {
        'description': 'Oddiy foydalanuvchi',
        'permissions': ['read'],
        'endpoints': [
            '/api/buildings/',
            '/api/rooms/',
            '/api/devices/'
        ]
    }
}

def get_role_permissions(role):
    """Role uchun ruxsatlarni olish"""
    return ROLE_PERMISSIONS.get(role, {})

def check_endpoint_permission(role, endpoint, method='GET'):
    """Endpoint uchun ruxsat tekshirish"""
    role_info = get_role_permissions(role)
    if not role_info:
        return False
    
    # Admin va creator uchun barcha ruxsat
    if role in ['admin', 'creator', 'creater']:
        return True
    
    # Endpoint larni tekshirish
    allowed_endpoints = role_info.get('endpoints', [])
    if '*' in allowed_endpoints:
        return True
    
    # Aniq endpoint tekshirish
    for allowed_endpoint in allowed_endpoints:
        if endpoint.startswith(allowed_endpoint):
            return True
    
    return False

def get_allowed_methods(role):
    """Role uchun ruxsatli method larni olish"""
    role_info = get_role_permissions(role)
    permissions = role_info.get('permissions', [])
    
    methods = []
    if 'read' in permissions:
        methods.extend(['GET', 'HEAD', 'OPTIONS'])
    if 'write' in permissions:
        methods.extend(['POST', 'PUT', 'PATCH'])
    if 'delete' in permissions:
        methods.append('DELETE')
    
    return methods
