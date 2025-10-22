import threading
import logging
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)

_thread_locals = threading.local()


def get_current_request():
    """
    Joriy request ni olish
    """
    return getattr(_thread_locals, 'request', None)


def get_current_user():
    """
    Joriy foydalanuvchi ma'lumotlarini olish
    Returns: Dict yoki None
    """
    request = get_current_request()
    if request and hasattr(request, 'auth_user_data'):
        return request.auth_user_data
    return None


def get_current_user_id():
    """
    Joriy foydalanuvchi ID'sini olish
    """
    request = get_current_request()
    if request and hasattr(request, 'auth_user_id'):
        return request.auth_user_id
    return None


def get_current_username():
    """
    Joriy foydalanuvchi username'ini olish
    """
    request = get_current_request()
    if request and hasattr(request, 'auth_username'):
        return request.auth_username
    return None


class CurrentUserMiddleware(MiddlewareMixin):
    """
    Request ni thread-local'ga saqlash va audit fields uchun user ma'lumotlarini tayyorlash
    """

    def process_request(self, request):
        """
        Request ni thread-local'ga saqlash
        """
        _thread_locals.request = request
        logger.debug(f"CurrentUserMiddleware: Request saqlandi - {request.path}")

    def process_response(self, request, response):
        """
        Thread-local'ni tozalash
        """
        if hasattr(_thread_locals, 'request'):
            del _thread_locals.request
            logger.debug("CurrentUserMiddleware: Thread-local tozalandi")
        return response

    def process_exception(self, request, exception):
        """
        Exception bo'lganda ham thread-local'ni tozalash
        """
        if hasattr(_thread_locals, 'request'):
            del _thread_locals.request
            logger.debug("CurrentUserMiddleware: Exception - Thread-local tozalandi")
        return None