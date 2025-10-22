"""
Advanced permission class lar - keyingi qadamlar uchun
"""

import logging
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework import status
from .auth_service import auth_service
from .role_permissions import check_endpoint_permission, get_allowed_methods

logger = logging.getLogger(__name__)

class AdvancedAuthPermission(permissions.BasePermission):
    """
    Advanced permission class - role va endpoint asosida tekshirish
    """
    
    def has_permission(self, request, view):
        """
        Request da permission borligini tekshirish
        """
        # Access token ni olish
        access_token = self._get_access_token(request)
        
        if not access_token:
            logger.warning(f"Access token topilmadi: {request.path}")
            return False
        
        # Token ni tekshirish
        if not auth_service.verify_token(access_token):
            logger.warning(f"Invalid access token: {request.path}")
            return False
        
        # User role ni olish
        user_role_data = auth_service.get_current_user_role(access_token)
        if not user_role_data:
            logger.warning(f"User role olinmadi: {request.path}")
            return False
        
        user_role = user_role_data.get('role', '').lower()
        request.auth_role = user_role
        request.auth_user_data = user_role_data
        
        # Endpoint va method uchun ruxsat tekshirish
        endpoint = request.path
        method = request.method
        
        # Endpoint ruxsatini tekshirish
        if not check_endpoint_permission(user_role, endpoint, method):
            logger.warning(f"Endpoint ruxsati yo'q: {user_role} - {endpoint} - {method}")
            return False
        
        # Method ruxsatini tekshirish
        allowed_methods = get_allowed_methods(user_role)
        if method not in allowed_methods:
            logger.warning(f"Method ruxsati yo'q: {user_role} - {method}")
            return False
        
        logger.info(f"Permission granted: {user_role} - {endpoint} - {method}")
        return True
    
    def _get_access_token(self, request):
        """
        Access token ni olish
        """
        # Authorization header dan olish
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Bearer '):
            return auth_header[7:]
        
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


class ManagerOnlyPermission(permissions.BasePermission):
    """
    Faqat manager va yuqori role lar uchun
    """
    
    def has_permission(self, request, view):
        access_token = self._get_access_token(request)
        
        if not access_token:
            return False
        
        if not auth_service.verify_token(access_token):
            return False
        
        user_role_data = auth_service.get_current_user_role(access_token)
        if not user_role_data:
            return False
        
        user_role = user_role_data.get('role', '').lower()
        
        # Manager va yuqori role lar uchun ruxsat
        if user_role in ['admin', 'creator', 'creater', 'manager']:
            request.auth_role = user_role
            request.auth_user_data = user_role_data
            return True
        
        return False
    
    def _get_access_token(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Bearer '):
            return auth_header[7:]
        
        access_token = request.GET.get('access_token')
        if access_token:
            return access_token
        
        if hasattr(request, 'data') and isinstance(request.data, dict):
            access_token = request.data.get('access_token')
            if access_token:
                return access_token
        
        return None


class TechnicianOnlyPermission(permissions.BasePermission):
    """
    Faqat technician va yuqori role lar uchun
    """
    
    def has_permission(self, request, view):
        access_token = self._get_access_token(request)
        
        if not access_token:
            return False
        
        if not auth_service.verify_token(access_token):
            return False
        
        user_role_data = auth_service.get_current_user_role(access_token)
        if not user_role_data:
            return False
        
        user_role = user_role_data.get('role', '').lower()
        
        # Technician va yuqori role lar uchun ruxsat
        if user_role in ['admin', 'creator', 'creater', 'manager', 'technician']:
            request.auth_role = user_role
            request.auth_user_data = user_role_data
            return True
        
        return False
    
    def _get_access_token(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Bearer '):
            return auth_header[7:]
        
        access_token = request.GET.get('access_token')
        if access_token:
            return access_token
        
        if hasattr(request, 'data') and isinstance(request.data, dict):
            access_token = request.data.get('access_token')
            if access_token:
                return access_token
        
        return None
