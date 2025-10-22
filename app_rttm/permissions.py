import logging
from rest_framework import permissions
from functools import wraps
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)


class AuthPermission(permissions.BasePermission):
    """
    Asosiy auth permission - middleware tomonidan o'rnatilgan ma'lumotlarni tekshiradi
    """

    def has_permission(self, request, view):
        """
        Middleware tomonidan autentifikatsiya qilinganligini tekshirish
        """
        # Middleware allaqachon auth tekshirgan va request ga ma'lumot qo'ygan
        if hasattr(request, 'auth_user_id') and hasattr(request, 'auth_role'):
            logger.info(f"AuthPermission: User {request.auth_username} authenticated with role {request.auth_role}")
            return True

        logger.warning("AuthPermission: No auth data found in request")
        return False


class SmartPermission(permissions.BasePermission):
    """
    Smart permission - role asosida CRUD ruxsatlarini boshqaradi
    - Admin/Creator: Full access (CRUD)
    - User: Read-only (GET, HEAD, OPTIONS)
    """

    def has_permission(self, request, view):
        """
        Request method va user role asosida ruxsat berish
        """
        # Auth tekshiruv
        if not hasattr(request, 'auth_role'):
            logger.warning("SmartPermission: No auth_role in request")
            return False

        user_role = request.auth_role
        method = request.method

        # Admin va creator - full access
        if user_role in ['admin', 'creator', 'creater']:
            logger.info(f"SmartPermission: {request.auth_username} ({user_role}) - Full access granted for {method}")
            return True

        # User role - faqat o'qish
        if user_role == 'user':
            if method in permissions.SAFE_METHODS:  # GET, HEAD, OPTIONS
                logger.info(f"SmartPermission: {request.auth_username} (user) - Read access granted for {method}")
                return True
            else:
                logger.warning(f"SmartPermission: {request.auth_username} (user) - Write access DENIED for {method}")
                return False

        # Boshqa role'lar - ruxsat yo'q
        logger.warning(f"SmartPermission: {request.auth_username} ({user_role}) - Access DENIED")
        return False


class AdminOnlyPermission(permissions.BasePermission):
    """
    Faqat admin va creator uchun ruxsat
    """

    def has_permission(self, request, view):
        """
        Admin yoki creator ekanligini tekshirish (middleware ma'lumotlaridan)
        """
        # Middleware tomonidan o'rnatilgan role'ni tekshirish
        if not hasattr(request, 'auth_role'):
            logger.warning("AdminOnlyPermission: No auth_role in request")
            return False

        user_role = request.auth_role

        # Admin va creator uchun ruxsat
        if user_role in ['admin', 'creator', 'creater']:
            logger.info(f"AdminOnlyPermission: User {request.auth_username} has admin/creator role")
            return True

        logger.warning(f"AdminOnlyPermission: User {request.auth_username} has insufficient role: {user_role}")
        return False


class ReadOnlyPermission(permissions.BasePermission):
    """
    Faqat o'qish ruxsati
    """

    def has_permission(self, request, view):
        """
        Faqat GET, HEAD, OPTIONS ruxsat
        """
        # Middleware tomonidan autentifikatsiya tekshirilgan
        if not hasattr(request, 'auth_role'):
            logger.warning("ReadOnlyPermission: No auth_role in request")
            return False

        # Faqat o'qish method lariga ruxsat
        if request.method in permissions.SAFE_METHODS:  # GET, HEAD, OPTIONS
            logger.info(f"ReadOnlyPermission: User {request.auth_username} accessing read-only endpoint")
            return True

        logger.warning(f"ReadOnlyPermission: User {request.auth_username} tried unsafe method {request.method}")
        return False


# Decorator lar (eski versiya - compatibility uchun qoldirilgan)
def require_auth_token(view_func):
    """
    View function uchun auth token tekshirish decorator
    ESLATMA: Middleware ishlatilganda bu kerak emas
    """

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not hasattr(request, 'auth_user_id'):
            return Response({
                'error': 'Authentication required',
                'message': 'Middleware auth data not found'
            }, status=status.HTTP_401_UNAUTHORIZED)
        return view_func(request, *args, **kwargs)

    return wrapper


def require_admin_role(view_func):
    """
    Admin/Creator role tekshirish decorator
    ESLATMA: Middleware ishlatilganda bu kerak emas
    """

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not hasattr(request, 'auth_role'):
            return Response({
                'error': 'Authentication required',
                'message': 'Middleware auth data not found'
            }, status=status.HTTP_401_UNAUTHORIZED)

        if request.auth_role not in ['admin', 'creator', 'creater']:
            return Response({
                'error': 'Permission denied',
                'message': f'Admin yoki creator ruxsati kerak. Sizning role: {request.auth_role}'
            }, status=status.HTTP_403_FORBIDDEN)

        return view_func(request, *args, **kwargs)

    return wrapper