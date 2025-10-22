import logging
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from .auth_service import auth_service

logger = logging.getLogger(__name__)


class AuthMiddleware(MiddlewareMixin):
    """
    Access token ni tekshirish va user ma'lumotlarini request ga qo'shish
    """

    def process_request(self, request):
        """
        Har bir request da access token ni tekshirish
        """
        # Health check va schema endpoint larni o'tkazib yuborish
        if request.path in ['/health/', '/health', '/api/health/', '/api/health', '/api/schema/',
                            '/api/schema/swagger-ui/', '/api/schema/redoc/']:
            return None

        # Admin endpoint larni o'tkazib yuborish
        if request.path.startswith('/admin/'):
            return None

        # Faqat API endpoint larni tekshirish (schema va health dan tashqari)
        if not request.path.startswith('/api/'):
            return None

        # Access token ni olish
        access_token = self._get_access_token(request)

        if not access_token:
            logger.warning(f"Access token topilmadi: {request.path}")
            return JsonResponse({
                'error': 'Access token required',
                'message': 'Authorization header yoki access_token parameter kerak'
            }, status=401)

        # ✅ Faqat BITTA request - user role olish (token verify ham qiladi)
        user_role_data = auth_service.get_current_user_role(access_token)

        if not user_role_data:
            logger.warning(f"Invalid access token: {request.path}")
            return JsonResponse({
                'error': 'Invalid access token',
                'message': 'Token noto\'g\'ri yoki muddati o\'tgan'
            }, status=401)

        # Request ga ma'lumotlarni qo'shish
        request.auth_user_id = user_role_data.get('userId') or user_role_data.get('id')
        request.auth_username = user_role_data.get('username', 'Unknown')
        request.auth_email = user_role_data.get('email', '')
        request.auth_role = user_role_data.get('role', '').lower()
        request.auth_permissions = user_role_data.get('permissions', [])
        request.access_token = access_token
        request.auth_user_data = user_role_data  # To'liq ma'lumot

        logger.info(f"Auth middleware: User authenticated - {request.auth_username} (Role: {request.auth_role})")
        return None

    def _get_access_token(self, request):
        """
        Access token ni olish - header yoki parameter dan
        """
        # Authorization header dan olish
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Bearer '):
            return auth_header[7:]  # "Bearer " ni olib tashlash

        # Query parameter dan olish
        access_token = request.GET.get('access_token')
        if access_token:
            return access_token

        # POST data dan olish
        if hasattr(request, 'data') and isinstance(request.data, dict):
            access_token = request.data.get('access_token')
            if access_token:
                return access_token

        return None


class RolePermissionMiddleware(MiddlewareMixin):
    """
    Role asosida permission tekshirish
    """

    def process_request(self, request):
        """
        Role permission tekshirish
        """
        # Auth middleware dan keyin ishlaydi
        if not hasattr(request, 'auth_role'):
            return None

        # Admin va creator uchun barcha endpoint lar ochiq
        if request.auth_role in ['admin', 'creator', 'creater']:
            logger.info(f"Admin/Creator user: {request.auth_username} - Full access granted")
            return None

        # Boshqa role lar uchun cheklovlar
        if request.auth_role == 'user':
            # Faqat o'qish ruxsati
            if request.method not in ['GET', 'HEAD', 'OPTIONS']:
                logger.warning(f"User {request.auth_username} tried to {request.method} {request.path}")
                return JsonResponse({
                    'error': 'Permission denied',
                    'message': 'Sizda faqat o\'qish ruxsati bor'
                }, status=403)

        return None